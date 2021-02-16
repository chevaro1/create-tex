import mysql.connector


mydb = mysql.connector.connect(
    host="localhost",
    user="global",
    password="global2020",
    database="doc_automation"
    )

mycursor = mydb.cursor()

caseno = "123"
lit = []

def getData():
    mycursor.execute("SELECT * FROM `lease_information` WHERE case_number = '" + caseno + "'")

    result = mycursor.fetchall()

    return result




res = getData()
print(res[0][0])
commands = ["addressee", "street", "locality", "town", "postcode", "dateset", "borrower", "property", "weborrower", "leessees", "address", "caseno"]


def content(res):
    return

def newCommand(name, content):
    prefix = "\\newcommand{\\"
    postname = "}{"
    postfix = "}\n"

    lit.append(prefix + name + postname + content + postfix)


f = open("/home/william/github/create-tex/testing.tex", "w")
#lit = ["\\newcommand{\dateset}{20/2/2021}", "\\newcommand{\dateset}{20/2/2021}"]
for i in lit:
    f.write(i)
f.close()
