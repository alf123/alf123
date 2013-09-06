# -*- coding: utf-8 -*-
import math, socket
from PyDbLite import Base
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
        today = datetime.date.today()
        self.sID = sID
        self.opp = onePiece
        self.historyDB = Base("F://alfStock//"+"alf123"+'.history')
        self.currentDB = Base("F://alfStock//"+"alf123"+'.current')
        self.historyDB.open()
        self.currentDB.open()
        db = Base("F://alfStock//"+str(today)+'.db')
        impactDB = Base("F://alfStock//"+str(today)+'.yv')
        if db.exists():
            db.open()

            recs = [ r for r in db if r['sid'] == self.sID ]
            if len(recs) > 0:

                self.history = recs[0]['history']
                self.sCurrent = recs[0]['current']
            else:
                print "already existed:  ", len(db)
                self.insertHistory(db)
        else:
            db.create('sid','history', 'current')
            self.insertHistory(db)

        if impactDB.exists():
            self.idb = impactDB
        else:
            impactDB.create('sid','UpOrDown')# U:up; D:down
            impactDB.open()
            impactDB.commit()
            self.idb = impactDB

    def insertHistory(self, db):
            db.open()
            self.history = self.stockHistoryGet()
            self.sCurrent = self.stockCurrent()
            db.insert(sid = self.sID, history = self.history, current = self.sCurrent)
            db.commit()

    def TTLUrlOpen(self, url, rc):
        retryCount = rc
        if retryCount > 2:
            pass
        else:
            try:
                response = urllib2.urlopen(url, None, 2.5)
            except URLError, e:
                    print "url"
            except socket.timeout:
                    print "Timed out!"
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
        print "alf123:              ", realTime, company
        return (realTime, company)

    def stockHistoryGet(self):
        today = datetime.date.today()
        if self.opp == "TW":
            response2 = urllib2.urlopen('http://finance.yahoo.com/q/hp?s=' + self.sID + '.TW&a=00&b=5&c=2000&d='+str(today.month)+'&e='+str(today.day)+'&f=2013&g=d')
        else:
            response2 = urllib2.urlopen('http://finance.yahoo.com/q/hp?s=' + self.sID + '.TWO&a=00&b=5&c=2000&d='+str(today.month)+'&e='+str(today.day)+'&f=2013&g=d')
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
    def insertIDB(self, UpOrDown):
        self.idb.open()
        k = [r for r in self.idb if r['sid'] == self.sID]
        if len(k) > 0:
            pass
        else:
            self.idb.open()
            self.idb.insert(self.sID, UpOrDown)
            self.idb.commit()

    def UpStill(self):
        self.idb.open()
        existOrNot = [r for r in self.idb if r['sid']== self.sID]
        leng = 0
        if len(existOrNot)>0:
            pass
        else:
            record = [r for r in self.currentDB if r['sid'] == self.sID]
            if len(record)>0:
                k = record[0]['length']
                leng = k+1
                self.currentDB.update(record[0],length=leng)
                self.currentDB.commit()
            else:
                leng = 1
                self.currentDB.insert(sid = self.sID,Edate = datetime.date.today(),length=leng)
                self.currentDB.commit()
        return leng
    def DownStill(self):
        record = [r for r in self.currentDB if r['sid'] == self.sID]
        if len(record)>0:
            self.historyDB.insert(sid = self.sID, Edate = record[0]['Edate'], length = record[0]['length'])
            self.historyDB.commit()
            self.currentDB.delete(record[0])
            self.currentDB.commit()
    def test(self, lf):
        #http://finance.yahoo.com/q/ta?s=5603.TWO&t=1y&l=on&z=l&q=l&p=b&a=&c=
        print "-----------test start ---------------------------------------"
        conf = [30,30]
        conf2 = [10,10]
        st = ""
        if (float(self.sCurrent[0]) > self.Up(conf)) and ( (self.Up(conf)-self.Dn(conf))/(self.MB(conf[0])+0.00000001) < 0.1):
            fuNum = self.UpStill()
            if self.opp == "TW":
                st = ",['"+self.sCurrent[1] +".TW',   {v: 8000,   f: '$" + str(self.sCurrent[0])+"'},  "+str(fuNum)+"]"
                self.insertIDB("U")
            else:
                st = ",['"+self.sCurrent[1] +".TWO',   {v: 8000,   f: '$" + str(self.sCurrent[0])+"'},  "+str(fuNum)+"]"
                self.insertIDB("U")
        if float(self.sCurrent[0]) < self.Dn(conf):
            self.DownStill()
            if self.opp == "TW":
                st = ""#",['"+self.sCurrent[1] +".TW',   {v: 8000,   f: '$" + str(self.sCurrent[0])+"'},  false]"
                self.insertIDB("D")
            else:
                 st = ""#",['"+self.sCurrent[1] +".TWO',   {v: 8000,   f: '$" + str(self.sCurrent[0])+"'},  false]"
                 self.insertIDB("D")
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
from configobj import ConfigObj

def setPid(pid):
    config = ConfigObj('./cindy.pid')
    config['pid'] = pid
    print pid
    config.write()

import os, time
def main():
    pid = str(os.getpid())
    setPid(pid)
    print "alfPid is: ", pid
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
        #alf456 = alf456 + 1
        print "     alf123, alf456, alf789 lalala~  "
        print "             alf123, alf456, alf789 lalala~  "
        print "                     alf123, alf456, alf789 lalala~  "
        break
if __name__ == "__main__":
    main()
