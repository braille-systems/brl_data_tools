import numpy as np
import matplotlib.pyplot as plt

from scripts.needleman_wunsch import forward_pass, backtrack, InDelSymbols

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

    fig, ax = plt.subplots()
    ax.imshow(scores)
    ax.set_xticks(np.arange(len(ref)))
    ax.set_yticks(np.arange(len(query)))
    ax.set_xticklabels(ref)
    ax.set_yticklabels(query)
    ax.xaxis.tick_top()
    for i in range(len(query)):
        for j in range(len(ref)):
            ax.text(j, i, scores[i, j],
                    ha="center", va="center", color="w")
    fig.tight_layout()
    plt.savefig("data/out/needlemah_wunsch.png")


def test_backtrack():
    scores, path = forward_pass(ref=ref, query=query)
    ref_aligned, query_aligned, score = backtrack(scores=scores, path=path, ref=ref, query=query)
    assert ref_aligned == "aribbe"
    assert query_aligned == "bri" + InDelSymbols.delet + "be"
    assert score == 2
