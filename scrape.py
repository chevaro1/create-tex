from bs4 import BeautifulSoup
import re
import mysql.connector
from datetime import date
# import urllib2

mydb = mysql.connector.connect(
    host="localhost",
    user="global",
    password="global2020",
    database="doc_automation"
    )

today = date.today()

mycursor = mydb.cursor()

url = "/home/william/Documents/greg project documents/statements/5fd79fa9c0073/5fd79fa9c0073s.html"
page = open(url)
p = BeautifulSoup(page.read(),features="lxml")

texts = [str.strip(x) for x in p.strings if str.strip(x) != '']
#print(texts)

results = []


for i in texts:
    if "Opening balance" in i:
        index = texts.index(i)
        texts = texts[index+2:]
        print(texts)
        break

for i in texts:
    if "Date" in i:
        index = texts.index(i)
        texts = texts[:index]
        print(texts)
        break
#print(texts)
textsDup = texts.copy()
dateslist = []
for i in texts:
    x = re.search("^[0-3][0-9]-[a-zA-Z]{3}-[0-9][0-9]$", i)
    if x:
        #print("Found a Date! " + i)
        dateslist.append(texts.index(i))
        pos = texts.index(i)
        texts[pos]= "done"

#print(dateslist)
rowsfinal=[]
def getRows():
    rows = []
    count = 0
    for i in dateslist:
        if count+1 >= len(dateslist):
            rows.append(textsDup[i:])
            #print("found end of dates")
        else:
            pos = dateslist[count+1]
            #print("row in texts = ")
            #print(textsDup[i:pos])
            rows.append(textsDup[i:pos])
        #print(dateslist[count+1] -1)
        #print(rows[count])
        count +=1
    #print(textsDup)



    for i in rows:
        date = i[0]
        length = len(i)
        count = 4
        if length > 4:
            #print(i)
            rowsfinal.append(i[:count])
            while count < length:
                #print("adding extra rows")
                temp = []
                temp.append(date)
                final = temp + i[count:count+3]
                rowsfinal.append(final)
                count += 3
        else:
            rowsfinal.append(i)


def editPrice(val):
    val = re.sub('[,£\s]', '', val)
    return val

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
index = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12",]
def editDate(date):
    x = date.split("-")
    x[2] = "20" + x[2]
    for i in months:
        if x[1] in i:
            pos = months.index(i)
            x[1] = index[pos]
    temp = [x[2], x[1], x[0]]
    res = '-'.join(temp)
    return res


def insertdb(row):
    caseno = 991122
    sql = "INSERT INTO sheet (case_number, created, start_date, value) VALUES (%s, %s, %s, %s)"
    val = (caseno, today, row[0], row[3])

    mycursor.execute(sql,val)


    mydb.commit()
getRows()
#print(rowsfinal)

for i in rowsfinal:
    i[3] = editPrice(i[3])
    i[0] = editDate(i[0])
    insertdb(i)
    print(i)
