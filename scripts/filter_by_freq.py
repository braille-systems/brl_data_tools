from pathlib import Path
from shutil import copy

from scripts.preprocess_text import read_text

from scripts.postprocess_text import read_csv_stats


def main():
    out_dir = Path("data/10_filtered_no_correction")
    out_dir.mkdir(parents=True, exist_ok=True)
    frequencies = read_csv_stats(Path("data/ref/4_vocabulary/word_freq_stats.csv"))
    dataset_size = len(read_text(Path("data/9a_corrected/train.txt")).split())
    freq_thresh = sorted(frequencies.values(), reverse=True)[dataset_size - 1]
    print("threshold: {}".format(freq_thresh))
    for jpg_filename in Path("data/3_pseudolabeled").rglob("*.labeled.jpg"):
        if frequencies[jpg_filename.stem.replace(".labeled", ".marked")] >= freq_thresh:
            copy(str(jpg_filename), out_dir)
            copy(str(jpg_filename.with_suffix(".json")), out_dir)


if __name__ == "__main__":
    main()
