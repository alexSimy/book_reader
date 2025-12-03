import os

def test_write_to_file_creates_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from src.utils.file_utils import write_to_file

    file_path = write_to_file('testidx', 'hello', base_dir=tmp_path / "test - output")
    assert file_path is not None

    assert os.path.exists(file_path)
    assert open(file_path, encoding='utf-8').read() == 'hello'
