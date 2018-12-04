import platform
import multiprocessing
import psutil import virtual_memory
import subprocess

def gatherInformation():
    hostname = subprocess.check_output(["hostname"]) 

    #getting ip address
    unparsedIpOutput = subprocess.check_output(["ip", "route", "ls"])
    splitted = re.findall( r'src [\d.-]+ metric', str(unparsedIpOutput))
    ipaddr = splitted[0].split()[1]

    totalMemory = (virtual_memory()).total
    numberOfCPU = multiprocessing.cpu_count()

    information = hostname + ":" + ipaddr ":" + totalMemory + ":" + numberOfCPU
    return information

    