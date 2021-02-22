import mysql.connector


mydb = mysql.connector.connect(
    host="localhost",
    user="global",
    password="global2020",
    database="doc_automation"
    )

mycursor = mydb.cursor()

caseno = "testing 3"


def getData():
    mycursor.execute("SELECT * FROM `lease_information` WHERE case_number = '" + caseno + "'")

    result = mycursor.fetchall()

    return result




res = getData()
#print(res[0][40])
declaration = [["addressee", 31], ["street", 33], ["locality", 35], ["town",37], ["postcode", 39], ["dateset", 1], ["borrower", 3], ["property", 8], ["weborrower", 52], ["lessees", 53], ["address", 19],
                ["caseno", 0], ["arrears", 60], ["interest", 60], ["legalcosts", 60], ["total", 60]]
loc = [["firstperson", 3], ["secondperson", 5], ["addressee", ],  ["street", ], ["locality", ], ["town", ], ["postcode", ], ["dateset", ], ["sendmethod", ], ["property", ], ["borrower", ], ["pone", ],
        ["tnumber", ], ["propowner", ], ["charges", ], ["clause", ], ["demanddate", ], ["arrears", ], ["intrate", ], ["total", ], ["interest", ], ["costs", ]]



def content(res):
    lit = []
    for i in declaration:
        name = i[0]
        pos = i[1]
        new = newCommand(name, res[0][pos])
        lit.append(new)
    print(lit)
    printdeclaration(lit)




def newCommand(name, content):
    prefix = "\\newcommand{\\"
    postname = "}{"
    postfix = "}\n"

    lit = (prefix + name + postname + str(content) + postfix)
    return lit






def printdeclaration(lit):
    f = open("/home/william/github/create-tex/declaration.tex", "w")
    #lit = ["\\newcommand{\dateset}{20/2/2021}", "\\newcommand{\dateset}{20/2/2021}"]
    for i in lit:
        f.write(i)
    f.close()

def printloc(lit):
    f = open("/home/william/github/create-tex/loc.tex", "w")
    #lit = ["\\newcommand{\dateset}{20/2/2021}", "\\newcommand{\dateset}{20/2/2021}"]
    for i in lit:
        f.write(i)
    f.close()

content(res)
