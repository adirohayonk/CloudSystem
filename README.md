# CloudSystem
This system allows executing of files on remote servers in linux environment.

## Getting Started
You can run the managerService ,workerService, and clientInterface on local Machine to see how the system works.  
See deployment for notes on how to deploy the project on a live system.

### Prerequisites
* [MariaDB] - MySQL database.
* [Prettytable] - for printing information to user interface
* [Python] - version 3.7 or newer.

### Installing
Install MySQL database on the manager server.  
install Prettytable module on the client machines:
```
pip install prettytable
```

## Deployment

You should copy manager folder with lib to the manager server, 
Configure the MySQL server data in DatabaseLib, then run the managerService.  

Copy the worker folder with lib to the workers machines.  
Copy the client folder to the users machines.  

## Author
* **Adir Ohayon** 

[MariaDB]: <https://downloads.mariadb.org/>
[Prettytable]: <http://zetcode.com/python/prettytable/>
[Python]: <https://www.python.org/>

