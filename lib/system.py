import sys
sys.path.append('../lib/')
import pathlib
import platform
import multiprocessing
from psutil import virtual_memory
import subprocess
import re

def openFile(folder ,filename):
    if not os.path.exists(folder):
        os.makedirs(folder)
    if os.path.isfile(filename):
        return True
    else: 
        return False

def createEnv():
    jobsFolder = 'jobs/'
    pathlib.Path(jobsFolder).mkdir(parents=True, exist_ok=True)
    
def gatherInformation():
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
    unparsedIpOutput = subprocess.check_output(["ip", "route", "ls"])
    splitted = re.findall( r'src [\d.-]+ metric', str(unparsedIpOutput))
    ipaddr = splitted[0].split()[1]
    return ipaddr

def getSystemHostname():
    hostname = subprocess.check_output(["hostname"]) 
    hostname = hostname.decode()
    hostname = hostname.replace("\n","")
    return hostname

def run_file(filename_to_run, db):
	"""
	This function execute a file and store the output in output file 	
	Arguments:
		filename_to_run {String} -- filename that should be executed by the function
		db {class} -- pointer to the db controller from the worker  
	
	Returns:
		String -- output_file name 
	"""
	realFileLocation = "jobs/" +filename_to_run 
	output_file = "results-" + filename_to_run 
	#change the permission of the file to make it executeable
	subprocess.call(["chmod", "+x", realFileLocation]) 
	db.update_job_status_by_filename(filename_to_run, "IN-PROGRESS") 
	#run the job and store the output
	result = subprocess.check_output(['bash', realFileLocation]) 
	#after execuion completed change job status in db
	db.update_job_status_by_filename(filename_to_run, "COMPLETED") 
	f = open("jobs/" + output_file, 'w') 
	f.write(result.decode()) 
	return output_file
