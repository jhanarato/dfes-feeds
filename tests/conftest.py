import pytest


@pytest.fixture
def xml_feed_one_entry():
    return """
    <?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:georss="urn:oasis:names:tc:emergency:cap:1.2"
     xmlns:dfes="http://emergency.wa.gov.au/xmlns/dfes"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#" version="2.0">
    <channel>
<title>Total Fire Ban (All Regions)</title>
<link>http://emergency.wa.gov</link>
<description />
<language>en-us</language>
<pubDate>Mon, 16 Oct 2023 08:10:56 GMT</pubDate>
<lastBuildDate>Mon, 16 Oct 2023 08:10:56 GMT</lastBuildDate>
<docs>http://blogs.law.harvard.edu/tech/rss</docs>
<generator>Whispir RSS Engine</generator>
<managingEditor>no-reply@whispir.com</managingEditor>
<webMaster>no-reply@whispir.com</webMaster>
<ttl>1</ttl>
<item>
<title>Total Fire Ban advice for 16 October 2023 </title>
<link>https://www.emergency.wa.gov.au/#totalfirebans</link>
<description><![CDATA[This is where the summary goes]]></description>
<dfes:publicationTime>15/10/23 08:08 AM</dfes:publicationTime>
<pubDate>Sun, 15 Oct 2023 08:08:08 GMT</pubDate>
<guid>878860094</guid>
<geo:long />
<geo:lat />
</item>
</channel>
</rss>
    """


@pytest.fixture
def xml_feed_no_entry():
    return """
<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:georss="urn:oasis:names:tc:emergency:cap:1.2" xmlns:dfes="http://emergency.wa.gov.au/xmlns/dfes" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#" version="2.0">
    <channel>
        <title>Total Fire Ban (All Regions)</title>
        <link>http://emergency.wa.gov</link>
        <description />
        <language>en-us</language>
        <pubDate>Sat, 14 Oct 2023 18:16:26 GMT</pubDate>
        <lastBuildDate>Sat, 14 Oct 2023 18:16:26 GMT</lastBuildDate>
        <docs>http://blogs.law.harvard.edu/tech/rss</docs>
        <generator>Whispir RSS Engine</generator>
        <managingEditor>no-reply@whispir.com</managingEditor>
        <webMaster>no-reply@whispir.com</webMaster>
        <ttl>1</ttl>
    </channel>
</rss>    
    """
