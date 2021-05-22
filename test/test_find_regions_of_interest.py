from pathlib import Path

from scripts.preprocess_text import StringForAlignment, OneLineString, read_text
from scripts.find_regions_of_intetest import build_ktuple_database, find_regions


def test_build_ktuples_database():
    ref = StringForAlignment(OneLineString("^lean mean green machine."))
    ktuples_to_bins = build_ktuple_database(ref=ref, bin_size=7, k=3)
    assert ktuples_to_bins["ean"] == {0, 1}
    assert ktuples_to_bins["n m"] == {0, 2}
    assert ktuples_to_bins["ine"] == {3}
    assert ktuples_to_bins["chi"] == set()


def test_find_regions():
    out_dir = Path("data/out/test_find_regions")
    find_regions(ref_dir=Path("data/ref/"),
                 queries_dir=Path("data/queries"),
                 out_dir=out_dir,
                 name_prefix="short_for_alignment", bin_size=5, bins_per_region=3, k=4)
    assert read_text(out_dir / "short_for_alignment_1.ref.txt").strip() == "an city, ^you will find i"

