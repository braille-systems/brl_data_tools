import copy
import json
import re
from enum import Enum
from pathlib import Path
from typing import Tuple

from scripts.preprocess_text import read_text, StringForAlignment, write_text
from scripts.needleman_wunsch import InDelSymbols


def inspect_json_content(json_content: dict, text: str) -> Tuple[str, str, bool]:
    labels = [shape["label"] if shape["label"] is not None else "■" for shape in json_content["shapes"]]
    formatted_text = text.replace(" ", "").replace(InDelSymbols.delet, "")
    formatted_labels = "".join(labels).replace("##", StringForAlignment.number_sign) \
        .replace("()", "|") \
        .replace("XX", "@")
    match = len(formatted_text) == len(formatted_labels)
    return formatted_text, formatted_labels, match


def inspect_json(json_file_name: Path, txt_for_aln_file_name: Path):
    with open(str(json_file_name)) as json_file:
        json_content = json.load(json_file)
    text = read_text(txt_for_aln_file_name).strip()
    formatted_text, formatted_labels, match = inspect_json_content(json_content, text)
    # TODO find out why there are some caps signs in TXT missing in JSON (? EN sign); now just filter these pages
    if not match:
        print(json_file_name.stem)
        print("{} {}".format(len(formatted_text), formatted_text))
        print("{} {}".format(len(formatted_labels), formatted_labels))
    return match


def find_page_no(ref: str, query: str, page_no: int) -> Tuple[str, bool]:
    page_no_str = str(page_no)
    numbers_occurences = re.finditer(StringForAlignment.number_sign_regex + "[0-9]+", query)
    for num_occurence in numbers_occurences:
        i_start = num_occurence.start()
        num_str = num_occurence.group(0)[1:]
        if num_str == page_no_str and ref[i_start:i_start + len(num_str) + 1] == InDelSymbols.ins * (len(num_str) + 1):
            new_ref = ref[:i_start] + StringForAlignment.number_sign + page_no_str + ref[i_start + len(num_str) + 1:]
            return new_ref, True
    return ref, False


class JsonCorrectionStatus(Enum):
    success = "success"
    no_not_found = "odd page, but page number not found"
    json_query_mismatch = "number of letters in query doesn't match number of letters in JSON"


def correct_json(json_content: dict, ref: str, query: str, page_no: int) -> Tuple[dict, JsonCorrectionStatus]:
    """
    Correct JSON labels with respect to alignment
    :param json_content: labels to be corrected
    :param ref: aligned reference string
    :param query: aligned query string
    :param page_no: number of page in the document (we search for it on odd pages)
    :return: modified `json_content` and status
    """
    ref = StringForAlignment.return_digits_to_text(ref, remove_number_sign=False)
    query = StringForAlignment.return_digits_to_text(query, remove_number_sign=False)

    result_json = copy.deepcopy(json_content)
    _, _, match = inspect_json_content(json_content, query)
    if not match:
        return result_json, JsonCorrectionStatus.json_query_mismatch
    if page_no % 2:
        ref, no_is_found = find_page_no(ref=ref, query=query, page_no=page_no)
        if not no_is_found:
            return result_json, JsonCorrectionStatus.no_not_found
    indices_to_remove = []
    i_label = 0
    for q_symbol, ref_symbol in zip(query, ref):
        if q_symbol in (" ", InDelSymbols.delet):
            continue
        if ref_symbol == InDelSymbols.ins:
            indices_to_remove.append(i_label)
        elif ref_symbol != q_symbol:
            new_label = ref_symbol
            if ref_symbol == StringForAlignment.number_sign:
                new_label = "##"
            result_json["shapes"][i_label]["label"] = new_label
        i_label += 1
    return result_json, JsonCorrectionStatus.success


def main():
    json_dir = Path("data/3_pseudolabeled")
    txt_dir = Path("data/6_for_alignment")
    aln_dir = Path("data/7_aligned")
    result_dir = Path("data/9a_corrected")
    rejected_dir = Path("data/9b_rejected")
    result_dir.mkdir(parents=True, exist_ok=True)
    rejected_dir.mkdir(parents=True, exist_ok=True)

    # inspect jsons
    n_matches = n_mismatches = 0
    for json_file_name in json_dir.rglob("*.labeled.json"):
        txt_file_name = txt_dir / (json_file_name.stem.replace(".labeled", ".query") + ".txt")
        if inspect_json(json_file_name, txt_file_name):
            n_matches += 1
        else:
            n_mismatches += 1
    print("matches: {}".format(n_matches))
    print("mismatches: {}".format(n_mismatches))

    # correct jsons # TODO filter by freq
    for json_file_name in json_dir.rglob("*.labeled.json"):
        aln_file_name = aln_dir / (json_file_name.stem.replace(".labeled", "") + ".txt")
        with open(str(json_file_name)) as json_file:
            json_content = json.load(json_file)
        ref, query = read_text(aln_file_name).split("\n")[:2]
        page_no = int(re.search("p[0-9]+", aln_file_name.stem).group(0)[1:])
        new_json_content, status = correct_json(json_content=json_content, ref=ref, query=query, page_no=page_no)
        out_dir = result_dir if status == JsonCorrectionStatus.success else rejected_dir
        write_text(out_dir / json_file_name.name, json.dumps(new_json_content, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
