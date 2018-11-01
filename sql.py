#!/usr/bin/python

import mysql.connector

class DbController:
    def __init__(self,hostname,username,password,database):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.database = database
        self.mydb = self.connect_to_db(hostname, username, password, database)
        self.cursor = self.mydb.cursor()

    def connect_to_db(self,hostname, username, password, database):
        mydb = mysql.connector.connect(host=hostname,user=username,passwd=password,database=database)
        return mydb

    def insert_to_db(self, table, data):
        if table == 'hosts':
            sql = "INSERT INTO " \
                  "hosts(hostname, ipaddr, availMem, totalMem, cores, cpuUsage, memUsage)" \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        else:
            sql = "INSERT INTO " \
                  "jobs(id, fileName, filePath, outputPath) " \
                  "VALUES (%s, %s, %s, %s)"
        try:
            self.cursor.execute(sql, data)
        except:
            print("unable to execute:{}{}".format(sql,data))

    def commit_to_db(self):
        self.mydb.commit()

    def update_host(self, host, field, fieldContent):
        sql = " UPDATE hosts SET {} = %s WHERE hostname = %s".format(field)
        self.cursor.execute(sql,(fieldContent,host))
        self.commit_to_db()

    def update_host(self, host, field, fieldContent):
        sql = " UPDATE hosts SET {} = %s WHERE hostname = %s".format(field)
        self.cursor.execute(sql,(fieldContent,host))
        self.commit_to_db()

def main():
    dbCon1 = DbController("192.168.1.20", "man", "p", "cloudSystemDB")
    #dbCon1.insert_to_db("hosts",("test", "192.168.1.24", "250", "600", "1", "30", "20"))
    #dbCon1.insert_to_db("jobs",("test", "192.168.1.24", "250", "600"))
    #dbCon1.commit_to_db()
    dbCon1.cursor.execute("SELECT * FROM hosts")
    for row in dbCon1.cursor.fetchall():
        print(row)
    dbCon1.update_host("test", "totalMem", "900")
    dbCon1.cursor.execute("SELECT * FROM hosts")
    for row in dbCon1.cursor.fetchall():
        print(row)


if(__name__== "__main__"):
    main()
