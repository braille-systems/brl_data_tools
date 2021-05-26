from collections import defaultdict
from pathlib import Path
from typing import Dict, Set

from scripts.preprocess_text import read_text, StringForAlignment, OneLineString, write_text


def build_ktuple_database(ref: StringForAlignment, bin_size: int, k: int) -> Dict[str, Set[int]]:
    ktuples_to_bins = defaultdict(set)
    for i_bin in range(len(ref.text) // bin_size + 1):
        bin_left_idx, bin_right_idx = i_bin * bin_size, min(len(ref.text), (i_bin + 1) * bin_size)
        for ktuple in [ref.text[i_char:i_char + k] for i_char in range(bin_left_idx, bin_right_idx - k + 1)]:
            ktuples_to_bins[ktuple].add(i_bin)
    return ktuples_to_bins


def find_regions(ref_dir: Path, queries_dir: Path, out_dir: Path, name_prefix: str,
                 bins_per_region: int, bin_size: int, k: int) -> None:
    ref = StringForAlignment(OneLineString(read_text((ref_dir / name_prefix).with_suffix(".txt"))))
    ktuples_to_bins = build_ktuple_database(ref=ref, bin_size=bin_size, k=k)
    n_bins = len(ref.text) // bin_size + 1
    for query_filename in queries_dir.rglob(name_prefix + "*.txt"):
        query = read_text(Path(query_filename))

        matches_per_bin = [0 for _ in range(n_bins)]
        for ktuple in [query[i_char:i_char + k] for i_char in range(len(query) - k + 1)]:
            for i_bin in ktuples_to_bins[ktuple]:
                matches_per_bin[i_bin] += 1

        matches_per_region = [sum(matches_per_bin[i:i + bins_per_region]) for i in range(n_bins - bins_per_region + 1)]
        best_region_idx = 0
        max_matches = 0
        for i_region, n_matches in enumerate(matches_per_region):
            if n_matches > max_matches:
                best_region_idx, max_matches = i_region, n_matches
        left_char_idx = max(0, (best_region_idx - 1) * bin_size)
        right_char_idx = (best_region_idx + bins_per_region + 1) * bin_size
        write_text((out_dir / Path(query_filename.stem).stem).with_suffix(".ref.txt"),
                   ref.text[left_char_idx:right_char_idx])


def main():
    bins_per_region = 4
    for name_prefix in ("jane_eyre", "scarlet_letter"):
        find_regions(ref_dir=Path("data/ref/5_for_alignment"),
                     queries_dir=Path("data/6_for_alignment"),
                     out_dir=Path("data/6_for_alignment"),
                     name_prefix=name_prefix,
                     bin_size=(40 * 25) // bins_per_region,
                     bins_per_region=bins_per_region,
                     k=8)  # TODO find optimal `k`


if __name__ == "__main__":
    main()
