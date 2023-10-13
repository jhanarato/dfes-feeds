import feedparser
from bs4 import BeautifulSoup

# This is probably has all the information we need to extract.
html = """
<div>
<p>
<br /><span style="color: #777777;">Time of issue: 05:05 PM </span>
<br /><span style="color: #777777;">Date of issue: 02 January 2023 </span> 
</p>
<p><strong>Midwest Gascoyne Region:</strong></p>
<ul>
    <li>Carnmah - All Day</li>
    <li>Chapman Valley - All Day</li>
</ul>
</div>
"""

entries = fire_bans.entries(feedparser.parse("../tests/data/2023-01-03/message_TFB.rss"))
summary = entries[0].summary
soup = BeautifulSoup(summary, features="html.parser")

# Find the right <div> containing a <strong tag with Region: within it.
soup.findAll('strong', string='Midwest Gascoyne Region:')
