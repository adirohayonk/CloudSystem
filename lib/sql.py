import mysql.connector

class DbController:
    """
        init creates the db pointer using connect_to_db function
        and create the cursor pointer
        Args:
            hostname (string): the hostname for the mysql server
            username (string): the username for the mysql server
            password (string): the password for the mysql server
            database (string): the database that should be used

    """
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
                  "hosts(hostname, ipaddr, totalMem, CPUnum)" \
                  "VALUES (%s, %s, %s, %s, %s)"
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
        sql = "UPDATE hosts SET {} = %s WHERE hostname = %s".format(field)
        self.cursor.execute(sql,(fieldContent,host))
        self.commit_to_db()

    def get_host_data(self, host, field):
        sql = "SELECT {} from hosts WHERE hostname = %s".format(field)
        self.cursor.execute(sql,(host, ))
        hostData = self.cursor.fetchone()
        return hostData

if(__name__== "__main__"):
    main()
