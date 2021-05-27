import random
from pathlib import Path

from scripts.preprocess_text import write_text


def split(data_dir: Path, test_part: float) -> None:
    file_names = [str(fname).replace(str(data_dir), ".") for fname in list(data_dir.rglob("*.labeled.jpg"))]
    random.seed(0)  # for reproducibility
    random.shuffle(file_names)
    test_filenames, train_filenames = file_names[:int(len(file_names) * test_part)], \
                                      file_names[int(len(file_names) * test_part):]
    write_text(data_dir / "train.txt", "\n".join(train_filenames))
    write_text(data_dir / "unused.txt", "\n".join(test_filenames))


def main():
    split(data_dir=Path("data/3_pseudolabeled"),
          test_part=.1  # we leave 10% of data for test
          )
    split(data_dir=Path("data/9a_corrected"), test_part=.1)
    split(data_dir=Path("data/10_filtered_no_correction"), test_part=0)


if __name__ == "__main__":
    main()
