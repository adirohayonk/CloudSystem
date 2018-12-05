import os
import pathlib

def openFile(folder ,filename):
    if not os.path.exists(folder):
        os.makedirs(folder)
    if os.path.isfile(filename):
        return True
    else: 
        return False

def createEnv():
    jobsFolder = 'jobs/'
    jobsResultsFolder = 'jobs_results/'
    pathlib.Path(jobsFolder).mkdir(parents=True, exist_ok=True)
    pathlib.Path(jobsResultsFolder).mkdir(parents=True, exist_ok=True)
    
    
