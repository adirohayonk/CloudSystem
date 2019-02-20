"""This module contains various system functions 
that collects information and run files
"""
import sys
sys.path.append('../lib/')
import pathlib
import platform
import multiprocessing
from psutil import virtual_memory
import subprocess
import re

def createEnv():
	"""This function creates the jobs folder if needed.
	"""
	jobsFolder = 'jobs/'
	pathlib.Path(jobsFolder).mkdir(parents=True, exist_ok=True)
	
	
def gatherInformation():
	"""This function collects system information such as hostname, ip address, total memory, number of CPU

	Returns:
		[string] : information splitted by colon
	"""

	#getting hostname
	hostname = getSystemHostname()

	#getting ip address
	ipaddr = getSystemIp()

	totalMemory = (virtual_memory()).total
	totalMemory = int(totalMemory/1024/1024)
	numberOfCPU = multiprocessing.cpu_count()

	information = "{}:{}:{}:{}".format(hostname,ipaddr,totalMemory,numberOfCPU)
	information = information.replace("\n","")
	return information


def getSystemIp():
	"""This function returns the system ip using ip command.
	
	Returns:
		[string]: The ip address of the system 
	"""

	unparsedIpOutput = subprocess.check_output(["ip", "route", "ls"])
	splitted = re.findall( r'src [\d.-]+ metric', str(unparsedIpOutput))
	ipaddr = splitted[0].split()[1]
	return ipaddr

def getSystemHostname():
	"""This function returns the hostname of the system using hostname command.
	
	Returns:
		[string]: the hostname of the system 
	"""

	hostname = subprocess.check_output(["hostname"]) 
	hostname = hostname.decode()
	hostname = hostname.replace("\n","")
	return hostname

def run_file(filename_to_run, db):
	"""
	This function execute a file and store the output in output file 	
	Arguments:
		filename_to_run (String) : filename that should be executed by the function
		db (class) : pointer to the db controller from the worker  
	
	Returns:
		String : output_file name 
	"""
	realFileLocation = "jobs/" +filename_to_run 
	output_file = "results-" + filename_to_run 
	f = open("jobs/" + output_file, 'w') 
	#change the permission of the file to make it executeable
	print("Changing file permission make it executable")
	subprocess.call(["chmod", "+x", realFileLocation]) 
	db.update_job_status_by_filename(filename_to_run, "IN-PROGRESS") 
	print("Updating status to IN-PROGRESS")
	#run the job and store the output
	try:
		result = subprocess.check_output(["./"+realFileLocation],stderr=subprocess.STDOUT, universal_newlines=True) 
		print("Running File {}".format(filename_to_run))
	except subprocess.CalledProcessError as exc:
		print("Job Failed to run: ErrorCode:{} \n{} ".format( exc.returncode, exc.output),file=f) 
		db.update_job_status_by_filename(filename_to_run,"ERROR")
		return output_file

	#after execuion completed change job status in db
	db.update_job_status_by_filename(filename_to_run, "COMPLETED") 
	print("job has been done changing status to COMPLETED")
	f.write(result) 
	f.close()
	return output_file
