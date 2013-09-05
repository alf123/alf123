# -*- coding: utf-8 -*-
import math, socket
from configobj import ConfigObj
from lxml.html import tostring, fromstring, fragment_fromstring
#from lxml.cssselect import CSSSelector
import urllib2, datetime
#response = urllib2.urlopen('http://finance.yahoo.com/q?s=2002.tw&ql=1')
#data = response.read()
##print data
#html = fromstring(data)
#realTime = html.xpath("//span[@class='time_rtq_ticker']")[0].text_content().encode('utf-8').strip()
#company = html.xpath("//div[@class='title']")[0].text_content().encode('utf-8').strip()
#print realTime, company

#http://finance.yahoo.com/q/hp?s=2480.TW+Historical+Prices

class alf123:
    def __init__(self, sID, onePiece):
        self.sID = sID
        self.opp = onePiece
        self.sCurrent = self.stockCurrent()
        self.history = self.stockHistoryGet()

    def TTLUrlOpen(self, url, rc):
        retryCount = rc
        if retryCount > 2:
            print "pass"
            pass
        else:
            try:
                response = urllib2.urlopen(url, None, 120)
            except urllib2.HTTPError:
                    print "------------------------------------HTTPError!------------------------------------"
            except urllib2.URLError:
                    print "------------------------------------Bad url!------------------------------------"                    
            except socket.timeout:
                    print "------------------------------------ALF123: Timed out!------------------------------------"                    
                    response = TTLUrlOpen(self, url, retryCount+1)
        return response


    def stockCurrent(self):
        if self.opp == "TW":
            #response = urllib2.urlopen('http://finance.yahoo.com/q?s=' + self.sID + '.tw&ql=1')
            response = self.TTLUrlOpen('http://finance.yahoo.com/q?s=' + self.sID + '.tw&ql=1', 1)
        else:
            #response = urllib2.urlopen('http://finance.yahoo.com/q?s=' + self.sID + '.two&ql=1')
            response = self.TTLUrlOpen('http://finance.yahoo.com/q?s=' + self.sID + '.two&ql=1', 1)
        data = response.read()
        html = fromstring(data)
        realTime = html.xpath("//span[@class='time_rtq_ticker']")[0].text_content().encode('utf-8').strip()
        company = html.xpath("//div[@class='title']")[0].text_content().encode('utf-8').strip()
        company = company.replace("'","_")
        alf456 = '目前股價'.decode('utf8').encode('big5')
        print "stock_"+self.sID, alf456, ": ", realTime
        
        return (realTime, company)

    def stockHistoryGet(self):
        today = datetime.date.today()
        if self.opp == "TW":
            response2 = self.TTLUrlOpen('http://finance.yahoo.com/q/hp?s=' + self.sID + '.TW&a=00&b=5&c=2000&d='+str(today.month)+'&e='+str(today.day)+'&f=2013&g=d', 1)
        else:
            response2 = self.TTLUrlOpen('http://finance.yahoo.com/q/hp?s=' + self.sID + '.TWO&a=00&b=5&c=2000&d='+str(today.month)+'&e='+str(today.day)+'&f=2013&g=d', 1)
        data2 = response2.read()
        html2 = fromstring(data2)
        rows = html2.xpath("//table[@class='yfnc_datamodoutline1']//table//tr")[1:-1]
        ALFhistory = list()
        for row in rows:
            history = list()
            entries = row.xpath(".//td")
            for entry in entries:
                history.append(entry.text_content())
            if len(history)>4:
                ALFhistory.append( float(history[4]) )
            else:
                print self.sID, history
        return ALFhistory
    def stockHistory(self, days):

        print "stock_"+self.sID, " history: ", self.history[:days]
        return self.history[:days]


    def average(self, s):
        if len(s) > 0:
            av = sum(s) * 1.0 / len(s)
            print "stock_"+self.sID, "average: ", av
            return av
        else:
            return 0

    def std(self, s):
        avg = self.average(s)
        variance = map(lambda x: (x - avg)**2, s)
        standard_deviation = math.sqrt(self.average(variance))
        print "stock_"+ self.sID, "std: ", standard_deviation
        return standard_deviation

    #print std([5,6,29,300,60])
    def MB(self, days):
        return self.average(self.stockHistory( days))

    def MD(self, days):
        return self.std(self.stockHistory( days))

    def Up(self, conf):
        day1 = conf[0]
        day2 = conf[1]
        u = self.MB( day1) + 2* self.MD(day2)
        print "upper bound: ", u
        return u

    def Dn(self, conf):
        day1 = conf[0]
        day2 = conf[1]
        d = self.MB( day1) - 2* self.MD(day2)
        print "lower bound: ", d
        return d
   


    def test(self, lf):
        #http://finance.yahoo.com/q/ta?s=5603.TWO&t=1y&l=on&z=l&q=l&p=b&a=&c=
        print "-----------test start ---------------------------------------"
        conf = [30,30]
        conf2 = [10,10]
        st = ""
        if float(self.sCurrent[0]) > self.Up(conf) and (self.Up(conf)-self.Dn(conf))/(self.MB(conf[0])+0.00000001) < 0.1:
            if self.opp == "TW":
                st = ",['"+self.sCurrent[1] +".TW',   {v: 8000,   f: '$" + str(self.sCurrent[0])+"'},  true]"
            else:
                st = ",['"+self.sCurrent[1] +".TWO',   {v: 8000,   f: '$" + str(self.sCurrent[0])+"'},  true]"
        if float(self.sCurrent[0]) < self.Dn(conf):
            if self.opp == "TW":
                st = ",['"+self.sCurrent[1] +".TW',   {v: 8000,   f: '$" + str(self.sCurrent[0])+"'},  false]"
            else:
                 st = ",['"+self.sCurrent[1] +".TWO',   {v: 8000,   f: '$" + str(self.sCurrent[0])+"'},  false]"
        print "-----------test end-------------------------------------------"
        return st


#    history.append([c.text for c in row.getchildren()])
#    for row in data[4:]:
#        print(row)
#tableID = "tblStockInfo"
#stab = html.get_element_by_id(tableID)
#selAnchor = CSSSelector('tr')
#foundElements = selAnchor(stab)
#print len(foundElements)
#for d in [e for e in foundElements]:
#    print d.text_content().encode('utf-8').strip()

import os, time
def main():
    httpdoc = "C:\\Program Files (x86)\\LightTPD\\htdocs\\"
    h = "alfhead.cind"
    e = "alfend.cind"
    fh = open(httpdoc +h, "rb")
    fe = open(httpdoc +e, "rb")
    alf456 = 0
    title = fh.read()
    tail = fe.read()
    config = ConfigObj("strong.gu")
    d = config["tw"]
    e = config["two"]
    alfs = []
    for cindy in d:
        alfs.append(alf123(cindy, "TW"))
    for cindy2 in e:
        alfs.append(alf123(cindy2, "TWO"))
    while (1):
        logfile = open(httpdoc +'indexALF.html', 'w')
        logfile.write(title)

        for alf in alfs:
            st = alf.test(logfile)
            #print st
            logfile.write(st)

        logfile.write(tail)
        logfile.close()
        logfile2 = open(httpdoc +'indexALF.html', 'r')
        homepage = open(httpdoc +'index.html', 'w')
        homepage.write(logfile2.read().replace("[,[", "[["))
        homepage.close()
        logfile2.close()
        alf456 = alf456 + 1
        print 'Yahoo has been attacked ' + str(alf456) + " times!!!"
        time.sleep(60)
if __name__ == "__main__":
    main()
