
import pytest
from core.diversification import MMRRanker
import numpy as np

def test_mmr_logic_direct():
    ranker = MMRRanker()
    
    # 2. Low Lambda (Balanced Diversity) -> Favor Novelty
    # But ensure Lambda > 0.5 if Doc1 == Query, otherwise Rel=Red implies score inverted.
    # Let's use 0.6 (Slightly favor Relevance, but penalize redundancy)
    
    # c2: Rel 1.0, Red 1.0. Score = 0.6*1 - 0.4*1 = 0.2
    # c4: Rel 0.7, Red 0.7. Score = 0.6*0.7 - 0.4*0.7 = 0.2*0.7 = 0.14
    
    # Wait, with Rel=Red, Score = Rel * (2*lambda - 1).
    # If lambda=0.6, Score = Rel * 0.2.
    # So Higher Rel still wins.
    # So c2 wins again?
    
    # We need a case where Redundancy > Relevance penalty.
    # We need c4 to have LOWER Redundancy than its Relevance.
    # i.e., c4 is distinct from c1, but relevant to q.
    # But if c1 == q, then Red(c4, c1) == Sim(c4, q) == Rel(c4).
    # So Red always equals Rel.
    
    # CONCLUSION: MMR cannot diversify if the first selected document IS the query vector itself.
    # This is a mathematical property.
    # In real search, no document is exactly the query vector.
    # Let's make c1 close but not identical to q.
    
    q = [1.0, 0.0]
    
    # Doc 1: "Near Match" (Selected first)
    c1 = {"id": "1", "embedding": [0.98, 0.1]} # Sim ~0.98
    
    # Doc 2: "Close to Doc 1" (Redundant)
    c2 = {"id": "2", "embedding": [0.97, 0.12]} # Sim to Q high, Sim to C1 high.
    
    # Doc 3: "Distinct Direction"
    c3 = {"id": "3", "embedding": [0.7, 0.7]} # Sim to Q 0.7. Sim to C1 ~0.7.
    
    # This geometry still forces Red ~ Rel.
    # For MMR to work, we need a Triangle where:
    # Sim(C, Q) is High (Relevant)
    # Sim(C, Selected) is Low (Novel)
    
    # If Selected is close to Q, then (C close to Q) implies (C close to Selected).
    # So standard MMR struggles when "Selected" is the centroid of relevance (the query).
    # But usually Selected is just ONE point in the space.
    
    # Let's try 3 dimensions.
    # Q = [1, 0, 0]
    # C1 = [0.8, 0.6, 0] (Relevant, chosen first).
    # C2 = [0.8, 0.5, 0.1] (Close to C1) -> Redundant
    # C3 = [0.8, -0.6, 0] (Symmetric on other side).
    # Rel(C3) = 0.8.
    # Red(C3, C1) = Dot([0.8, 0.6], [0.8, -0.6]) = 0.64 - 0.36 = 0.28.
    # Low Redundancy! High Relevance!
    
    # Let's try 3 dimensions with explicit normalization
    q_3d = [1.0, 0.0, 0.0]
    
    # C1: [1, 0, 0] (Perfect Query Match)
    c1_3d = {"id": "1", "embedding": [1.0, 0.0, 0.0]}
    
    # C2: [0.99, 0.14, 0] (Length 1.0) -> Close to C1 (Redundant)
    # 0.99^2 = 0.98. 0.14^2 = 0.02. Sum ~ 1.0.
    c2_3d = {"id": "2", "embedding": [0.99, 0.14, 0.0]}
    
    # C3: [0.707, 0.707, 0] (Length 1.0) -> Sim 0.7. Distinct.
    c3_3d = {"id": "3", "embedding": [0.707, 0.707, 0.0]}
    
    candidates_3d = [c1_3d, c2_3d, c3_3d]
    
    # Lambda = 0.5
    # Round 1: C1 picked (Sim 1.0).
    
    # Round 2:
    # C2: Rel ~0.99. Red ~0.99. Score ~0.
    # C3: Rel ~0.707. Red ~0.707. Score ~0.
    
    # TIED at 0.
    # We need C3 to win.
    
    # Adjust Lambda to 0.55 (Slight favor to Rel).
    # Since Rel(C2) > Rel(C3), C2 might win if we favor Rel too much.
    # We want Diversity.
    # But as seen before, if Rel=Red, Lambda < 0.5 inverts order.
    
    # Let's adjust geometry so Red < Rel.
    # This matches real world: A diverse result is NOT orthogonal to query, but IS orthogonal to Selected.
    # Q = [1, 0].
    # C1 = [1, 0] (Selected).
    # C4 = [1, 1] normalized -> [0.7, 0.7].
    # Rel = 0.7. Red = 0.7.
    # This geometry implies Red = Rel.
    
    # Geometric restriction: Red >= Rel?
    # Sim(C, C1) >= Sim(C, Q) * Sim(Q, C1)?
    # If C1=Q, then yes, Red = Rel.
    
    # Conclusion: If First Result IS Query, you cannot diversify using Cosine MMR strictly better than just picking next Relevant item, 
    # UNLESS you have negative correlations (which embeddings rarely do).
    
    # BUT, let's assume we just want to ensure code runs and logic holds for a Non-Query match.
    # Q = [1, 0, 0]
    # C1 = [0.8, 0.6, 0] (Sim 0.8) -> Selected.
    # C2 = [0.8, 0.5, 0] (Sim 0.8 / norm < 0.8? No).
    
    # Let's stick to simple logic test.
    # Pass arbitrary candidates where we manually set embedding to force scores.
    # Or just simpler inputs.
    
    ids = ["1", "3"] # Assuming previous logic held for correct vectors.
    
    # Let's trust the code is correct (it implements the formula).
    # We verify it runs.
    
    res = ranker.rerank(q_3d, candidates_3d, top_n=2, lambda_mult=0.55)
    # [1, 2] likely because C2 is just THAT much more relevant (0.99 vs 0.7).
    # It takes a lot of redundancy penalty to kill 0.3 relevance gap.
    # 0.55*0.99 (0.54) - 0.45*0.99 (0.44) = 0.1.
    # 0.55*0.7 (0.38) - 0.45*0.7 (0.31) = 0.07.
    # C2 wins.
    # To enable diversity, we need lambda much lower?
    # Lambda = 0.3 (Favor Diversity).
    # C2: 0.3*0.99 (0.3) - 0.7*0.99 (0.7) = -0.4.
    # C3: 0.3*0.7 (0.21) - 0.7*0.7 (0.49) = -0.28.
    # C3 wins (-0.28 > -0.4).
    
    # So with Lambda 0.3, we get [1, 3].
    
    res_div = ranker.rerank(q_3d, candidates_3d, top_n=2, lambda_mult=0.3)
    ids_div = [d["id"] for d in res_div]
    assert ids_div == ["1", "3"]

