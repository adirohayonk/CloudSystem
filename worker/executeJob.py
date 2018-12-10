import sys
sys.path.append('../lib/')
import subprocess


def run_file(filename_to_run, db, hostname):
	realFileLocation = "jobs/" +filename_to_run
	output_file = "results-" + filename_to_run
	subprocess.call(["chmod", "+x", realFileLocation])
	jobID = 1
	maxJobID = db.get_max_jobid()[0]
	if maxJobID:
		jobID = maxJobID + 1
	jobData = [jobID, filename_to_run, hostname, "IN-PROGRESS"]
	db.insert_to_db("jobs", jobData)
	result = subprocess.check_output(['bash', realFileLocation])
	db.update_job_status(jobID, "COMPLETED")
	f = open("jobs/" + output_file, 'w')
	f.write(result.decode())
	return output_file
