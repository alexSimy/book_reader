import os


def test_write_to_file_creates_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from src.utils.file_utils import write_to_file

    ok = write_to_file('testidx', 'hello')
    assert ok is True
    out = tmp_path / 'output' / 'testidx_summary.txt'
    assert out.exists()
    assert out.read_text(encoding='utf-8') == 'hello'
