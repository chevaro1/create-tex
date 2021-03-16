from bs4 import BeautifulSoup
import re
import mysql.connector
from datetime import date
import numpy as np
import sys

mydb = mysql.connector.connect(
    host="localhost",
    user="william",
    password="FRandBOD",
    #user="global",
    #password="global2020",
    database="doc_automation"
    )

today = date.today()

mycursor = mydb.cursor()

def getFile(url):
    page = open(url)
    p = BeautifulSoup(page.read(),features="lxml")


    texts = [str.strip(x) for x in p.strings if str.strip(x) != '']

    return texts

results = []

def getTable(texts):
    for i in texts:
        if "Opening balance" in i:
            index = texts.index(i)
            texts = texts[index+2:]
            #print(texts)
            break

    for i in texts:
        if "Closing balance" in i:
            index = texts.index(i)
            remainder = texts[index:]
            texts = texts[:index]

            break

    return texts, remainder


def findDates(texts):
    dateslist = []
    for i in texts:
        x = re.search("^[0-3][0-9]-[a-zA-Z]{3}-[0-9][0-9]$", i)
        if x:
            dateslist.append(texts.index(i))
            pos = texts.index(i)
            texts[pos]= "done"
    return texts, dateslist


def getRows(textsDup, dateslist):
    rowsfinal=[]
    rows = []
    count = 0
    for i in dateslist:
        if count+1 >= len(dateslist):
            rows.append(textsDup[i:])
        else:
            pos = dateslist[count+1]
            rows.append(textsDup[i:pos])
        count +=1


    for i in rows:
        date = i[0]
        length = len(i)
        count = 4
        if length > 4:
            rowsfinal.append(i[:count])
            while count < length:
                temp = []
                temp.append(date)
                final = temp + i[count:count+3]
                rowsfinal.append(final)
                count += 3
        else:
            rowsfinal.append(i)
    return rowsfinal


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


def insertdb(row, type, caseno):
    #caseno = 991122
    sql = "INSERT INTO sheet (case_number, created, type, start_date, value, interest) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (caseno, today, type, row[0], row[3], "false")

    mycursor.execute(sql,val)


    mydb.commit()


def cleanTable(tables):

    count = 0
    tableno = len(tables)
    while count < tableno:
        count2 = 0
        while count2 < len(tables[count]):
            if "Date" in tables[count][count2]:
                if "Description" in tables[count][count2]:
                    if "Demands" in tables[count][count2]:
                        tables[count].remove(tables[count][count2])

            if "Receipts" in tables[count][count2]:
                if "Balance" in tables[count][count2]:
                    tables[count].remove(tables[count][count2])

            count2 += 1
        count += 1
    return tables


def tablecount(texts):
    count = 0
    for i in texts:
        if "Opening balance" in i:
            count = count + 1
    return count

def getType(table):
    #print("getting type")
    for i in table:
        #print(i)
        if "Service charge" in i[1]:
            #print("service charge table found")
            return "service charge"
        if "ground rent" in i[1]:
            #print("ground rent table found")
            return "ground rent"

def run(url, caseno):
    texts = getFile(url)
    count = tablecount(texts)

    tables = []

    for i in range(count):
        texts, remainder = getTable(texts)
        textsDup = texts.copy()
        texts, dates = findDates(texts)
        tables.append(getRows(textsDup, dates))

        texts = remainder
        #print(texts)

    tables = cleanTable(tables)


    for a in tables:
        print("new table \n")
        for i in a:
            i[3] = editPrice(i[3])
            i[0] = editDate(i[0])
            #insertdb(i)
            #print(i)
        type = getType(a)
        for i in a:
            insertdb(i, type, caseno)


#url = "/home/william/github/action-automation/upload/fulltest_v1s.html"
#caseno = "fulltest_v1"
#prefix = "/home/william/Documents/greg project documents/statements/city tower/statements.html"
url = str(sys.argv[2])
caseno = str(sys.argv[1])
run(url, caseno)
