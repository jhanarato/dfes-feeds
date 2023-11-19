import requests
import responses


def test_get_a_webpage():
    responses.add(
        responses.GET,
        "https://bswa.org",
        body="<html></html>"
    )

    r = requests.get("https://bswa.org")
    assert r.text == "<html></html>"
