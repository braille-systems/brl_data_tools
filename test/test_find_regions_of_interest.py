from pathlib import Path

import matplotlib.pyplot as plt
import pytest

from scripts.preprocess_text import StringForAlignment, OneLineString, read_text
from scripts.find_regions_of_interest import build_ktuple_database, find_regions

out_dir = Path("data/out/test_find_regions")


def test_build_ktuples_database():
    ref = StringForAlignment(OneLineString("^lean mean green machine."))
    ktuples_to_bins = build_ktuple_database(ref=ref, bin_size=7, k=3)
    assert ktuples_to_bins["ean"] == {0, 1}
    assert ktuples_to_bins["n m"] == {0, 2}
    assert ktuples_to_bins["ine"] == {3}
    assert ktuples_to_bins["chi"] == set()


def test_find_regions():
    find_regions(ref_dir=Path("data/ref/"),
                 queries_dir=Path("data/queries"),
                 out_dir=out_dir,
                 name_prefix="short_for_alignment", bin_size=5, bins_per_region=3, k=4)
    assert read_text(out_dir / "short_for_alignment_1.ref.txt").strip() == "an city, ^you will find i"


@pytest.mark.slow
def test_find_regions_big():
    ref_dir = Path("../data/ref/5_for_alignment")
    queries_dir = Path("data/queries")
    bins_per_region = 4
    bin_size = (40 * 25) // bins_per_region
    ref = StringForAlignment(OneLineString(read_text(ref_dir / "scarlet_letter.txt")))
    for k in range(10, 40, 5):
        ktuples_to_bins = build_ktuple_database(ref=ref, bin_size=bin_size, k=k)
        n_bins = len(ref.text) // bin_size + 1

        query = read_text(queries_dir / "scarlet_letter_p311.query.txt")

        matches_per_bin = [0 for _ in range(n_bins)]
        for ktuple in [query[i_char:i_char + k] for i_char in range(len(query) - k + 1)]:
            for i_bin in ktuples_to_bins[ktuple]:
                matches_per_bin[i_bin] += 1

        matches_per_region = [sum(matches_per_bin[i:i + bins_per_region]) for i in range(n_bins - bins_per_region + 1)]
        plt.figure()
        plt.plot(list(range(len(matches_per_region))), matches_per_region)
        plt.savefig(str(out_dir / "find_regions_k{}.png".format(k)))
