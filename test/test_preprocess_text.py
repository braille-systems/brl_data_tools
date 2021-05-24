from pathlib import Path

from scripts.preprocess_text import OneLineString, read_text, AlphaNumericString, StringForAlignment


def test_oneline_string():
    for input_str, expected_output in (
            ("   ", " "),
            ("  [123]  ", " "),
            ("  [123] AaXz  ", " ^aa^xz "),
            ("  [123] \t \n\r AaXz\n\r  ", " ^aa^xz "),
            ("  [123] \t \n\r AaXz\n\r [ivv]123  ", " ^aa^xz 123 "),
    ):
        assert OneLineString(input_str).text == expected_output

    in_string = read_text(Path("data/ref/ref_short.txt"))
    out_string = OneLineString(in_string).text
    for char in "\t\n":
        assert char in in_string
        assert char not in out_string
    assert not in_string.islower()
    assert out_string.islower()


def test_alphanumeric_string():
    assert AlphaNumericString(OneLineString("^abc... ^def? 123")).text == "abc def 123"


def test_string_for_alignment():
    assert StringForAlignment.to_letters("901") == "]ija"
    assert StringForAlignment(OneLineString("^abc 123 456")).text == "^abc ]abc ]def"
    assert StringForAlignment.return_digits_to_text("]abc", remove_number_sign=True) == "123"
    assert StringForAlignment.return_digits_to_text("]ab cd ]ef", remove_number_sign=True) == "12 cd 56"
    assert StringForAlignment.return_digits_to_text("]ab cd ]efgh.j", remove_number_sign=False) == "]12 cd ]5678.j"
