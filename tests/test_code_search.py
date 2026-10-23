from repomedic.code_search import search_symbol
from repomedic.source_reader import read_source_context


def test_search_ast_and_exclusions(tmp_path):
    (tmp_path / "a.py").write_text("async def target():\n    pass\nclass target:\n    pass\n", encoding="utf-8")
    (tmp_path / "broken.py").write_text("def broken(", encoding="utf-8")
    ignored = tmp_path / ".venv"
    ignored.mkdir()
    (ignored / "x.py").write_text("def target(): pass", encoding="utf-8")
    results = search_symbol(tmp_path, "target")
    assert {item["kind"] for item in results} == {"async_function", "class"}
    assert len(search_symbol(tmp_path, "target", max_results=1)) == 1


def test_reader_rejects_large_and_invalid_encoding(tmp_path):
    path = tmp_path / "large.py"
    path.write_bytes(b"x" * (1024 * 1024 + 1))
    assert read_source_context(str(tmp_path), "large.py", 1) is None
    path.write_bytes(b"\xff\xfe")
    assert read_source_context(str(tmp_path), "large.py", 1) is None
