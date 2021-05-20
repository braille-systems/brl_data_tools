from pathlib import Path
from typing import Sequence

from cv2 import cv2 as cv


def crop_horizontally(in_dir: Path, keep_fraction: float, skip_files: Sequence[str] = ()) -> None:
    for in_filename in Path.rglob(in_dir, "*.*"):
        if in_filename.name in skip_files:
            continue
        odd_page = int(in_filename.stem[-1]) % 2
        in_img = cv.imread(str(in_filename))
        h, w, _ = in_img.shape
        cropped = in_img[:, :int(w * keep_fraction), :] if odd_page else in_img[:, int(w * (1 - keep_fraction)):, :]
        hc, wc, _ = cropped.shape
        cv.imwrite(str(in_filename), cropped)


def main():
    # crop photos shot on XPeria. Warning: this will overwrite files in "2_renamed"
    xperia_keep_fraction = .65
    jane_eyre_path = Path("data/2_renamed/jane_eyre")
    janeyre_crop_params = (
        # subdir_name, list_of_files_to_skip
        ("vol6", ("jane_eyre_p0756.JPG",)),
        ("vol7", ()),
        ("vol8", ["jane_eyre_p10{}.JPG".format(n) for n in range(58, 72)]),
    )
    for subdir_name, skip_files in janeyre_crop_params:
        crop_horizontally(jane_eyre_path / subdir_name, keep_fraction=xperia_keep_fraction, skip_files=skip_files)

    crop_horizontally(Path("data/2_renamed/scarlet_letter/vol4"), keep_fraction=xperia_keep_fraction,
                      skip_files=["scarlet_letter_p4{:02d}.JPG".format(n) for n in range(5, 20)])


if __name__ == "__main__":
    main()
