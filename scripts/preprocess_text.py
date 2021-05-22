import re
from os import PathLike
from pathlib import Path


def read_text(filename: PathLike):
    with open(filename, encoding="UTF-8") as in_file:
        return "\n".join(in_file.readlines())


def write_text(filename: PathLike, text: str):
    with open(filename, "w", encoding="UTF-8") as out_file:
        out_file.write(text + "\n")


class OneLineString:
    """
    Basic form of string. All texts for alignment/region finding are first converted into this, then to specific forms.
    """

    def __init__(self, raw_text: str):
        no_tabs_text = re.sub("[\t\r\n]", " ", raw_text)

        # we'll denote capital sign as `^`
        # TODO maybe convert only the first match after space?
        caps_converted_text = re.sub("[A-Z]", lambda ch: "^" + ch.group(0).lower(), no_tabs_text)
        no_line_numbers_text = re.sub("\[([0-9]|[a-z])*\]", " ", caps_converted_text)

        # in Braille, dash & hyphen are the same; a dash is followed by, but not preceded by a space
        space_after_dash_text = re.sub("—", "- ", no_line_numbers_text)
        # in Braille, dots (…) are three separate dots (...)
        dots_exploded_text = re.sub("…", "...", space_after_dash_text)
        whitespace_reduced_text = re.sub(" +", " ", dots_exploded_text)
        self.text = whitespace_reduced_text


class AlphaNumericString:
    """
    A form of text for finding regions of interest and constructing vocabulary. Only alphanumeric + spaces
    """

    def __init__(self, one_line_str: OneLineString):
        self.text = "".join(ch for ch in one_line_str.text if ch.isalnum() or ch == " ")

    def dump_vocabulary(self, out_filename: PathLike):
        words = sorted(set(self.text.split()))
        write_text(out_filename, "\n".join(words))


class StringForAlignment:
    """
    A form of text for alignment. All numbers converted to number sign + letters
    """
    number_sign = "]"
    num_to_letters = {1: "a", 2: "b", 3: "c", 4: "d", 5: "e", 6: "f", 7: "g", 8: "h", 9: "i", 0: "j"}

    @staticmethod
    def to_letters(number_str: str) -> str:
        return StringForAlignment.number_sign + "".join(StringForAlignment.num_to_letters[int(ch)] for ch in number_str)

    def __init__(self, one_line_str: OneLineString):
        self.text = re.sub("\d+", lambda match: StringForAlignment.to_letters(match.group(0)), one_line_str.text)


def preprocess_ref():
    in_dir = Path("data/ref/1_gutenberg/")
    one_line_dir = Path("data/ref/2_oneline/")
    alpha_num_dir = Path("data/ref/3_alphanumeric/")
    vocab_dir = Path("data/ref/4_vocabulary")
    for_aln_dir = Path("data/ref/5_for_alignment")
    for out_dir in (one_line_dir, alpha_num_dir, vocab_dir, for_aln_dir):
        out_dir.mkdir(parents=True, exist_ok=True)

    for ref_filename in in_dir.rglob("*.txt"):
        one_line_str = OneLineString(read_text(Path(ref_filename)))
        alpha_num_str = AlphaNumericString(one_line_str)
        for_aln_str = StringForAlignment(one_line_str)

        write_text(one_line_dir / ref_filename.name, one_line_str.text)
        write_text(alpha_num_dir / ref_filename.name, alpha_num_str.text)
        alpha_num_str.dump_vocabulary(vocab_dir / ref_filename.name)
        write_text(for_aln_dir / ref_filename.name, for_aln_str.text)


def preprocess_queries():
    in_dir = Path("data/3_pseudolabeled")
    one_line_dir = Path("data/4_oneline/")
    alpha_num_dir = Path("data/5_alphanumeric/")
    for_aln_dir = Path("data/6_for_alignment")
    for out_dir in (one_line_dir, alpha_num_dir, for_aln_dir):
        out_dir.mkdir(parents=True, exist_ok=True)

    for query_filename in in_dir.rglob("*.marked.txt"):
        query_path = Path(query_filename)
        one_line_str = OneLineString(read_text(query_path))
        alpha_num_str = AlphaNumericString(one_line_str)
        for_aln_str = StringForAlignment(one_line_str)

        write_text(one_line_dir / query_filename.name, one_line_str.text)
        write_text(alpha_num_dir / query_filename.name, alpha_num_str.text)
        write_text(for_aln_dir / query_filename.name.replace(".marked", ".query"), for_aln_str.text)


def main():
    preprocess_queries()
    preprocess_ref()


if __name__ == "__main__":
    main()
