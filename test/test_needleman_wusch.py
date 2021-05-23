import numpy as np

from scripts.needleman_wuhsch import forward_pass, backtrack, InDelSymbols

ref = "$caribbean"
query = "$bribe"


def test_forward_pass():
    scores, path = forward_pass(ref=ref, query=query)
    assert (scores == np.array(
        [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [-1, -1, -1, -1, -1, 1, 1, 0, -1, -1],
         [-2, -2, -2, 0, -1, 0, 0, 0, -1, -2],
         [-3, -3, -3, -1, 1, 0, -1, -1, -1, -2],
         [-4, -4, -4, -2, 0, 2, 1, 0, -1, -2],
         [-5, -5, -5, -3, -1, 1, 1, 2, 2, 2]]
    )).all()
    print(path)


def test_backtrack():
    scores, path = forward_pass(ref=ref, query=query)
    ref_aligned, query_aligned, score = backtrack(scores=scores, path=path, ref=ref, query=query)
    assert ref_aligned == "aribbe"
    assert query_aligned == "bri" + InDelSymbols.delet + "be"
    assert score == 2
