from dfes.fire_danger import feed_title


def test_should_get_title():
    test_data = "data/2023-01-03/message_FDR.rss"
    assert feed_title(test_data) == "Fire Danger Ratings (All Regions)"
