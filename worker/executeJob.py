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
	realFileLocation = "jobs/" +filename_to_run 
	output_file = "results-" + filename_to_run 
	#change the permission of the file to make it executeable
	subprocess.call(["chmod", "+x", realFileLocation]) 
	jobID = 1
	maxJobID = db.get_max_jobid()[0] 
	if maxJobID:  
		jobID = maxJobID + 1 
	#list with the data that should be written to database
	jobData = [jobID, filename_to_run, hostname, "IN-PROGRESS"] 
	db.insert_to_db("jobs", jobData) 
	#run the job and store the output
	result = subprocess.check_output(['bash', realFileLocation]) 
	#after execuion completed change job status in db
	db.update_job_status(jobID, "COMPLETED") 
	f = open("jobs/" + output_file, 'w') 
	f.write(result.decode()) 
	return output_file
