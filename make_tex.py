import mysql.connector
import sys
import os
import shutil
import re

mydb = mysql.connector.connect(
    host="localhost",
    user="william",
    password="FRandBOD",
    #user="global",
    #password="global2020",
    database="doc_automation"
    )

mycursor = mydb.cursor()

#caseno = "20"
caseno = str(sys.argv[1])

interest = r"\noindent\underline{Interest}\\ Further, pursuant to the provisions of paragraph 3, Part One of the Eighth Schedule of the Lease, you are liable to pay interest on the amounts outstanding under the Lease at the rate of four per centum (4\%) above Barclays Bank plc base rate from time to time from the date 14 days after such payment shall be due until the date of actual payment. At present, the accrued interest on the service charges arrears is \textbf{\arrears} accruing at the daily rate of \intrate. The interest calculations are set out in Annex A to this letter."

costs = r"\noindent\underline{Costs}\\ Pursuant to the provisions of paragraph 4, Part One of the Eighth Schedule you are also liable for all costs charges and expenses incurred by the Lessor in or in contemplation of any proceedings or service of any notice under Sections 146 and 147 of the Law of Property Act 1925. At the date of this letter, our client’s legal fees and disbursements amount to £367.20. Should further steps be required in connection with this matter, our client will incur further costs for which you will be liable.\vspace{3 mm} \par"

def getData():
    mycursor.execute("SELECT * FROM `lease_information` WHERE case_number = '" + caseno + "'")

    result = mycursor.fetchall()

    return result

def getTotals():
    mycursor.execute("SELECT * FROM `spreadsheet_totals` WHERE case_number = '" + caseno + "'")

    result = mycursor.fetchall()

    return result

def editLine(word):
    word = re.sub("&", "\&", word)
    word = re.sub("#", "\#", word)
    word = re.sub("}", "\}", word)
    word = re.sub("{", "\{", word)
    word = re.sub("%", "\%", word)
    #word = re.sub("$", "\$", word)
    return word


decTotals= [["arrears", 3], ["interest", 2], ["legalcosts", 7], ["total", 10]]
locTotals= [["arrears", 3], ["interest", 2], ["total", 10]]

res = getData()
totals = getTotals()
#print(res[0][40])
declaration = [["addressee", 31], ["street", 33], ["locality", 35], ["town",37], ["postcode", 39], ["dateset", 1], ["borrower", 67], ["property", 8], ["weborrower", 52], ["lessees", 53], ["address", 19],
                ["caseno", 0]]
loc = [["firstperson", 3], ["secondperson", 5], ["addressee", 41],  ["street", 43], ["locality", 45], ["town", 47], ["postcode", 49], ["dateset", 66], ["sendmethod", 53], ["property", 68], ["borrower", 67],
        ["pone", 16], ["tnumber", 63], ["propowner", 19], ["charges", 59], ["clause", 23], ["demanddate", 49], ["forfeitureOne", 60], ["forfeitureTwo", 29],
        ["forfeitureThreeOne", 69], ["forfeitureThreeTwo", 31], ["forfeitureThree", 62], ["caseno", 0]]



def content(res):
    writeDeclaration(res)
    writeLoc(res)

def writeDeclaration(res):
    lit = []
    for i in declaration:
        name = i[0]
        pos = i[1]
        new = newCommand(name, res[0][pos])
        lit.append(new)
    for i in decTotals:
        name = i[0]
        pos = i[1]
        new = newCommand(name, totals[0][pos])
        lit.append(new)
    #print(lit)
    printdeclaration(lit)

def writeLoc(res):
    lit = []
    for i in loc:
        name = i[0]
        pos = i[1]
        new = newCommand(name, res[0][pos])
        lit.append(new)
    for i in locTotals:
        name = i[0]
        pos = i[1]
        new = newCommand(name, totals[0][pos])
        lit.append(new)
    if res[0][55] == "true":
        new = newCommand("interest", interest)
        lit.append(new)
    if res[0][56] == "true":
        new = newCommand("costs", costs)
        lit.append(new)
    #print(lit)
    printloc(lit)


def newCommand(name, content):
    content = editLine(str(content))
    prefix = "\\newcommand{\\"
    postname = "}{"
    postfix = "}\n"

    lit = (prefix + name + postname + content + postfix)
    return lit






def printdeclaration(lit):
    filename = "/var/www/python/create-tex/declaration/" + caseno + "/declaration.tex"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    f = open(filename, "w")
    #lit = ["\\newcommand{\dateset}{20/2/2021}", "\\newcommand{\dateset}{20/2/2021}"]
    for i in lit:
        f.write(i)
    f.close()
    shutil.copy("/var/www/python/create-tex/declaration/dec.tex", "/var/www/python/create-tex/declaration/" + caseno)

def printloc(lit):
    filename = "/var/www/python/create-tex/loc/" + caseno + "/loc.tex"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    f = open(filename, "w")
    #lit = ["\\newcommand{\dateset}{20/2/2021}", "\\newcommand{\dateset}{20/2/2021}"]
    for i in lit:
        f.write(i)
    f.close()
    shutil.copy("/var/www/python/create-tex/loc/letterOfClaim.tex", "/var/www/python/create-tex/loc/" + caseno)

content(res)
