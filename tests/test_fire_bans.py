from dfes.fire_bans import feed_title


def test_get_feed_title():
    test_data = "data/2023-01-03/message_TFB.rss"
    assert feed_title(test_data) == "Total Fire Ban (All Regions)"
