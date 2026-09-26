# -*- coding: utf-8 -*-
"""Fine-tune PhoBERT phân loại độ khó MCQ — CHẠY TRÊN GOOGLE COLAB (GPU).

===========================================================================
CÁCH DÙNG
===========================================================================
1. Mở https://colab.research.google.com  ->  New notebook
2. Runtime -> Change runtime type -> Hardware accelerator = **T4 GPU** -> Save
3. Dán từng KHỐI (đánh dấu "# %% CELL n") vào một cell riêng rồi chạy lần lượt.
4. Cell cuối tải về file `oof_phobert.csv`.
5. Về máy, chạy:
     python tools/ablation.py --csv <feature_matrix.csv> \
            --oof-phobert oof_phobert.csv

VÌ SAO PHẢI OUT-OF-FOLD (OOF):
  Nếu train PhoBERT trên toàn bộ dữ liệu rồi lấy xác suất của chính dữ liệu đó
  làm đặc trưng cho XGBoost, mô hình đã "nhìn thấy đáp án" -> rò rỉ dữ liệu,
  kết quả ảo cao. Đúng cách: chia 5 fold; với mỗi fold, train trên 4 phần và
  chỉ dự đoán phần còn lại. Ghép 5 phần dự đoán đó lại = OOF, mỗi câu đều được
  dự đoán bởi mô hình CHƯA từng thấy nó. Fold ở đây trùng khớp với fold trong
  tools/ablation.py (StratifiedKFold, shuffle=True, random_state=42) nên hai
  bên so sánh được với nhau.
===========================================================================
"""

# %% CELL 1 — Cài thư viện (~1 phút)
CELL_1 = r"""
!pip -q install transformers==4.44.2 torch --upgrade
!nvidia-smi --query-gpu=name,memory.total --format=csv
"""

# %% CELL 2 — Lấy dữ liệu từ GitHub (repo công khai của nhóm)
CELL_2 = r"""
!git clone -q https://github.com/tungnq2005/estimate_question_difficulty.git repo
!ls repo/subjects/history/samples/
"""

# %% CELL 3 — Nạp dữ liệu, dựng chuỗi đầu vào
CELL_3 = r"""
import json, numpy as np, pandas as pd

# CHỈ lấy bản canonical (is_canonical=True): ~55% bộ crawl là bản sao do lấy
# trùng từ nhiều trang mirror -> giữ nguyên thì rò rỉ giữa các fold y hệt vấn
# đề đã phát hiện ở XGBoost/TF-IDF (xem docs/RELATED_WORK.md mục 5).
rows = []
for f in ["mcq_samples.json", "mcq_crawled.json"]:
    for q in json.load(open(f"repo/subjects/history/samples/{f}", encoding="utf-8")):
        if q.get("difficulty") and q.get("is_canonical", True):
            rows.append({
                "mcq_id": q["id"],
                # Chuỗi đầu vào: câu dẫn [SEP] đáp án đúng [SEP] 3 đáp án nhiễu.
                # Đưa cả phương án vào vì độ khó phụ thuộc mức giống nhau giữa chúng.
                "text": q["stem"] + " </s> " + q["correct"] + " </s> "
                        + " </s> ".join(q["distractors"]),
                "label": {"Easy": 0, "Medium": 1, "Hard": 2}[q["difficulty"]],
            })
df = pd.DataFrame(rows)
print(len(df), "câu |", df.label.value_counts().sort_index().to_dict())
df.head(2)
"""

# %% CELL 4 — Fine-tune 5 fold, xuất xác suất out-of-fold (~15-20 phút trên T4)
CELL_4 = r"""
import numpy as np, torch, torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, cohen_kappa_score

MODEL, MAXLEN, BS, EPOCHS, LR, SEED = "vinai/phobert-base", 256, 16, 4, 2e-5, 42
dev = "cuda" if torch.cuda.is_available() else "cpu"
torch.manual_seed(SEED); np.random.seed(SEED)
tok = AutoTokenizer.from_pretrained(MODEL)

class DS(Dataset):
    def __init__(s, texts, labels):
        s.e = tok(list(texts), truncation=True, padding="max_length",
                  max_length=MAXLEN, return_tensors="pt")
        s.y = torch.tensor(labels)
    def __len__(s):  return len(s.y)
    def __getitem__(s, i):
        return {k: v[i] for k, v in s.e.items()} | {"labels": s.y[i]}

y = df.label.values
# Trọng số lớp: lớp Hard ít hơn hẳn -> phạt nặng hơn khi đoán sai lớp này
cw = torch.tensor(len(y) / (3 * np.bincount(y)), dtype=torch.float).to(dev)
oof = np.zeros((len(df), 3))

# CÙNG cách chia fold với tools/ablation.py -> kết quả so sánh được
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
for fold, (tr, va) in enumerate(cv.split(df, y), 1):
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL, num_labels=3).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=LR)
    dl = DataLoader(DS(df.text.values[tr], y[tr]), batch_size=BS, shuffle=True)
    lossf = nn.CrossEntropyLoss(weight=cw)

    model.train()
    for ep in range(EPOCHS):
        tot = 0.0
        for b in dl:
            b = {k: v.to(dev) for k, v in b.items()}
            lb = b.pop("labels")
            opt.zero_grad()
            loss = lossf(model(**b).logits, lb)
            loss.backward(); opt.step(); tot += loss.item()
        print(f"  fold {fold} epoch {ep+1}: loss {tot/len(dl):.4f}")

    model.eval()
    preds = []
    with torch.no_grad():
        for b in DataLoader(DS(df.text.values[va], y[va]), batch_size=64):
            b = {k: v.to(dev) for k, v in b.items()}; b.pop("labels")
            preds.append(torch.softmax(model(**b).logits, -1).cpu().numpy())
    oof[va] = np.vstack(preds)
    print(f"fold {fold} xong | acc {accuracy_score(y[va], oof[va].argmax(1)):.4f}")
    del model; torch.cuda.empty_cache()

p = oof.argmax(1)
print(f"\n=== PhoBERT fine-tune (5-fold OOF) ===")
print(f"accuracy {accuracy_score(y,p):.4f} | macro-F1 {f1_score(y,p,average='macro'):.4f}"
      f" | QWK {cohen_kappa_score(y,p,weights='quadratic'):.4f}")
print(f"F1 theo lớp (Easy/Medium/Hard): {f1_score(y,p,average=None).round(3)}")
"""

# %% CELL 5 — Xuất và tải file về máy
CELL_5 = r"""
out = pd.DataFrame({"mcq_id": df.mcq_id,
                    "p_easy": oof[:,0], "p_medium": oof[:,1], "p_hard": oof[:,2]})
out.to_csv("oof_phobert.csv", index=False)
from google.colab import files; files.download("oof_phobert.csv")
"""

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(__doc__)
    for i, c in enumerate([CELL_1, CELL_2, CELL_3, CELL_4, CELL_5], 1):
        print(f"\n{'='*70}\n# ===== CELL {i} — dán vào một cell Colab =====\n{'='*70}")
        print(c.strip())
