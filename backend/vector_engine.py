"""
Vector Embedding and Semantic Vectorizer Engine.
Converts resumes and job descriptions into high-dimensional dense vector embeddings
and computes point-by-point vector similarity using cosine distance.
Provides full vector inspection, dimensional activations, and section embeddings for debugging.
"""
import re
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Default embedding dimension for all-MiniLM-L6-v2
DEFAULT_DIM = 384

class VectorEmbeddingEngine:
    def __init__(self, dimension: int = DEFAULT_DIM):
        self.dimension = dimension
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def _split_into_points(self, text: str) -> List[str]:
        """Split document into discrete meaningful points or bullet sentences."""
        lines = text.split('\n')
        points = []
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            # Remove leading bullet symbols
            clean = re.sub(r'^[•\-\*\u2022\u2023\u25E6\d\.\)\s]+', '', line_str).strip()
            # Only keep substantive statements (> 20 chars, not just short headers)
            if len(clean) >= 20 and len(clean.split()) >= 4:
                # Avoid pure header lines like "WORK EXPERIENCE" or "EDUCATION"
                if not (clean.isupper() and len(clean.split()) <= 3):
                    points.append(clean)

        # Fallback to sentence splitting if lines were few
        if len(points) < 3:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            points = [s.strip() for s in sentences if len(s.strip()) >= 25]

        return points[:15]  # Take top relevant points

    def vectorize_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate dense normalized vector embeddings using SentenceTransformers.
        """
        if not texts:
            return np.zeros((0, self.dimension))
        
        # encode handles tokenization, forward pass, and pooling
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings

    def generate_document_vector(self, text: str, sections: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generate full dense embedding vector and diagnostic metadata for a document (e.g. uploaded resume).
        Computes the document-level vector, statistics, top active latent dimensions,
        and section-level embedding vectors for interactive frontend debugging.
        """
        if not text or not text.strip():
            empty_vec = [0.0] * self.dimension
            return {
                "dimension": self.dimension,
                "vector": empty_vec,
                "preview": empty_vec[:16],
                "stats": {
                    "norm": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "mean": 0.0,
                    "active_dimensions": 0,
                    "sparsity_pct": 100.0
                },
                "top_dimensions": [],
                "section_embeddings": []
            }

        # Vectorize document text
        doc_vectors = self.vectorize_texts([text])
        raw_vec = doc_vectors[0]
        vec_list = [round(float(v), 4) for v in raw_vec]

        # Calculate vector statistics
        norm_val = round(float(np.linalg.norm(raw_vec)), 4)
        min_val = round(float(np.min(raw_vec)), 4)
        max_val = round(float(np.max(raw_vec)), 4)
        mean_val = round(float(np.mean(raw_vec)), 4)
        active_dims = int(np.sum(np.abs(raw_vec) > 0.01))
        sparsity_pct = round(float((self.dimension - active_dims) / self.dimension) * 100.0, 1)

        # Identify top activated dimensions (highest absolute magnitude)
        top_indices = np.argsort(np.abs(raw_vec))[::-1][:8]
        top_dimensions = []
        for idx in top_indices:
            val = float(raw_vec[idx])
            top_dimensions.append({
                "dimension": int(idx),
                "weight": round(val, 4),
                "intensity": round(abs(val) * 100, 1),
                "sign": "positive" if val >= 0 else "negative"
            })

        # Calculate section-level embeddings if sections are provided
        section_embeddings = []
        if sections:
            sec_keys = [k for k, v in sections.items() if k != "header" and v and len(v.strip()) > 30]
            if sec_keys:
                sec_texts = [sections[k] for k in sec_keys]
                sec_vecs = self.vectorize_texts(sec_texts)
                for i, k in enumerate(sec_keys):
                    s_vec = sec_vecs[i]
                    s_vec_list = [round(float(v), 4) for v in s_vec]
                    s_active = int(np.sum(np.abs(s_vec) > 0.01))
                    section_embeddings.append({
                        "section": k.capitalize(),
                        "dimension": self.dimension,
                        "vector": s_vec_list,
                        "preview": s_vec_list[:16],
                        "active_dimensions": s_active,
                        "norm": round(float(np.linalg.norm(s_vec)), 4),
                        "max_weight": round(float(np.max(np.abs(s_vec))), 4)
                    })

        return {
            "dimension": self.dimension,
            "vector": vec_list,
            "preview": vec_list[:16],
            "stats": {
                "norm": norm_val,
                "min": min_val,
                "max": max_val,
                "mean": mean_val,
                "active_dimensions": active_dims,
                "sparsity_pct": sparsity_pct
            },
            "top_dimensions": top_dimensions,
            "section_embeddings": section_embeddings
        }

    def compute_embedding_match(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        """
        Compute dense vector embeddings and point-by-point semantic vector resonance.
        Includes full vector representations for both documents to enable frontend debugging.
        """
        # 1. Overall document vectors
        doc_vectors = self.vectorize_texts([resume_text, jd_text])
        resume_vec = doc_vectors[0:1]
        jd_vec = doc_vectors[1:2]

        overall_sim = float(cosine_similarity(resume_vec, jd_vec)[0][0])
        # Apply a realistic "Square Root Curve" to the cosine similarity.
        # This naturally boosts semantic matches without artificially adding flat points.
        overall_vector_score = round(min(100.0, max(0.0, (max(0, overall_sim) ** 0.5) * 100.0)), 1)

        # 2. Extract discrete requirement points from JD and achievements from Resume
        jd_points = self._split_into_points(jd_text)
        resume_points = self._split_into_points(resume_text)

        point_matches = []
        covered_count = 0

        if jd_points and resume_points:
            all_points = jd_points + resume_points
            all_vecs = self.vectorize_texts(all_points)

            jd_vecs = all_vecs[:len(jd_points)]
            resume_vecs = all_vecs[len(jd_points):]

            # Compute similarity matrix: [num_jd_points, num_resume_points]
            sim_matrix = cosine_similarity(jd_vecs, resume_vecs)

            for i, jd_p in enumerate(jd_points):
                best_j = int(np.argmax(sim_matrix[i]))
                raw_sim = float(sim_matrix[i][best_j])
                
                # Apply a realistic "Square Root Curve" to point-by-point cosine similarity.
                # Example: raw 0.49 -> 70% | raw 0.64 -> 80% | raw 0.81 -> 90%
                match_pct = round(min(100.0, max(0.0, (max(0, raw_sim) ** 0.5) * 100.0)), 1)

                status = "high" if match_pct >= 80.0 else "medium" if match_pct >= 60.0 else "low"
                if match_pct >= 60.0:
                    covered_count += 1

                point_matches.append({
                    "jd_requirement": jd_p,
                    "matched_resume_bullet": resume_points[best_j],
                    "vector_similarity": match_pct,
                    "raw_cosine": round(raw_sim, 4),
                    "status": status
                })

        coverage_pct = round((covered_count / max(1, len(jd_points))) * 100, 1) if jd_points else 75.0

        resume_vec_list = [round(float(v), 4) for v in resume_vec[0]]
        jd_vec_list = [round(float(v), 4) for v in jd_vec[0]]

        # Dimension correlation array for vector debugger: element-wise product of normalized vectors
        element_products = [round(float(resume_vec[0][k] * jd_vec[0][k]), 4) for k in range(self.dimension)]

        return {
            "overall_vector_similarity": overall_vector_score,
            "vector_dimension": self.dimension,
            "embedding_type": "HuggingFace MiniLM-L6-v2 Dense 384-D Semantic Space",
            "coverage_percentage": coverage_pct,
            "total_jd_points_vectorized": len(jd_points),
            "total_resume_points_vectorized": len(resume_points),
            "point_by_point_matches": point_matches,
            "resume_vector": resume_vec_list,
            "jd_vector": jd_vec_list,
            "dimensional_correlation": element_products,
            "vector_stats": {
                "resume_norm": round(float(np.linalg.norm(resume_vec[0])), 4),
                "jd_norm": round(float(np.linalg.norm(jd_vec[0])), 4),
                "cosine_similarity": round(overall_sim, 4)
            }
        }

# Singleton instance
vector_engine = VectorEmbeddingEngine()

def get_vector_match(resume_text: str, jd_text: str) -> Dict[str, Any]:
    return vector_engine.compute_embedding_match(resume_text, jd_text)

def get_semantic_similarity(text1: str, text2: str) -> float:
    """
    Computes a direct cosine similarity (0-100) between two text strings
    using the dense vector embeddings.
    """
    if not text1.strip() or not text2.strip():
        return 0.0
        
    vecs = vector_engine.vectorize_texts([text1, text2])
    sim = float(cosine_similarity(vecs[0:1], vecs[1:2])[0][0])
    
    # Apply a modest curve to stretch semantic closeness
    score = min(100.0, max(0.0, (max(0, sim) ** 0.5) * 100.0))
    return round(score, 1)
