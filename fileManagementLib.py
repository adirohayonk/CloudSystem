import os

def checkFiles(filename):
    if os.path.isfile(filename):
        return True
    else: 
        return False
