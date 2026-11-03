from lumenpath.progress import Progress


def test_record_keeps_the_best(tmp_path):
    progress = Progress(tmp_path / "p.json")
    assert progress.record("01", 5)
    assert not progress.record("01", 7)
    assert progress.record("01", 3)
    assert progress.best == {"01": 3}


def test_save_and_load(tmp_path):
    path = tmp_path / "deep" / "progress.json"
    progress = Progress(path)
    progress.record("01", 2)
    progress.save()
    assert Progress.load(path).best == {"01": 2}


def test_damaged_or_missing_file_starts_fresh(tmp_path):
    assert Progress.load(tmp_path / "missing.json").best == {}
    broken = tmp_path / "broken.json"
    for content in ("{not json", "[1, 2]", '{"best": {"01": "lots"}}', '{"best": 5}'):
        broken.write_text(content, encoding="utf-8")
        assert Progress.load(broken).best == {}


def test_first_unsolved():
    progress = Progress(None)
    ids = ["01", "02", "03"]
    assert progress.first_unsolved(ids) == 0
    progress.record("01", 1)
    assert progress.first_unsolved(ids) == 1
    progress.record("02", 1)
    progress.record("03", 1)
    assert progress.first_unsolved(ids) == 2


def test_no_path_means_no_saving():
    Progress(None).save()  # must not raise
