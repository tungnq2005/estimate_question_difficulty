# -*- coding: utf-8 -*-
"""Ba mô hình nền VĂN BẢN cho hệ thống được giải thích.

    QDE_BACKEND=text    PhoBERT đóng băng (768) + 15 cột luật tay   ← mặc định của họ này
    QDE_BACKEND=tfidf   TF-IDF từ + ký tự      + 15 cột luật tay
    QDE_BACKEND=emb     PhoBERT đóng băng (768), KHÔNG cột luật tay

Ba mô hình này cùng với `xgb15` (XGBoost trên đúng 15 cột đó) tạo thành bốn
điểm trên một trục: **bao nhiêu phần quyết định nằm ngoài cột đặt tên được**
— từ ~0 % (xgb15) tới ~100 % (emb). Có bốn điểm thì mới kiểm được giả thuyết
"quy kết mất trung thực khi khối không đặt tên được phình ra", thay vì chỉ có
hai điểm rồi nối bừa một đường. Xem docs/MODEL_UPGRADE.md.

VÌ SAO CÓ FILE NÀY
------------------
Mô hình nền cũ (XGBoost trên 15 cột viết tay) khớp nhãn giáo viên kém xa mức mà
HAI LẦN GÁN NHÃN CỦA NGƯỜI khớp nhau: trên các câu trùng, máy–người chỉ đạt QWK
0,144 (Lý) và 0,007 (Sử) trong khi người–người là 0,391 và 0,355. Giải thích một
mô hình như vậy thì lời giải thích nói về một hệ chưa học được thứ cần học.

Thay biểu diễn đầu vào bằng PhoBERT đóng băng (mean-pool) GIỮ NGUYÊN 15 cột cũ
đưa máy–người lên 0,408 / 0,358 — tức không còn phân biệt được với người chấm
thứ hai. Trên BÀI CHƯA GẶP (chia lát theo trang bài học), QWK đi từ 0,381 →
0,548 (Lý) và 0,135 → 0,364 (Sử).

Giữ đúng 15 cột cũ là cố ý: toàn bộ máy quy trách nhiệm theo cột, định nghĩa
trục BỀ MẶT / TRI THỨC và phép can thiệp không phải viết lại. Bản dùng 52 cột
"sạch" chỉ hơn 0,015 QWK, không đáng đổi.

CÁCH DÙNG
---------
Bật bằng biến môi trường, không sửa code gọi:

    QDE_BACKEND=tfidf python tools/counterfactual_validity.py --subject physics

Khi bật, `counterfactual_validity.Featurizer` gắn thêm cột `__tid__` (số hiệu
văn bản) vào mỗi hàng đặc trưng, và `fit_out_of_fold` trả về mô hình đọc cột đó
để tra vector PhoBERT. Mọi tool phía sau (xai_difficulty, xai_sanity,
natural_raters) dùng lại y nguyên giao diện `model_of[i].predict_proba(df)`.

Vector PhoBERT được cache ra đĩa theo băm SHA-1 của văn bản (`.cache/phobert/`,
đã nằm trong .gitignore) nên chạy lại không phải nhúng lại. Nhúng là tất định.
"""
from __future__ import annotations

import atexit
import hashlib
import os
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

TID_COL = "__tid__"
MODEL_NAME = "vinai/phobert-base"
MAX_LEN = 256
BATCH = 64
# C cố định, chọn theo QWK trên nhãn THẬT một lần (lưới 0,01 / 0,03 / 0,1) rồi
# dùng y hệt cho mọi lần chạy, kể cả mô hình học trên NHÃN XÁO — nếu chọn riêng
# cho từng lần chạy thì mô hình nhãn xáo được ưu ái hơn và phép kiểm tỉnh táo
# mất nghĩa.
C_LR = 0.01
# C của mô hình TF-IDF, chọn MỘT LẦN theo cùng luật với C_LR: lưới
# 1 / 4 / 16 / 64 / 256 trên nhãn THẬT (tools/pick_c_tfidf.py), lấy cực đại
# QWK trung bình hai môn — 0,4478 · 0,4675 · **0,4798** · 0,4715 · 0,4597.
# Cực đại nằm trong lưới, không phải giá trị mép.
C_TFIDF = 16.0
CACHE_DIR = Path(".cache/phobert")

# Chế độ, đọc từ cùng biến môi trường mà counterfactual_validity đọc.
MODE = os.environ.get("QDE_BACKEND", "text")
if MODE not in ("text", "tfidf", "emb"):
    MODE = "text"
USE_EMB = MODE in ("text", "emb")        # có dùng vector PhoBERT không
USE_TFIDF = MODE == "tfidf"
USE_COLS = MODE in ("text", "tfidf")     # có đưa 15 cột luật tay vào mô hình không

_texts: list[str] = []
_index: dict[str, int] = {}
_vec: dict[int, np.ndarray] = {}
# Hàng đợi văn bản CHƯA có vector. Phải có: `_design` gọi `embed_pending` ở mỗi
# lần dự đoán, mà bước kiểm tra chéo dự đoán hàng nghìn lần — quét lại cả danh
# sách mỗi lần thì chính việc quét trở thành nút cổ chai.
_pending: set[int] = set()


def text_of(stem: str, correct: str, distractors) -> str:
    """Câu dẫn + 4 phương án ĐÃ SẮP XẾP theo chữ cái.

    Sắp xếp là cố ý: mô hình không biết phương án nào đúng, nên nó không thể
    lấy 'đâu là đáp án' làm manh mối — và dữ liệu crawl thêm không có đáp án
    vẫn dùng được.
    """
    return stem + " </s> " + " </s> ".join(sorted([correct] + list(distractors)))


def register(text: str) -> int:
    tid = _index.get(text)
    if tid is None:
        tid = len(_texts)
        _index[text] = tid
        _texts.append(text)
        _pending.add(tid)
    return tid


def _key(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


# Cache chia 256 MẢNH theo 2 ký tự đầu của băm. Một file duy nhất sẽ phình tới
# ~900 MB sau loạt kiểm tra tỉnh táo, và bị ghi lại nguyên vẹn sau mỗi lần chạy;
# chia mảnh thì mỗi lần chỉ ghi lại phần đã đụng vào.
_shards: dict[str, dict] = {}
_dirty: set[str] = set()


def _shard_file(sh: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"emb_{sh}.pkl"


def _shard(key: str) -> dict:
    sh = key[:2]
    d = _shards.get(sh)
    if d is None:
        f = _shard_file(sh)
        try:
            with open(f, "rb") as fh:
                d = pickle.load(fh)
        except Exception:
            d = {}
        _shards[sh] = d
    return d


def _flush() -> None:
    # Ghi qua file tạm rồi đổi tên: loạt kiểm tra tỉnh táo chạy nhiều tiến
    # trình song song, cùng ghi một mảnh thì file dễ đứt nửa chừng.
    for sh in sorted(_dirty):
        f = _shard_file(sh)
        tmp = f.with_suffix(f".{os.getpid()}.tmp")
        with open(tmp, "wb") as fh:
            pickle.dump(_shards[sh], fh, protocol=4)
        os.replace(tmp, f)
    _dirty.clear()


_enc = None


def _encoder():
    """Nạp PhoBERT ĐÚNG MỘT LẦN cho cả tiến trình.

    Quan trọng về hiệu năng: đường ống can thiệp gọi dự đoán ngay sau khi dựng
    từng phản thực, nên hàm nhúng bị gọi rất nhiều lần với một văn bản. Nạp lại
    mô hình mỗi lần thì một lần chạy mất hàng giờ thay vì vài phút.
    """
    global _enc
    if _enc is None:
        import torch
        from transformers import AutoModel, AutoTokenizer
        torch.set_num_threads(max(4, torch.get_num_threads()))
        _enc = (AutoTokenizer.from_pretrained(MODEL_NAME),
                AutoModel.from_pretrained(MODEL_NAME).eval())
    return _enc


def embed_pending(verbose: bool = True) -> None:
    """Nhúng mọi văn bản đã đăng ký mà chưa có vector. Dùng cache đĩa trước."""
    if not _pending:
        return
    miss = []
    for tid in sorted(_pending):
        k = _key(_texts[tid])
        v = _shard(k).get(k)
        if v is None:
            miss.append(tid)
        else:
            _vec[tid] = v
    _pending.clear()
    if not miss:
        return

    import torch
    tok, mod = _encoder()
    # Xếp theo độ dài rồi mới chia lô: lô toàn câu dài-ngắn lẫn lộn thì phần
    # đệm chiếm phần lớn phép tính. Xếp trước nhanh hơn ~1,5-2 lần.
    order = sorted(miss, key=lambda t: len(_texts[t]))
    done = 0
    with torch.inference_mode():
        for s in range(0, len(order), BATCH):
            chunk = order[s:s + BATCH]
            enc = tok([_texts[t] for t in chunk], padding=True, truncation=True,
                      max_length=MAX_LEN, return_tensors="pt")
            h = mod(**enc).last_hidden_state
            m = enc["attention_mask"].unsqueeze(-1).float()
            vecs = ((h * m).sum(1) / m.sum(1)).numpy().astype(np.float32)
            for t, v in zip(chunk, vecs):
                _vec[t] = v
                k = _key(_texts[t])
                _shard(k)[k] = v
                _dirty.add(k[:2])
            done += len(chunk)
            if verbose and len(order) > 200 and (s // BATCH) % 20 == 0:
                print(f"    [text_backend] nhúng {done}/{len(order)}", flush=True)
    # Ghi mảnh theo đợt: đường ống có lúc nhúng lẻ từng văn bản một, ghi đĩa
    # mỗi lần thì I/O lấn át cả phép tính.
    if sum(len(_shards[sh]) for sh in _dirty) > 2000 or len(order) > 200:
        _flush()
    if verbose and len(order) > 200:
        print(f"    [text_backend] xong {len(order)} văn bản mới", flush=True)


def _design(df: pd.DataFrame, cols) -> np.ndarray:
    embed_pending()
    tid = df[TID_COL].to_numpy(dtype=int)
    E = np.vstack([_vec[t] for t in tid])
    if cols:
        return np.hstack([E, df[list(cols)].to_numpy(dtype=float)])
    return E


class TextModel:
    """Bọc hồi quy logistic sao cho giống hệt giao diện của XGBClassifier.

    Luôn trả đủ 4 cột xác suất, kể cả khi một lát huấn luyện thiếu mức nào đó —
    phía gọi tính E[y] bằng `p @ arange(4)` nên số cột phải cố định.
    """

    def __init__(self, lr, imp, sc, cols):
        self.lr, self.imp, self.sc, self.cols = lr, imp, sc, list(cols)

    def _z(self, df: pd.DataFrame) -> np.ndarray:
        return self.sc.transform(self.imp.transform(_design(df, self.cols)))

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        p = self.lr.predict_proba(self._z(df))
        full = np.zeros((p.shape[0], 4))
        for j, c in enumerate(self.lr.classes_):
            full[:, int(c)] = p[:, j]
        return full

    def contrib_rows(self, df: pd.DataFrame, groups: dict) -> dict:
        return _contrib(self._z(df), self.lr.coef_, self.cols, groups)


def _contrib(z, W, cols, groups: dict) -> dict:
    """Quy kết TUYẾN TÍNH thay cho TreeSHAP — TỪNG HÀNG.

    Đóng góp của một khối = hệ số × giá trị đã chuẩn hoá, cộng trong khối, rồi
    lấy |.| trung bình trên các lớp (đúng cách `group_attribution` gộp
    pred_contribs của TreeSHAP). Khối `__text__` là phần biểu diễn văn bản —
    768 chiều nhúng, hoặc mấy chục nghìn cột TF-IDF. Khối này KHÔNG tồn tại ở
    mô hình `xgb15`, và chính nó trả lời "bao nhiêu quyết định đến từ văn bản
    chứ không từ cột viết tay nào".

    Ở chế độ `emb` không có cột luật tay nào, nên mọi khối đặt tên được đều
    bằng 0 và khối `__text__` chiếm tất cả — đó là điểm 100 % của đường cong,
    không phải lỗi.
    """
    cols = list(cols)
    n_text = z.shape[1] - len(cols)
    n = z.shape[0]
    # Khối văn bản lấy bằng LÁT CẮT chứ không bằng danh sách chỉ số: ở mô hình
    # TF-IDF khối này tới mấy chục nghìn cột, và cắt lát trên ma trận thưa rẻ
    # hơn hẳn việc dựng một danh sách chỉ số dài như vậy.
    out = {"__text__": (np.abs(np.asarray(z[:, :n_text] @ W[:, :n_text].T))
                        .mean(axis=1) if n_text else np.zeros(n))}
    for name, cs in groups.items():
        ids = [n_text + cols.index(c) for c in cs if c in cols]
        out[name] = (np.abs(np.asarray(z[:, ids] @ W[:, ids].T)).mean(axis=1)
                     if ids else np.zeros(n))
    return out


class TfidfModel:
    """TF-IDF (từ 1–2 gram + ký tự 2–5 gram) + 15 cột, hồi quy logistic.

    Cố ý để thưa: TF-IDF đã chuẩn hoá L2 theo hàng nên không đưa qua
    StandardScaler; chỉ 15 cột luật tay mới được điền khuyết + chuẩn hoá, rồi
    ghép vào. Giao diện giống hệt `TextModel` nên mọi tool phía sau không biết
    mình đang gọi mô hình nào.
    """

    def __init__(self, lr, vw, vc, imp, sc, cols):
        self.lr, self.vw, self.vc = lr, vw, vc
        self.imp, self.sc, self.cols = imp, sc, list(cols)

    def _z(self, df: pd.DataFrame):
        from scipy import sparse as sp
        txt = [_texts[t] for t in df[TID_COL].to_numpy(dtype=int)]
        Z = sp.hstack([self.vw.transform(txt), self.vc.transform(txt)]).tocsr()
        if not self.cols:
            return Z
        D = self.sc.transform(self.imp.transform(
            df[self.cols].to_numpy(dtype=float)))
        return sp.hstack([Z, sp.csr_matrix(D)]).tocsr()

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        p = self.lr.predict_proba(self._z(df))
        full = np.zeros((p.shape[0], 4))
        for j, c in enumerate(self.lr.classes_):
            full[:, int(c)] = p[:, j]
        return full

    def contrib_rows(self, df: pd.DataFrame, groups: dict) -> dict:
        return _contrib(self._z(df), self.lr.coef_, self.cols, groups)


def _fit_tfidf(texts_tr, Xtr_cols, ytr, cols):
    from scipy import sparse as sp
    from sklearn.feature_extraction.text import TfidfVectorizer
    vw = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=2)
    vc = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=3,
                         sublinear_tf=True, max_features=40000)
    Z = sp.hstack([vw.fit_transform(texts_tr), vc.fit_transform(texts_tr)]).tocsr()
    imp = sc = None
    if cols:
        imp = SimpleImputer(strategy="median").fit(Xtr_cols)
        sc = StandardScaler().fit(imp.transform(Xtr_cols))
        Z = sp.hstack([Z, sp.csr_matrix(sc.transform(imp.transform(Xtr_cols)))]).tocsr()
    lr = LogisticRegression(C=C_TFIDF, max_iter=2000).fit(Z, ytr)
    return TfidfModel(lr, vw, vc, imp, sc, cols)


def _fit_fold(X: pd.DataFrame, y: np.ndarray, tr, cols):
    """Huấn luyện MỘT lát, theo đúng chế độ đang bật."""
    if USE_TFIDF:
        tid = X.iloc[tr][TID_COL].to_numpy(dtype=int)
        Xc = X.iloc[tr][cols].to_numpy(dtype=float) if cols else None
        return _fit_tfidf([_texts[t] for t in tid], Xc, y[tr], cols)
    Xtr = _design(X.iloc[tr], cols)
    imp = SimpleImputer(strategy="median").fit(Xtr)
    sc = StandardScaler().fit(imp.transform(Xtr))
    lr = LogisticRegression(C=C_LR, max_iter=2000)
    lr.fit(sc.transform(imp.transform(Xtr)), y[tr])
    return TextModel(lr, imp, sc, cols)


def _model_cols(cols) -> list:
    """15 cột luật tay có được đưa VÀO mô hình không (chế độ `emb` thì không).

    X vẫn giữ đủ cột ở mọi chế độ — máy quy kết, định nghĩa trục và hồi quy
    khống chế hop đều đọc chúng; chỉ riêng mô hình là không nhìn.
    """
    cols = [c for c in (list(cols) if cols else []) if c != TID_COL]
    return cols if USE_COLS else []


def fit_out_of_fold(X: pd.DataFrame, y: np.ndarray, seed: int, cols=None) -> dict:
    """Cùng chữ ký và cùng cách chia lát với `counterfactual_validity`."""
    cols = _model_cols(cols if cols else list(X.columns))
    if USE_EMB:
        embed_pending()
    model_of = {}
    for tr, te in StratifiedKFold(n_splits=5, shuffle=True,
                                  random_state=seed).split(X, y):
        m = _fit_fold(X, y, tr, cols)
        for i in te:
            model_of[int(i)] = m
    return model_of


def grouped_fit(X: pd.DataFrame, y: np.ndarray, groups, seed: int, cols=None,
                n_splits: int = 5):
    """Bản chia lát THEO NHÓM (dùng cho natural_raters: bản sao phải cùng lát)."""
    from sklearn.model_selection import GroupKFold
    cols = _model_cols(cols if cols else list(X.columns))
    if USE_EMB:
        embed_pending()
    pred = np.zeros(len(y), dtype=int)
    for tr, te in GroupKFold(n_splits=n_splits).split(X, y, groups):
        pred[te] = _fit_fold(X, y, tr, cols).predict_proba(
            X.iloc[te]).argmax(axis=1)
    return pred


atexit.register(_flush)


def stats() -> dict:
    return {"mode": MODE,
            "model": MODEL_NAME if USE_EMB else "tfidf(word 1-2 + char_wb 2-5)",
            "C": C_TFIDF if USE_TFIDF else C_LR,
            "handcrafted_cols": USE_COLS,
            "n_texts": len(_texts), "n_embedded": len(_vec)}
