from FlagEmbedding import BGEM3FlagModel
import numpy as np
import yaml
from sentence_transformers import SentenceTransformer, util
import os

os.environ["HF_HUB_DISABLE_WARNINGS"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"  # не лезть в интернет
os.environ["HF_DATASETS_OFFLINE"] = "1"


class SemanticIndex:
    def __init__(self, yaml_path: str):
        print('Загружаю модель...')
        self.model = SentenceTransformer("BAAI/bge-m3")

        with open(yaml_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.index = self._build_index()

    def _build_index(self) -> list[dict]:
        """
        Для каждой метрики из yaml создаём один текст
        и превращаем его в вектор (эмбеддинг).
        """

        index = []

        for metric_id, metric in self.config['metrics'].items():
            text = (
                    metric['label']
                    + " "
                    + metric['description']
                    + " "
                    + " ".join(metric['aliases'])
            )

            vec = self.model.encode("passage: " + text)

            index.append({'id': metric_id, 'text': text, 'vec': vec})
            # print(f'Проиндексировано: {metric_id}')

        return index

    def find_metric(self, question: str) -> tuple[str, float]:
        """
        Ищет наиболее подходящую метрику для вопроса.
        """
        query_vec = self.model.encode("query: " + question)
        # print(self.index)
        metric_vecs = np.array([item['vec'] for item in self.index])

        score = util.cos_sim(query_vec, metric_vecs)[0]

        best_idx = int(score.argmax())

        return self.index[best_idx]['id'], float(score[best_idx])

    def find_dimensions(self, question: str, threshold: float = 0.45) -> list[tuple[str, float]]:
        """
        Ищет параметры для группировки в вопросе
        Возвращает список (dimension_id, score)
        threshold - мин. score, ниже которого считаем, что измерение не упомянуто.
        """
        dim_texts = []
        dim_ids = []

        for dim_id, dim in self.config['dimensions'].items():
            text = (
                    dim['label']
                    + " "
                    + dim['description']
                    + " "
                    + " ".join(dim['aliases'])
            )
            dim_texts.append(text)
            dim_ids.append(dim_id)

        dim_vecs = self.model.encode(["passage: " + t for t in dim_texts])
        query_vecs = self.model.encode("query: " + question)

        scores = util.cos_sim(query_vecs, dim_vecs)[0]

        result = []
        for dim_id, score in zip(dim_ids, scores):
            print(f"  {dim_id}: {float(score):.4f}")

        for idx, score in enumerate(scores):
            if float(score) >= threshold:
                result.append((dim_ids[idx], float(score)))

        result.sort(key=lambda x: x[1], reverse=True)
        return result


