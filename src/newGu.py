f = open ("./tw.csv","r")
tw = f.read()
f.close()

f = open ("./two.csv","r")
two = f.read()
f.close()

tw = "tw = " + tw
two = "two = " + two

f = open('./strong.gu','w')
f.write(tw + '\n' + two)
f.close()

