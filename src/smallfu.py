from PyDbLite import Base
import datetime
today = datetime.date.today()
#impactDB = Base("F://alfStock//"+str(today)+'.yv')
#impactDB.open()
#sammi =([r for r in impactDB if r['UpOrDown']=="U"])
#print len(sammi)
#for d in sammi:
#    print d['sid']


#AintB update Current length + 1
#historyDB = Base("F://alfStock//"+"alf123"+'.history')

#historyDB.create('sid','Edate', 'lenth')
#historyDB.open()

#A-B History: sid date length
#currentDB = Base("F://alfStock//"+"alf123"+'.current')

#currentDB.create('sid','Edate', 'lenth')
#currentDB.open()

#B-A insert Current: sid date length

def resetHisDB():
    historyDB = Base("F://alfStock//"+"alf123"+'.history')
    historyDB.create('sid','Edate', 'length')#Edate := started day not end day
    historyDB.open()
    historyDB.commit()
    currentDB = Base("F://alfStock//"+"alf123"+'.current')
    currentDB.create('sid','Edate', 'length')
    currentDB.open()
    currentDB.commit()

def UpStill(entry):
    record = [r for r in currentDB if r['sid'] == entry['sid']]
    if len(r)>0:
        k = record['length']
        currentDB.update(record,length=k+1)
