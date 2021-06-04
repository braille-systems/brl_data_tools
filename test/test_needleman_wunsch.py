from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import pytest

from scripts import read_text
from scripts.needleman_wunsch import forward_pass, backtrack, InDelSymbols

ref = "$caribbean"
query = "$bribe"
out_dir = Path("data/out/test_needleman_wunsch")
out_dir.mkdir(parents=True, exist_ok=True)


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

    for penalize_first_dels in (True, False):
        scores, path = forward_pass(ref=ref, query=query, penalize_first_dels=penalize_first_dels)
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
        plt.savefig(str(out_dir / "simple_penalize_{}.png".format(penalize_first_dels)))


@pytest.mark.slow
def test_forward_pass_big():
    ref_big = read_text(Path("data/ref/scarlet_letter_p311.ref.txt"))
    query_big = read_text(Path("data/queries/scarlet_letter_p311.query.txt"))
    for penalize_first_dels in (True, False):
        scores, path = forward_pass(
            ref=ref_big,
            query=query_big,
            # ref=read_text(Path("data/ref/jane_eyre_p0010.ref.txt")),
            # query=read_text(Path("data/queries/jane_eyre_p0010.query.txt")),
            penalize_first_dels=penalize_first_dels)
        plt.figure()
        plt.imshow(scores, cmap='hot', interpolation='nearest')
        plt.savefig(str(out_dir / "big_penalize{}.png".format(penalize_first_dels)))

        plt.figure()
        plt.imshow(scores[:100, :500], cmap="hot", interpolation="nearest")
        plt.savefig(str(out_dir / "big_penalize_0-100_0-500{}.png".format(penalize_first_dels)))

        ref_aligned, query_aligned, _ = backtrack(scores=scores, path=path, ref=ref_big, query=query_big)
        print("penalize: {}".format(penalize_first_dels))
        print("r: " + ref_aligned)
        print("q: " + query_aligned)


def test_backtrack():
    scores, path = forward_pass(ref=ref, query=query)
    ref_aligned, query_aligned, score = backtrack(scores=scores, path=path, ref=ref, query=query)
    assert ref_aligned == "aribbe"
    assert query_aligned == "bri" + InDelSymbols.delet + "be"
    assert score == 2

    ref_lupus, query_lupus = "$homo homini lupus est", "$homhoni lupus"
    for penalize in (True, False):
        scores, path = forward_pass(ref=ref_lupus, query=query_lupus, penalize_first_dels=penalize)
        ref_aligned, query_aligned, score = backtrack(scores=scores, path=path, ref=ref_lupus, query=query_lupus)
        print("penalize: {}".format(penalize))
        print(ref_aligned)
        print(query_aligned)
