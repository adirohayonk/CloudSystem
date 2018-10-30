#!/usr/bin/python

import mysql.connector

mydb = mysql.connector.connect(
    host="192.168.1.20",
    user="man",
    passwd="p"
)
print(mydb)
