import re
from pathlib import Path
from typing import Generator, Any, Dict, Sequence


def read_text(filename: Path) -> str:
    with open(str(filename), encoding="UTF-8") as in_file:
        return "".join(in_file.readlines())


def write_text(filename: Path, text: str) -> None:
    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(str(filename), "w", encoding="UTF-8") as out_file:
        out_file.write(text + "\n")


class OneLineString:
    """
    Basic form of string. All texts for alignment/region finding are first converted into this, then to specific forms.
    """

    def __init__(self, raw_text: str):
        no_tabs_text = re.sub("[\t\r\n]", " ", raw_text)

        # we'll denote capital sign as `^`
        # TODO maybe convert only the first match after space?
        caps_converted_text = re.sub("[A-Z]", lambda ch: StringForAlignment.caps_sign + ch.group(0).lower(),
                                     no_tabs_text)
        single_quotes_converted_text = re.sub(r"([^a-z])‘(.*)’([^a-z])", r"\1“\2”\3", caps_converted_text)
        apostrope_converted_text = re.sub("[‘’]", "'", single_quotes_converted_text)
        no_line_numbers_text = re.sub(r"\[([0-9]|[a-z])*" + StringForAlignment.number_sign_regex, " ",
                                      apostrope_converted_text)
        dash_converted_text = re.sub("—", "--", no_line_numbers_text)
        # in Braille, dots (…) are three separate dots (...)
        dots_exploded_text = re.sub("…", "...", dash_converted_text)
        # in Jane Eyre ampersand is always preceded by stress (') TODO do not do it in general case or create parameter
        amp_converted_text = re.sub("&", "'&", dots_exploded_text)
        whitespace_reduced_text = re.sub(" +", " ", amp_converted_text)

        special_letters_map = {
            "è": "e",
            "é": "e",
            "ê": "e",
            "ë": "e",
            "ï": "i",
            "ä": "a",
            "â": "a",
            "à": "a",
            "ç": "c",
            "ô": "o",
            "œ": "ae",
            "æ": "ae",
        }
        text_no_special = "".join(
            [special_letters_map[ch] if ch in special_letters_map else ch for ch in whitespace_reduced_text])
        self.text = text_no_special


class AlphaNumericString:
    """
    A form of text for finding regions of interest and constructing vocabulary. Only alphanumeric + spaces
    """

    def __init__(self, one_line_str: OneLineString):
        filtered_characters = [(index, ch) for index, ch in enumerate(one_line_str.text) if ch.isalnum() or ch == " "]
        self.text = "".join([ch for (_, ch) in filtered_characters])
        self.indices = [idx for (idx, _) in filtered_characters]

    def dump_vocabulary(self, out_filename: Path):
        words = sorted(set(self.text.split()))
        write_text(out_filename, "\n".join(words))


class StringForAlignment:
    """
    A form of text for alignment. All numbers converted to number sign + letters
    """
    number_sign = "]"
    caps_sign = "^"
    number_sign_regex = r"\]"
    num_to_letters = {1: "a", 2: "b", 3: "c", 4: "d", 5: "e", 6: "f", 7: "g", 8: "h", 9: "i", 0: "j"}

    @classmethod
    def to_letters(cls, number_str: str) -> str:
        return cls.number_sign + "".join(cls.num_to_letters[int(ch)] for ch in number_str)

    @classmethod
    def return_digits_to_text(cls, text: str, remove_number_sign: bool) -> str:
        letters_to_num = {value: key for key, value in cls.num_to_letters.items()}

        def substitute_with_num(letters_str: str):
            result = "".join(str(letters_to_num[ch]) for ch in letters_str[1:])
            return result if remove_number_sign else StringForAlignment.number_sign + result

        return re.sub(cls.number_sign_regex + "[a-j]*", lambda match: substitute_with_num(match.group(0)), text)

    def __init__(self, one_line_str: OneLineString):
        self.text = re.sub(r"\d+", lambda match: StringForAlignment.to_letters(match.group(0)), one_line_str.text). \
            replace("«", "“").replace("»", "”")


def calc_queries_stats(queries_file_names: Generator[Path, Any, Any], vocab_filename: Path) -> Dict[str, int]:
    vocabulary = set(read_text(vocab_filename).split())
    words_freq = {}
    for q_file_name in queries_file_names:
        q_file_path = Path(q_file_name)
        words = read_text(q_file_path).split()
        words_occurence_freq = len([w for w in words if w in vocabulary]) / len(words) if len(words) > 0 else 0
        words_freq[q_file_path.stem] = words_occurence_freq
    return words_freq


def calc_occurrences(queries_dir: Path, vocab_dir: Path, file_prefixes: Sequence[str], out_file_postfix: str) -> None:
    words_freq = {}
    for file_prefix in file_prefixes:
        words_freq.update(calc_queries_stats(queries_dir.rglob(file_prefix + "_*.txt"),
                                             vocab_dir / "{}.txt".format(file_prefix)))
    with open(str(vocab_dir / "word_freq_stats{}.csv".format(out_file_postfix)), "w", encoding="UTF-8") as out_file:
        for page_name, freq in words_freq.items():
            out_file.write("{}, {}\n".format(page_name, freq))


def preprocess_ref(vocab_dir: Path):
    in_dir = Path("data/ref/1_gutenberg/")
    one_line_dir = Path("data/ref/2_oneline/")
    alpha_num_dir = Path("data/ref/3_alphanumeric/")
    for_aln_dir = Path("data/ref/5_for_alignment")
    for out_dir in (one_line_dir, alpha_num_dir, vocab_dir, for_aln_dir):
        out_dir.mkdir(parents=True, exist_ok=True)

    for ref_filename in in_dir.rglob("*.txt"):
        one_line_str = OneLineString(read_text(Path(ref_filename)))
        alpha_num_str = AlphaNumericString(one_line_str)
        for_aln_str = StringForAlignment(one_line_str)

        write_text(one_line_dir / ref_filename.name, one_line_str.text)
        write_text(alpha_num_dir / ref_filename.name, alpha_num_str.text)
        write_text(alpha_num_dir / (ref_filename.stem + ".indices.txt"),
                   " ".join([str(idx) for idx in alpha_num_str.indices]))

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
    vocab_dir = Path("data/ref/4_vocabulary")
    preprocess_queries()
    preprocess_ref(vocab_dir=vocab_dir)
    calc_occurrences(queries_dir=Path("data/5_alphanumeric"), vocab_dir=vocab_dir,
                     file_prefixes=("scarlet_letter", "jane_eyre"), out_file_postfix="")


if __name__ == "__main__":
    main()
