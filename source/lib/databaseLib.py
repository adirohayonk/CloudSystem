"""
This module used for managing the database inserting and removing 
init creates the db pointer using connect_to_db function and create the cursor pointer.
"""
import mysql.connector
import traceback 


class DbController:
	def __init__(self,hostname):
		self.hostname = hostname
		self.username = "man" 
		self.password = "p" 
		self.database = "cloudSystemDB"
		try:
			self.mydb = self.connect_to_db(self.hostname, self.username, self.password, self.database)
		except mysql.connector.Error:
			print("Cannot connect to db (maybe server is off?)")
			exit(1)
		self.mydb.autocommit = True
		self.cursor = self.mydb.cursor(buffered=True)
		self.create_tables()

	def connect_to_db(self,hostname, username, password, database):
		""" This function creates the connection to the database
		
		Arguments:
			hostname (string) : hostname that database in located on 
			username (string) : username for the database  
			password (string) : password for the database  
			database (string) : database name 
		
		Returns:
			[class] : pointer to class controller 
		"""

		mydb = mysql.connector.connect(host=hostname,user=username,passwd=password,database=database)
		return mydb

	def create_tables(self):
		"""This function creates the jobs and hosts tables in the database if needed.
		"""
		checkJobsTable = "SHOW TABLES LIKE 'jobs'"
		checkHostsTable = "SHOW TABLES LIKE 'hosts'"
		self.cursor.execute(checkJobsTable)
		isExist = self.cursor.fetchone()
		if not(isExist):
			self.cursor.execute("CREATE TABLE jobs(jobid INT PRIMARY KEY, fileName VARCHAR(255), hostname VARCHAR(255), status VARCHAR(255))")
		self.cursor.execute(checkHostsTable)	
		isExist = self.cursor.fetchone()
		if not(isExist):
			self.cursor.execute("CREATE TABLE hosts(hostname VARCHAR(25) PRIMARY KEY, ipaddr VARCHAR(25),totalMem VARCHAR(25), CPUnum VARCHAR(25))")


	def insert_to_db(self, table, data):
		"""This function inserts data to database tables.
		
		Arguments:
			table (string) : Which table data should be inserted into 
			data (list) : list with the relevant data to this table
		"""

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

	def update_job_status(self, jobID, status):
		"""This function update job status based on jobID
		
		Arguments:
			jobID (int) : jobID to change the status for 
			status (string) : the new status 
		"""

		sql = "UPDATE jobs SET status = '{}' WHERE jobid = '{}'".format(status, jobID)
		self.cursor.execute(sql)

	def update_job_status_by_filename(self, fileName, status):
		"""This function update job status based on fileName
		because each file is called based on jobID fileName is different for each job 
		
		Arguments:
			fileName (string) : filename to change the status for 
			status (string) : the new status 
		"""

		sql = "UPDATE jobs SET status = '{}' WHERE fileName = '{}'".format(status, fileName)
		self.cursor.execute(sql)

	def get_host_data(self, host, field = "*"):
		"""this function returns data for specific host based on hostname if specific field is not privded it will return all the data
		
		Arguments:
			host (string) : hostname that data should be pulled for
		
		Keyword Arguments:
			field (str) : specific field to pull data for (default: ("*"))
		
		Returns:
			[list] : the requested data on the specific host 
		"""

		sql = "SELECT {} from hosts WHERE hostname = '{}'".format(field, host)
		self.cursor.execute(sql)
		hostData = self.cursor.fetchone()
		return hostData

	def get_host_data_by_ip(self, ipaddr, field = "*"):
		"""this function returns data for specific host based on ip address if specific field is not privded it will return all the data
		
		Arguments:
			ipaddr (str) : ip address that data should be pulled for 
		
		Keyword Arguments:
			field (str) : specific field to pull data for (default: ("*")) 
		
		Returns:
			[list] : the requested data on the specific host
		"""

		sql = "SELECT {} from hosts WHERE ipaddr = '{}'".format(field, ipaddr)
		self.cursor.execute(sql)
		hostData = self.cursor.fetchone()
		return hostData

	def get_job_data(self, jobID, field = "*"):
		"""This function returns specific job data based on jobID
		
		Arguments:
			jobID (int) : jobID that data should be pulled for 
		
		Keyword Arguments:
			field (str) : specific field to pull data for (default: ("*")) 
		
		Returns:
			[list] : the requested data for a specific jobID 
		"""

		sql = "SELECT {} from jobs WHERE jobid = '{}'".format(field, jobID)
		self.cursor.execute(sql)
		jobsData = self.cursor.fetchone()
		return jobsData

	def get_jobs_data(self, status = ""):
		"""This function returns all jobs data based on status if no status provided the function returns all jobs data
		
		Keyword Arguments:
			status (str) : status to pulled data for (default: (""))
		
		Returns:
			[list] : list with all the jobs data 
		"""

		sql = "SELECT * from jobs WHERE status = {}".format(status)
		self.cursor.execute(sql)
		jobsData = self.cursor.fetchall()
		return jobsData

	def get_worker_jobs(self, host, status = "*"):
		"""This function returns all the jobs that assigned to specific worker with specific status if no status provided function resturns all jobs data 
		
		Arguments:
			host (string) : the hostname to collect information for 
		
		Keyword Arguments:
			status (str) : status to pulled data for (default: (""))
		
		Returns:
			[list] : the requested data on the specific host 
		"""

		sql = "SELECT * from jobs WHERE hostname = '{}' AND status = '{}'".format(host, status)
		self.cursor.execute(sql)
		jobsData = self.cursor.fetchall()
		return jobsData

	def get_workers_list(self):
		"""This function returns all workers list
		
		Returns:
			[list] : list of workers based on hostname 
		"""

		sql = "SELECT hostname from hosts"
		self.cursor.execute(sql)
		listOfWorkersUnparsed = self.cursor.fetchall()
		listOfWorkers = [i[0] for i in listOfWorkersUnparsed]
		return listOfWorkers

	def get_next_jobid(self):
		"""This function returns the next jobID based on the last jobID in the database
		
		Returns:
			[int] : next jobID that is avalable if database is empty returns 1 
		"""

		sql = "SELECT MAX(jobid) from jobs"
		self.cursor.execute(sql)
		nextJobid = self.cursor.fetchone()[0]
		if nextJobid:
			return nextJobid + 1
		else:
			return 1

	def clean_table(self, table):
		"""This function will clean a specific table
		
		Arguments:
			table (str) : the specific table that should be cleaned 
		"""

		sql = "TRUNCATE TABLE {}".format(table)
		self.cursor.execute(sql) 

if(__name__== "__main__"):
	main()
