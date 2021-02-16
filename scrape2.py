from bs4 import BeautifulSoup
import re
import mysql.connector
from datetime import date

mydb = mysql.connector.connect(
    host="localhost",
    user="global",
    password="global2020",
    database="doc_automation"
    )

today = date.today()

mycursor = mydb.cursor()

class tables:
    rows = []

    def __init__(self, url):
        self.url = url

    def tablecount(self):
        break

    def getTables(self):
        break
