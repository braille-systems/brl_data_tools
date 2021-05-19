from pathlib import Path

from scripts.rename import rename_pages


def test_rename_jpg():
    out_dir = Path("data/out/renamed")
    rename_pages(in_dir=Path("data/raw"),
                 out_dir=out_dir,
                 start_num=1)
    results = [filename.name for filename in Path.rglob(out_dir, "*.*")]
    assert sorted(results) == ["p0001.JPG", "p0002.JPG", "p0003.JPG"]
