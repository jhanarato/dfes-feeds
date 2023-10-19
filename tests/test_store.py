from dfes import store


def test_file_name():
    assert store.file_name(None) == "total_fire_bans_issued_2023_01_02_1305.rss"
