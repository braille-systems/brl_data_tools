import json
from pathlib import Path

from scripts.modify_json import detect_hyphens, find_page_no, correct_json, JsonCorrectionStatus
from scripts.preprocess_text import read_text


def test_find_page_no():
    assert find_page_no("▲▲▲▲", "]123", 123) == ("]123", True)
    assert find_page_no("abc▲▲▲▲▲ def", "abc ]123 def", 123) == ("abc▲]123 def", True)


def test_detect_hyphens():
    assert detect_hyphens("cer▲▲tain", "cer- tain") == "cer- tain"
    assert detect_hyphens("cer▲▲tain▲▲ly", "cer- tainnnly") == "cer- tain▲▲ly"


def test_correct_json():
    with open("data/modify_json/labels.json") as json_file:
        json_content = json.load(json_file)
    (ref, query), page_no = read_text(Path("data/modify_json/alignment_p14.txt")).split("\n")[:2], 14
    corrected_json, status = correct_json(json_content=json_content, ref=ref, query=query, page_no=page_no)
    assert status == JsonCorrectionStatus.success
    assert "".join([shape["label"] if shape["label"] is not None else "■" for shape in corrected_json["shapes"]]) \
           == "CCb-##14nana"
