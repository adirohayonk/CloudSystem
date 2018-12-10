import subprocess


def run_file(filename_to_run):
	output_file = "result-" + filename_to_run
	subprocess.call(["chmod", "+x", filename_to_run])
	result = subprocess.check_output(['bash', filename_to_run])
	f = open("jobs_results/" + output_file, 'w')
	f.write(result.decode())