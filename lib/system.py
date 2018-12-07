import platform
import multiprocessing
from psutil import virtual_memory
import subprocess
import re

def gatherInformation():
    hostname = subprocess.check_output(["hostname"]) 
    hostname = hostname.decode()

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