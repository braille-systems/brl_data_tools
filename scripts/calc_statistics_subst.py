from pathlib import Path
from pprint import pprint

import numpy as np

from scripts import read_text


def calc_alphabet(alns_dir: Path):
    alphabet = set()
    for aln_file_name in alns_dir.rglob("*.txt"):
        ref, query = read_text(aln_file_name).split("\n")[:2]
        alphabet |= set(ref)
        alphabet |= set(query)
    return "".join(sorted(alphabet))


class SubstitutionMatrix:  # I do not want to use pandas, so building a custom data-frame-like object
    names: str
    values: np.ndarray

    def __init__(self, names: str):
        self.names = names
        self.values = np.zeros((len(names), len(names)))

    def __add__(self, other: "SubstitutionMatrix") -> "SubstitutionMatrix":
        assert self.names == other.names, "could not add two matrices with different column/row names"
        result = SubstitutionMatrix(self.names)
        result.values += self.values
        result.values += other.values
        return result


def calc_substitutions_matrix(alns_dir: Path,
                              subs_mtx_filename: Path,
                              diagonal_zeros: bool = False,
                              symmetrify: bool = False):
    names = "!$&'(),-./:;?@]^abcdefghijklmnopqrstuvwxyz“”■▲◂"
    trans = "⠖$&⠄⠣⠜⠂⠤⠲⠌:⠆⠢⠿⠼⠠⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚⠅⠇⠍⠝⠕⠏⠟⠗⠎⠞⠥⠧⠺⠭⠽⠵⠦⠴■▲◂"  # TODO en question is different from ru??

    delimiter = ","

    subst_matrix = SubstitutionMatrix(names=names)
    for aln_file_name in alns_dir.rglob("*.txt"):
        ref, query = read_text(aln_file_name).split("\n")[:2]
        for r, q in zip(ref, query):
            subst_matrix.values[subst_matrix.names.find(r), subst_matrix.names.find(q)] += 1

    if diagonal_zeros:
        np.fill_diagonal(subst_matrix.values, 0)

    names_trans = "123456789ABCDEFGabcdefghijklmnopqrstuvwxyzHI?X*"  # TODO
    if symmetrify:
        subst_matrix.values += subst_matrix.values.T
    else:
        counts = subst_matrix.values.sum(axis=1)
        subst_matrix.values /= (counts + 1)[:, np.newaxis]

        most_frequent = {}
        for row, char, count in zip(subst_matrix.values, names_trans, counts):
            row = np.round(row, 2)
            freq_map = sorted(list(zip(names_trans, row)),
                              key=lambda ch_freq_pair: ch_freq_pair[1], reverse=True)
            most_frequent[char] = {"replacements": freq_map[:4], "count": count}
        for ch, dic in sorted(most_frequent.items(), key=lambda item: item[1]["count"], reverse=True):
            count = dic["count"]
            replacements = dic["replacements"]
            print("{} & {} & {} \\\\".format(ch, int(count), ", ".join(
                ["{}: {}".format(ch_replacement, freq) for ch_replacement, freq in replacements if freq > 0.05])))

    with open(str(subs_mtx_filename), "w", encoding="UTF-8") as out_file:
        out_file.write("substitution: " + delimiter + delimiter.join(names_trans) + "\n")
        for idx, char in enumerate(names_trans):
            out_file.write(
                str(char) + delimiter + delimiter.join(subst_matrix.values[idx].astype(str)) + "\n")


def main():
    filtered_alns_dir = Path("data/9a_corrected_alns")
    stats_dir = Path("data/11_alns_stats")
    stats_dir.parent.mkdir(parents=True, exist_ok=True)
    for symmetrify in (True, False):
        calc_substitutions_matrix(alns_dir=filtered_alns_dir,
                                  subs_mtx_filename=stats_dir / "subst_mtx_symmetrify{}.csv".format(symmetrify),
                                  diagonal_zeros=True, symmetrify=symmetrify)
    # print(calc_alphabet(filtered_alns_dir))  # result: !$&'(),-./:;?@]^abcdefghijklmnopqrstuvwxyz“”■▲◂


if __name__ == "__main__":
    main()
