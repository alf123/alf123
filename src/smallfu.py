from PyDbLite import Base
import datetime
today = datetime.date.today()
impactDB = Base("F://alfStock//"+str(today)+'.yv')
impactDB.open()
sammi =([r for r in impactDB if r['UpOrDown']=="U"])

for d in sammi:
    print d['sid']