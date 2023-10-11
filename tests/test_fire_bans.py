from dfes.fire_bans import fire_bans


def test_get_feed_title():
    fire_ban_contents = fire_bans()
    assert fire_ban_contents['feed']['title'] == "Total Fire Ban (All Regions)"
