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
    libFolder = '../lib/'
    pathlib.Path(jobsFolder).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(libFolder):
        raise Exception('lib folder is missing in {}'.format(os.path.abspath(libFolder)))
