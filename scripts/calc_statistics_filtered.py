from pprint import pprint

import enchant
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Set, List, Tuple

from scripts import read_text, OneLineString, AlphaNumericString


@dataclass
class TextStats:
    word_errs: List[Tuple[str, str]]
    n_words: int = 0
    n_correct_words: int = 0
    n_word_errs: int = 0  # real world errs
    n_punctuation_errs: int = 0  # number of words with punctuation errors only
    n_spelling_errs: int = 0  # non-word errors

    def __add__(self, other: "TextStats") -> "TextStats":
        return TextStats(
            self.word_errs + other.word_errs,
            self.n_words + other.n_words,
            self.n_correct_words + other.n_correct_words,
            self.n_word_errs + other.n_word_errs,
            self.n_punctuation_errs + other.n_punctuation_errs,
            self.n_spelling_errs + other.n_spelling_errs,
        )


def calc_non_word_errs(ref: str, query: str, vocab: Set[str], dic: enchant.Dict) -> TextStats:
    i_char = i_start_word = 0
    stats = TextStats([])

    while i_char < len(ref):
        if ref[i_char] == " ":
            word_ref = ref[i_start_word:i_char]
            word_query = query[i_start_word:i_char]
            word_ref_alnum = AlphaNumericString(OneLineString(word_ref)).text
            word_query_alnum = AlphaNumericString(OneLineString(word_query)).text.replace(" ", "")
            if word_ref_alnum in vocab:
                stats.n_words += 1

                if word_query == word_ref:
                    stats.n_correct_words += 1
                elif word_ref_alnum == word_query_alnum:
                    stats.n_punctuation_errs += 1
                elif not len(word_query_alnum) or dic.check(word_query_alnum):
                    stats.n_word_errs += 1
                    stats.word_errs.append((word_ref_alnum, word_query_alnum))
                else:
                    stats.n_spelling_errs += 1

            else:
                print("could not find in vocabulary: " + word_ref)  # TODO logging (debug)
            i_start_word = i_char + 1

        i_char += 1
    return stats


def main():
    filtered_alns_dir = Path("data/9a_corrected_alns")
    vocab_dir = Path("data/ref/4_vocabulary")

    vocabs = {vocab_filename.stem: set(read_text(vocab_filename).split()) for vocab_filename in
              vocab_dir.rglob("*.txt")}
    dic = enchant.Dict("en_US")

    stats = TextStats([])
    for aln_file_name in filtered_alns_dir.rglob("*.txt"):
        ref, query = read_text(aln_file_name).strip().split("\n")[:2]
        stats += calc_non_word_errs(ref=ref, query=query,
                                    vocab=vocabs[re.sub(r"_p[0-9]+", "", aln_file_name.stem)], dic=dic)
    pprint(sorted(stats.word_errs))
    stats.word_errs = []
    pprint(stats)


if __name__ == "__main__":
    main()
