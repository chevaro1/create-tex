

newlist = []

def edit(line):
    if "INSERT" in line:
        #print(line)
        newlist.append(line.rstrip())
        return

    x = line.split()
    #print(x)
    date = x[1][1:-2]

    y = date.split("-")
    newdate = y[2] + "-" + y[1] + "-" + y[0]

    newline = x[0] + " '" + newdate + "', " + x[2]

    #print(newline)
    newlist.append(newline)







file = open("/home/william/github/create-tex/dates.txt", "r")
#print(file.readline())
for line in file:
    #print(line)
    edit(line)

with open('/home/william/github/create-tex/new_dates.txt', 'w') as f:
    for item in newlist:
        f.write("%s\n" % item)
