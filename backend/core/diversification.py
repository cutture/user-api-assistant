
import numpy as np
from typing import List, Dict, Any

class MMRRanker:
    """
    Implements Maximum Marginal Relevance (MMR) for result diversification.
    MMR tries to maximize relevance (to query) while minimizing similarity (to already selected docs).
    Score = lambda * Sim(query, doc) - (1 - lambda) * MaxSim(doc, selected_docs)
    """

    def rerank(self, 
               query_embedding: List[float], 
               candidates: List[Dict[str, Any]], 
               top_n: int = 3, 
               lambda_mult: float = 0.5) -> List[Dict[str, Any]]:
        """
        Args:
            query_embedding: Embedding vector of the user query.
            candidates: List of dicts, must contain 'embedding' and 'doc' keys.
            top_n: Number of documents to return.
            lambda_mult: 0.0 to 1.0. 
                         0.5 = Balanced. 
                         1.0 = Standard Relevance (No diversification).
                         0.0 = Max Diversity (Pure novelty).
        """
        if not candidates:
            return []
            
        # Convert inputs to numpy
        query_vec = np.array(query_embedding)
        query_norm = np.linalg.norm(query_vec)
        
        # Helper to compute sim
        def cosine_sim(v1, v2):
            n1 = np.linalg.norm(v1)
            n2 = np.linalg.norm(v2)
            if n1 == 0 or n2 == 0: return 0.0
            return np.dot(v1, v2) / (n1 * n2)

        # 1. Pre-calculate similarity of each candidate to query
        candidate_sims_to_query = []
        for cand in candidates:
            cand_vec = np.array(cand['embedding'])
            sim = cosine_sim(query_vec, cand_vec)
            candidate_sims_to_query.append(sim)

        # 2. Iterative Selection
        selected_indices = []
        candidate_indices = list(range(len(candidates)))

        while len(selected_indices) < top_n and candidate_indices:
            best_mmr_score = -float('inf')
            best_idx = -1

            for idx in candidate_indices:
                # Calculate Redundancy: Similarity to already selected docs
                redundancy = 0.0
                if selected_indices:
                    cand_vec = np.array(candidates[idx]['embedding'])
                    max_sim_to_selected = 0.0
                    for sel_idx in selected_indices:
                        sel_vec = np.array(candidates[sel_idx]['embedding'])
                        sim = cosine_sim(cand_vec, sel_vec)
                        if sim > max_sim_to_selected:
                            max_sim_to_selected = sim
                    redundancy = max_sim_to_selected

                # MMR Equation
                relevance = candidate_sims_to_query[idx]
                mmr_score = (lambda_mult * relevance) - ((1 - lambda_mult) * redundancy)


                if mmr_score > best_mmr_score:
                    best_mmr_score = mmr_score
                    best_idx = idx

            # Add best to selected
            if best_idx != -1:
                selected_indices.append(best_idx)
                candidate_indices.remove(best_idx)
            else:
                break 

        # Return fetched docs in order
        final_results = [candidates[i] for i in selected_indices]
        return final_results

# Singleton
ranker = MMRRanker()
