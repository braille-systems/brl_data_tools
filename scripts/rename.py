from pathlib import Path
from shutil import copyfile
from typing import Sequence


def rename_pages(in_dir: Path, out_dir: Path, start_num: int, fmt: str = "p{:04d}",
                 missing_pages: Sequence[int] = ()) -> None:
    """
    Rename pages from whatever names they have to unified format with page number, e. g. "p0001.jpg"
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    page_num = start_num
    for in_filename in Path.rglob(Path(in_dir), "*.*"):
        while page_num in missing_pages:  # TODO use set instead of sequence for O(1) complexity
            page_num += 1
        out_filename = (out_dir / fmt.format(page_num)).with_suffix(in_filename.suffix)
        copyfile(in_filename, out_filename)
        page_num += 1


def main():
    data_dir = Path("data") # run this script from the root directory of the repository
    raw_dir = data_dir / "1_raw"
    renamed_dir = data_dir / "2_renamed"
    renaming_params = {
        "scarlet_letter/vol1": (1, "p{:03d}", ()),  # verified
        "scarlet_letter/vol2": (141, "p{:03d}", ()),  # verified
        "scarlet_letter/vol3": (281, "p{:03d}", ()),  # verified
        "scarlet_letter/vol4": (405, "p{:03d}", ()),  # verified
        "jane_eyre/vol1": (1, "p{:04d}", ()),  # verified
        "jane_eyre/vol2": (149, "p{:04d}", ()),  # verified
        "jane_eyre/vol3": (307, "p{:04d}", ()),  # verified
        "jane_eyre/vol4": (475, "p{:04d}", (569,)),  # verified
        "jane_eyre/vol5": (577, "p{:04d}", ()),  # verified
        "jane_eyre/vol6": (755, "p{:04d}", ()),  # verified
        "jane_eyre/vol7": (893, "p{:04d}", ()),  # verified
        "jane_eyre/vol8": (1027, "p{:04d}", ()),  # verified
    }
    for subdir, (start_page, fmt, missing_pages) in renaming_params.items():
        rename_pages(in_dir=raw_dir / subdir,
                     out_dir=renamed_dir / subdir,
                     start_num=start_page,
                     fmt=fmt,
                     missing_pages=missing_pages)


if __name__ == "__main__":
    main()
