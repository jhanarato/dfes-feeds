from dfes.fire_bans import rss_url


def test_get_fire_ban_rss_url():
    assert rss_url() == "https://www.emergency.wa.gov.au/data/message_TFB.rss"
