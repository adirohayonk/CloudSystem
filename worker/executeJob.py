import sys
sys.path.append('../lib/')
import subprocess


def run_file(filename_to_run, db, hostname):
	"""
	This function execute a file and store the output in output file 	
	Arguments:
		filename_to_run {String} -- filename that should be executed by the function
		db {class} -- pointer to the db controller from the worker  
		hostname {String} -- hostname of the worker that perform this job
	
	Returns:
		String -- output_file name 
	"""

	realFileLocation = "jobs/" +filename_to_run #job file are in jobs folder
	output_file = "results-" + filename_to_run #output file should have a perfix of results
	subprocess.call(["chmod", "+x", realFileLocation]) #change the permission of the file to make it executeable
	jobID = 1
	maxJobID = db.get_max_jobid()[0] # find current max jobID
	if maxJobID:  #if no jobs at all jobID will be 1
		jobID = maxJobID + 1 #increase jobID by 1 in order to make it unique
	jobData = [jobID, filename_to_run, hostname, "IN-PROGRESS"] #list with the data the should be written to database
	db.insert_to_db("jobs", jobData) #insert data to db
	result = subprocess.check_output(['bash', realFileLocation]) #run the job and store the output
	db.update_job_status(jobID, "COMPLETED") #after execuion completed change job status in db
	f = open("jobs/" + output_file, 'w') 
	f.write(result.decode()) #write results to output_file
	return output_file
