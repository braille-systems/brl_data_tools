import json
from pathlib import Path

from scripts.preprocess_text import read_text


def inspect_json(json_file_name: Path, txt_for_aln_file_name: Path):
    with open(str(json_file_name)) as json_file:
        json_content = json.load(json_file)
    text = read_text(txt_for_aln_file_name).strip()
    labels = [shape["label"] if shape["label"] is not None else "■" for shape in json_content["shapes"]]
    formatted_text = text.replace(" ", "")
    formatted_labels = "".join(labels).replace("##", "]")\
        .replace("()", "|")\
        .replace("XX", "")
    match = len(formatted_text) == len(formatted_labels)
    # 3x TODO:
    # 1. Somehow insert markout signs in text files (from within Angeliona when `save_dev`=True  or merge TXT+JSON)
    # 2. Find out why in JSON each brace is two braces: ()
    # 3. Find out why there are some caps signs omitted in TXT
    if not match:
        print("{} {}".format(len(formatted_text), formatted_text))
        print("{} {}".format(len(formatted_labels), formatted_labels))
    return match


def main():
    json_dir = Path("data/3_pseudolabeled")
    txt_dir = Path("data/6_for_alignment")
    n_matches = n_mismatches = 0
    for json_file_name in json_dir.rglob("*.labeled.json"):
        txt_file_name = txt_dir / (json_file_name.stem.replace(".labeled", ".query") + ".txt")
        if inspect_json(json_file_name, txt_file_name):
            n_matches += 1
        else:
            n_mismatches += 1
    print("matches: {}".format(n_matches))
    print("mismatches: {}".format(n_mismatches))


if __name__ == "__main__":
    main()
