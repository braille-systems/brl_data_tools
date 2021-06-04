from pathlib import Path
from typing import Tuple

import numpy as np

from scripts.preprocess_text import read_text, write_text


class InDelSymbols:
    ins = "▲"
    delet = "◂"
    match = "⊙"
    dummy = "$"


def forward_pass(ref: str, query: str, penalize_tail_dels: bool = False,
                 del_penalty: int = 2) -> Tuple[np.array, np.array]:
    """
    Forward pass of modified Needleman-Wuhsch algorithm.
    assuming `ref`, `query` start with some dummy symbol
    """

    scores = np.zeros((len(query), len(ref)))
    if penalize_tail_dels:
        scores[0, :] = -np.arange(len(ref))
    scores[:, 0] = -np.arange(len(query))
    path = np.full((len(query), len(ref)), None)
    for i_row in range(1, len(query)):
        for i_col in range(1, len(ref)):
            match_score = scores[i_row - 1, i_col - 1] + (1 if ref[i_col] == query[i_row] else -1)
            del_score = scores[i_row, i_col - 1]
            if i_row != len(query) - 1:
                del_score -= 1 if penalize_tail_dels else del_penalty
            in_score = scores[i_row - 1, i_col] - 1
            scores[i_row, i_col] = max(match_score, in_score, del_score)
            if match_score == scores[i_row, i_col]:
                path[i_row, i_col] = InDelSymbols.match
            elif in_score == scores[i_row, i_col]:
                path[i_row, i_col] = InDelSymbols.ins
            else:
                path[i_row, i_col] = InDelSymbols.delet
    return scores, path


def backtrack(scores: np.array, path: np.array, ref: str, query: str) -> Tuple[str, str, int]:
    """
    Backtracking stage of modified Needleman-Wuhsch algorithm.
    :return: aligned ref, query (without dummy symbols), and score
    """
    last_col = len(ref) - 1
    while last_col > 0 and scores[len(query) - 1, last_col] == scores[len(query) - 1, last_col - 1]:
        last_col -= 1
    i_row, i_col = len(query) - 1, last_col
    score = scores[i_row, i_col]
    query_aligned, ref_aligned = [], []
    while i_row > 0:
        if path[i_row, i_col] == InDelSymbols.ins:
            query_aligned.append(query[i_row])
            ref_aligned.append(InDelSymbols.ins)
            i_row -= 1
        elif path[i_row, i_col] == InDelSymbols.delet:
            query_aligned.append(InDelSymbols.delet)
            ref_aligned.append(ref[i_col])
            i_col -= 1
        else:
            query_aligned.append(query[i_row])
            ref_aligned.append(ref[i_col])
            i_col -= 1
            i_row -= 1
    return "".join(reversed(ref_aligned)), "".join(reversed(query_aligned)), score


def main():
    seqences_dir = Path("data/6_for_alignment")
    alignment_dir = Path("data/7_aligned")
    alignment_dir.mkdir(parents=True, exist_ok=True)
    for query_filename in seqences_dir.rglob("*.query.txt"):
        ref_filename = query_filename.name.replace(".query", ".ref")
        query = InDelSymbols.dummy + read_text(query_filename).strip()
        ref = InDelSymbols.dummy + read_text(seqences_dir / ref_filename).strip()
        ref_aligned, query_aligned, score = backtrack(*forward_pass(ref=ref, query=query), ref=ref, query=query)
        write_text((alignment_dir / query_filename.stem.replace(".query", ".aln")).with_suffix(".txt"),
                   "\n".join([ref_aligned, query_aligned, str(score)]))


if __name__ == "__main__":
    main()
