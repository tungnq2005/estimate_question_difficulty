"""
Entity Embedding Cache
=======================
Pre-compute PhoBERT embeddings cho ALL entities trong Knowledge Graph.
Cache kết quả để mỗi lần tính knowledge_entropy chỉ cần embed text mới,
không cần embed lại toàn bộ entities.

V4.1 - Knowledge-Augmented Difficulty (KAD)

Caching strategy:
  1. Pre-compute embedding cho tất cả entity labels (1 lần, ~5s nếu có GPU)
  2. Lazy LRU cache cho text embeddings (tối đa 1000 texts)
  3. Vectorized cosine similarity với numpy

Dependencies:
  - transformers (phobert-base)
  - torch (PyTorch) — optional, fallback nếu không có
  - numpy

Note: Nếu không có torch, pipeline vẫn chạy với Block B/C = 0.0
"""

from __future__ import annotations

from functools import lru_cache
from typing import Dict, List, Optional

import json
import pickle
from pathlib import Path

import numpy as np

# Lazy import torch (chỉ load khi thực sự cần compute embeddings)
_torch = None

def _get_torch():
    global _torch
    if _torch is None:
        try:
            import torch
            _torch = torch
        except ImportError:
            raise ImportError(
                "PyTorch is required for embedding features. "
                "Install with: pip install torch torchvision torchaudio"
            )
    return _torch

# Lazy check for torch availability
_TORCH_AVAILABLE = False
try:
    import torch
    _TORCH_AVAILABLE = True
except ImportError:
    pass


class EntityEmbeddingCache:
    """
    Pre-compute PhoBERT embeddings for all KG entities.

    Usage:
        cache = EntityEmbeddingCache()
        cache.precompute_all(["Hồ Chí Minh", "Điện Biên Phủ", ...])

        # Then for any text:
        vec = cache.embed_text("Hiệp định Paris năm 1973")
        # Cosine similarity with all entities is O(N) vectorized
    """

    def __init__(self, model_name: str = "vinai/phobert-base"):
        self.model_name = model_name
        self._model = None
        self._tokenizer = None
        self.entity_embeddings: Dict[str, np.ndarray] = {}
        self._labels: List[str] = []
        self._device = "cpu"
        if _TORCH_AVAILABLE:
            self._device = "cuda" if torch.cuda.is_available() else "cpu"

    def _load_model(self):
        """Load PhoBERT model (lazy: chỉ load khi cần)."""
        if self._model is not None:
            return
        torch = _get_torch()  # will raise if not installed
        print(f"  [Embedding] Loading PhoBERT model on {self._device}...", flush=True)
        from transformers import AutoModel, AutoTokenizer
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self._model = AutoModel.from_pretrained(self.model_name)
        self._model.to(self._device)
        self._model.eval()
        print(f"  [Embedding] ✅ Model loaded ({sum(p.numel() for p in self._model.parameters()):,} params)")

    def precompute_all(self, labels: List[str], batch_size: int = 16):
        """
        Pre-compute embedding cho tất cả entity labels.

        Args:
            labels: List các entity labels từ KG
            batch_size: Số lượng batch để tối ưu GPU memory
        """
        self._load_model()
        self._labels = labels

        print(f"  [Embedding] Pre-computing {len(labels)} entity embeddings...", flush=True)
        all_embeddings = []

        for i in range(0, len(labels), batch_size):
            batch = labels[i:i + batch_size]
            batch_embs = self._embed_batch(batch)
            all_embeddings.extend(batch_embs)

            if (i + batch_size) % 64 == 0 or (i + batch_size) >= len(labels):
                print(f"    ... {min(i + batch_size, len(labels))}/{len(labels)} entities", flush=True)

        for label, emb in zip(labels, all_embeddings):
            self.entity_embeddings[label] = emb

        print(f"  [Embedding] ✅ Pre-computed {len(self.entity_embeddings)} entity embeddings")

    def _embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Embed một batch texts, trả về list numpy vectors."""
        torch = _get_torch()
        assert self._tokenizer is not None
        assert self._model is not None

        inputs = self._tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors="pt"
        ).to(self._device)

        with torch.no_grad():
            outputs = self._model(**inputs)
            # Mean pooling over tokens (trừ padding)
            attention_mask = inputs["attention_mask"].unsqueeze(-1)
            embeddings = (outputs.last_hidden_state * attention_mask).sum(dim=1)
            embeddings = embeddings / attention_mask.sum(dim=1).clamp(min=1)

        return [emb.cpu().numpy().flatten() for emb in embeddings]

    @lru_cache(maxsize=1000)
    def embed_text(self, text: str) -> np.ndarray:
        """
        Embed một text bất kỳ (có LRU cache).

        Args:
            text: Văn bản cần embed (stem, option, ...)

        Returns:
            np.ndarray shape=(768,)
        """
        self._load_model()
        return self._embed_batch([text])[0]

    def save(self, path: str | Path):
        """Lưu entity embeddings ra disk để tái sử dụng.
        
        Args:
            path: Đường dẫn file .pkl
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "labels": self._labels,
            "embeddings": {
                label: emb.tolist() for label, emb in self.entity_embeddings.items()
            },
            "model_name": self.model_name,
        }
        with open(path, "wb") as f:
            pickle.dump(data, f)
        print(f"  [Embedding] 💾 Saved {len(self.entity_embeddings)} embeddings to {path}")
    
    def load(self, path: str | Path) -> bool:
        """Load entity embeddings từ disk (bỏ qua compute lại).
        
        Args:
            path: Đường dẫn file .pkl đã lưu trước đó
        
        Returns:
            True nếu load thành công, False nếu file không tồn tại
        """
        path = Path(path)
        if not path.exists():
            return False
        
        with open(path, "rb") as f:
            data = pickle.load(f)
        
        self._labels = data["labels"]
        self.entity_embeddings = {
            label: np.array(emb) for label, emb in data["embeddings"].items()
        }
        self.model_name = data.get("model_name", self.model_name)
        
        print(f"  [Embedding] 📂 Loaded {len(self.entity_embeddings)} embeddings from {path}")
        return True

    def clear_cache(self):
        """Clear LRU cache nếu cần."""
        self.embed_text.cache_clear()



if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    # Test với danh sách entity nhỏ
    test_labels = [
        "Hồ Chí Minh",
        "Chiến tranh thế giới thứ hai",
        "Điện Biên Phủ",
        "Cách mạng tháng Tám",
        "Hiệp định Paris",
    ]

    cache = EntityEmbeddingCache()
    cache.precompute_all(test_labels)

    # Test entropy
    from scipy.special import softmax
    from sklearn.metrics.pairwise import cosine_similarity

    texts = [
        "Hiệp định Paris năm 1973",
        "Cách mạng tháng Tám năm 1945",
        "So sánh Điện Biên Phủ và Cần Vương",
    ]

    print("\n[TEST] Knowledge Entropy:")
    for text in texts:
        v_text = cache.embed_text(text)
        entity_embs = np.array(list(cache.entity_embeddings.values()))

        cosines = cosine_similarity([v_text], entity_embs)[0]
        tau = 0.1
        probs = softmax(cosines / tau)
        probs = np.clip(probs, 1e-10, 1.0)
        entropy = -np.sum(probs * np.log(probs))
        max_entropy = np.log(len(probs))
        entropy_norm = entropy / max_entropy

        # Top-3 entities
        top_idx = np.argsort(cosines)[-3:][::-1]
        top_ents = [test_labels[i] for i in top_idx]

        print(f"  {text}")
        print(f"    Top entities: {top_ents}")
        print(f"    Entropy: {entropy_norm:.4f} (normalized)")
        print()
