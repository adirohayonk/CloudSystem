import mysql.connector
import traceback 

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
	def __init__(self,hostname):
		self.hostname = hostname
		self.username = "man" 
		self.password = "p" 
		self.database = "cloudSystemDB"
		self.mydb = self.connect_to_db(self.hostname, self.username, self.password, self.database)
		self.mydb.autocommit = True
		self.cursor = self.mydb.cursor(buffered=True)

	def connect_to_db(self,hostname, username, password, database):
		mydb = mysql.connector.connect(host=hostname,user=username,passwd=password,database=database)
		return mydb

	def insert_to_db(self, table, data):
		if table == 'hosts':
			sql = "INSERT INTO " \
				  "hosts(hostname, ipaddr, totalMem, CPUnum)" \
				  "VALUES (%s, %s, %s, %s)"
		elif table == 'jobs':
			sql = "INSERT INTO " \
				  "jobs(jobid, fileName, hostname, status)" \
				  "VALUES (%s, %s, %s, %s)"
		try:
			self.cursor.execute(sql, data)
		except:
			print("unable to execute:{}{}".format(sql,data))
			print(traceback.format_exc())

	def update_host(self, host, field, fieldContent):
		print("host {}, field {} , fieldContent {} ".format(host,field,fieldContent))
		sql = "UPDATE hosts SET {} = %s WHERE hostname = %s".format(field)
		self.cursor.execute(sql,(fieldContent,host))

	def update_job_status(self, jobID, status):
		sql = "UPDATE jobs SET status = '{}' WHERE jobid = '{}'".format(status, jobID)
		self.cursor.execute(sql)

	def get_host_data(self, host, field = "*"):
		sql = "SELECT {} from hosts WHERE hostname = '{}'".format(field, host)
		self.cursor.execute(sql, host)
		hostData = self.cursor.fetchone()
		return hostData

	def get_job_data(self, jobID, field = "*"):
		sql = "SELECT {} from jobs WHERE jobid = '{}'".format(field, jobID)
		self.cursor.execute(sql)
		jobsData = self.cursor.fetchone()
		return jobsData

	def get_worker_jobs(self, host, status = "*"):
		sql = "SELECT * from jobs WHERE hostname = '{}' AND status = '{}'".format(host, status)
		self.cursor.execute(sql)
		jobsData = self.cursor.fetchall()
		return jobsData

	def get_workers_list(self):
		sql = "SELECT hostname from hosts"
		self.cursor.execute(sql)
		listOfWorkersUnparsed = self.cursor.fetchall()
		listOfWorkers = [i[0] for i in listOfWorkersUnparsed]
		return listOfWorkers

	def get_max_jobid(self):
		sql = "SELECT MAX(jobid) from jobs"
		self.cursor.execute(sql)
		maxJobid = self.cursor.fetchone()
		return maxJobid

	def clean_table(self, table):
		sql = "TRUNCATE TABLE {}".format(table)
		self.cursor.execute(sql) 

if(__name__== "__main__"):
	main()
