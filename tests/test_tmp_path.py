import pytest


@pytest.fixture
def path_a(tmp_path):
    return tmp_path


@pytest.fixture
def path_b(tmp_path):
    return tmp_path


def test_tmp_path_is_same(tmp_path, path_a, path_b):
    assert tmp_path == path_a
    assert tmp_path == path_b
