import csv
import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path
from typing import Dict

from scripts.preprocess_text import read_text, write_text, OneLineString, AlphaNumericString, calc_occurrences
from scripts.needleman_wunsch import InDelSymbols


def create_oneline_alns(out_dir: Path) -> None:
    for aln_filename in Path("data/7_aligned").rglob("*.txt"):
        ref, query = read_text(aln_filename).split("\n")[0:2]
        query_corrected = []
        for i_char in range(len(ref)):
            if query[i_char] != InDelSymbols.ins and ref[i_char] != InDelSymbols.delet:
                query_corrected.append(ref[i_char])

        write_text(out_dir / aln_filename.name, AlphaNumericString(OneLineString("".join(query_corrected))).text)


def read_csv_stats(stats_file_name: Path) -> Dict[str, float]:
    result = {}
    with open(str(stats_file_name)) as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            result[row[0].strip()] = float(row[1].strip())
    return result


def main():
    vocab_dir = Path("data/ref/4_vocabulary")
    aligned_queries_dir = Path("data/8_aligned_oneline")
    aligned_queries_dir.mkdir(parents=True, exist_ok=True)
    create_oneline_alns(out_dir=aligned_queries_dir)
    calc_occurrences(queries_dir=aligned_queries_dir, vocab_dir=vocab_dir,
                     file_prefixes=("scarlet_letter", "jane_eyre"), out_file_postfix=".aligned")
    freq_before = read_csv_stats(vocab_dir / "word_freq_stats.csv").values()
    freq_after = read_csv_stats(vocab_dir / "word_freq_stats.aligned.csv").values()

    fig, axs = plt.subplots(2)
    fig.suptitle("frequency of occurrence of words in the dictionary")
    for i_plot, (freq, title) in enumerate(((freq_before, "before correction"), (freq_after, "after correction"))):
        axs[i_plot].violinplot(freq, showmedians=True, showextrema=False, vert=False)
        axs[i_plot].scatter(freq, [1 for _ in range(len(freq))], c="black", s=5)
        axs[i_plot].set(ylabel=title, yticks=[])
        print("mean of frequencies ({}): {}".format(title, np.mean(list(freq))))
    plt.yticks([])
    plt.savefig(str(vocab_dir / "frequencies.png"), dpi=1000)


if __name__ == "__main__":
    main()
