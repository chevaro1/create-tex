from datetime import date
import mysql.connector
import sys



mydb = mysql.connector.connect(
    host="localhost",
    user="william",
    password="FRandBOD",
    #user="global",
    #password="global2020",
    database="doc_automation"
    )

mycursor = mydb.cursor()
today = date.today()

#caseno = "2"
caseno = str(sys.argv[1])

def getRateChanges(start, end):
    sql = "SELECT a.date FROM interest_rate AS a WHERE a.rate <> ( SELECT b.rate FROM interest_rate AS b WHERE a.date > b.date ORDER BY b.date DESC LIMIT 1 ) AND a.date BETWEEN '" + start.strftime("%Y-%m-%d") + "' AND '" + end.strftime("%Y-%m-%d") + "'"
    mycursor.execute(sql)

    result = mycursor.fetchall()
    return result

def addRateChanges(main, extra):
    new = []

    count = 0
    while count < len(main):
        #print("iterating through dates")
        temp = []
        for i in extra:
            if main[count][3] >= i[0]:
                #print("found gap")
                #print("table date = " + main[count][3].strftime("%Y-%m-%d"))
                #print("exchange rate change date = " + i[0].strftime("%Y-%m-%d"))
                temp.append(i)
                new.append(["999", caseno, main[count][2], i[0], "0", "true"])
        for i in temp:
            extra.remove(i)
        new.append(main[count])
        count += 1

    return new


def countTables(caseno):
    sql = "SELECT DISTINCT type FROM `sheet` WHERE case_number = '" + caseno + "'"
    mycursor.execute(sql)

    result = mycursor.fetchall()

    return result

def getTable(type, caseno):
    sql = "SELECT id, case_number, type, start_date, value, interest FROM `sheet` WHERE type = '" + type + "' AND case_number = '" + caseno + "'"
    mycursor.execute(sql)

    result = mycursor.fetchall()

    extra = getRateChanges(result[0][3], today)

    result = addRateChanges(result, extra)
    #return extra
    return result

def getLeaseInfoInterest(caseno):
    sql = "SELECT interest_rate FROM `lease_information` WHERE case_number = '" + caseno + "'"
    mycursor.execute(sql)
    #notes_interest
    result = mycursor.fetchall()
    #print(result)

    return result[0][0]

def getLeaseInfoLegalCosts(caseno):
    sql = "SELECT costs_price FROM `lease_information` WHERE case_number = '" + caseno + "'"
    mycursor.execute(sql)
    #notes_interest
    result = mycursor.fetchall()
    #print(result)

    return result[0][0]


class totals:
    def __init__(self, legal, caseNo, courtCosts = 0):
        #self.type = type
        self.caseNo = caseNo
        self.service_charges = 0
        self.ground_rent = 0
        self.chargeInterest = 0
        self.groundInterest = 0
        self.legalCosts = legal
        self.dailyInterestservice = 0
        self.dailyInterestground = 0
        self.courtCosts = courtCosts
        self.total = 0

    def addCharges(self, val, type):
        #self.charges = float(val)
        if type == "service charge":
            self.service_charges = float(val)
        else:
            self.ground_rent = float(val)

    def addInterest(self, val, type):
        if type == "service charge":
            self.chargeInterest += float(val)
        else:
            self.groundInterest += float(val)

    def addDailyInterest(self, outstanding, payable, type):
        if type == "service charge":
            self.dailyInterestservice = round(float(outstanding) * payable, 2)
        else:
            self.dailyInterestground = round(float(outstanding) * payable, 2)
        #self.dailyInterest = round(float(outstanding) * payable, 2)

    def calcTotal(self):
        self.total = round(self.service_charges + self.ground_rent + self.chargeInterest + self.groundInterest + float(self.legalCosts), 2)
        #print(self.total)

    def upload(self):
        sql = "INSERT INTO `spreadsheet_totals`(`created`, `case_number`, `service_charges`, `service_charges_with_interest`, `ground_rent`, `ground_rent_with_interest`, `legal_costs`, `ground_rent_daily_interest`, `service_charges_daily_interest`, `total`, `court_issue`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (today, self.caseNo, self.service_charges, self.chargeInterest, self.ground_rent, self.groundInterest, self.legalCosts, self.dailyInterestground, self.dailyInterestservice, self.total, self.courtCosts)

        mycursor.execute(sql,val)
        mydb.commit()




class row:
    def __init__(self, id, caseNo, type, start, value, interest, end, interestRate, previousId = None, nextId = None):
        self.previousId = previousId
        self.id = id
        self.nextId = nextId
        self.caseNo = caseNo
        self.type = type
        self.start = start
        self.end = end
        self.value = value
        self.interest = interest
        #print(interest)
        if interest == "true":
            self.setInterest(interestRate)
        else:
            self.interestRate = 0
        self.setDays()
        self.setDailyInterest()
        self.interestPayable()

    def __str__(self):
        return "Row values: id= " + str(self.id) + "     caseNo= " + str(self.caseNo) + "     type= " + str(self.type) + "     start= " + str(self.start) + "     days= " + str(self.days) + "     end= " + str(self.end) + "     value= " + str(self.value) + "     interest= " + str(self.interest) + "     interestRate= " + str(self.interestRate) + "     DailyInterestRate= " + str(self.dailyInterest) + "     Interest Payable= " + str(self.interestPayable)

    def setInterest(self, rate):
        date = str(self.start)
        #x = date.split("-")
        #date = x[2] + "-" + x[1] + "-" + x[0]
        sql = "SELECT rate FROM `interest_rate` WHERE date = '" + date + "'"
        mycursor.execute(sql)
        result = mycursor.fetchall()
        boe = float(result[0][0])
        self.interestRate = int(rate) + boe

    def setDays(self):
        d = self.end - self.start
        self.days = d.days

    def setDailyInterest(self):
        x = round(((self.interestRate / 100) / 365), 15)
        if x < 0:
            x = 0
        self.dailyInterest = x

    def interestPayable(self):
        x = round((float(self.value) * self.dailyInterest * int(self.days)) ,2)
        if x < 0:
            x = 0
        self.interestPayable = x

    def getRate(self):
        return self.rate

    def upload(self):
        sql = "INSERT INTO `spreadsheet`(`created`, `case_number`, `type`, `start_Date`, `end_date`, `days`, `interest_rate`, `daily_interest`, `outstanding`, `payable`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (today, self.caseNo, self.type, self.start, self.end, self.days, self.interestRate, self.dailyInterest, self.value, self.interestPayable)

        mycursor.execute(sql,val)
        mydb.commit()




#table4 = row("12", "1", "service", "2015-11-03", 1000.00, "false", "2015-12-03", "4")
#print(table4)
#rate = table.getRate()
#print(table.interest)
#print(table.days.days)


tablecount = countTables(caseno)
rate = getLeaseInfoInterest(caseno)
legal = getLeaseInfoLegalCosts(caseno)

tables = []

for i in tablecount:
    table = []
    print("new table")
    res = getTable(i[0], caseno)
    count = 0
    while count < len(res):
        if count == (len(res) -1):
            table.append(row(res[count][0], res[count][1], res[count][2], res[count][3], res[count][4], res[count][5], today, rate))
        else:
            table.append(row(res[count][0], res[count][1], res[count][2], res[count][3], res[count][4], res[count][5], res[count+1][3], rate))
        count += 1
    tables.append(table)

tableTotals = totals(legal, caseno)

for i in tables:
    #row = []
    #row.append(totals(legal, caseno, i[0].type))
    for a in i:
        print(a)
        a.upload()
        tableTotals.addCharges(a.value, a.type)
        tableTotals.addInterest(a.interestPayable, a.type)
        tableTotals.addDailyInterest(a.value, a.dailyInterest, a.type)

tableTotals.calcTotal()
tableTotals.upload()
