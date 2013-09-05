
from lxml.html import tostring, fromstring, fragment_fromstring
#from lxml.cssselect import CSSSelector
import urllib2
response = urllib2.urlopen('http://finance.yahoo.com/q?s=2489.tw&ql=1')#('http://finance.yahoo.com/q?s=2002.tw&ql=1')
data = response.read()
html = fromstring(data)
tableID = "title"
title = html.xpath("//div[@class='title']")[0].text_content().encode('utf-8').strip()
current = html.xpath("//span[@class='time_rtq_ticker']")[0].text_content().encode('utf-8').strip()
print title, current


response2 = urllib2.urlopen('http://finance.yahoo.com/q/hp?s=2002.TW+Historical+Prices')#('http://finance.yahoo.com/q?s=2002.tw&ql=1')
data2 = response2.read()
html2 = fromstring(data2)
rows = html2.xpath("//table[@class=yfnc_datamodoutline1]")[0].findall("tr")
data = list()
for row in rows:
    data.append([c.text for c in row.getchildren()])
for row in data[4:]: print(row)
