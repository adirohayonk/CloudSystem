#!/usr/bin/python
import subprocess
import threading


def run_file(filename_to_run,filename_to_store_output):
    result = subprocess.Popen(['bash', filename_to_run])
    print(result,open(filename_to_store_output,"w"))


def main():
    run_file("abc","/home/kipseron/zobi")


if __name__ == '__main__':
    main()
