ftpmysqldumps in 2 new flavors
-------------------------------

This repo has 2 modifications to ftpmysqldumps.  Both version have an updated argument structure which uses optional arguments instead of locally assigned variables for setting dump or upload parameters.  I prefer using a dict that is unpacked using **

```
params = {
    "arg1":"Hello",
    "arg2":"World"
    }

func(**params)
```

This is the same as

```
func(arg1="Hello", arg2="World")
```

###db_dump.py
This file uses Popen and stdout to grab the output of mysqldump directly, which skips writing the file to the file system.  It also adds the ability to remotely call via SSH this command, though currently on systems that are in authorized_keys can do this.

###db_dump_internal.py
The second modification uses the excellent paramiko library (https://github.com/paramiko/paramiko) to handle all of the SSHing and SFTPing internally, without calling any external commands.  This allows using passwords passed in as parameters, though the systems should have at least connected once to get past the "Are you sure you want to continue connecting..." unknown host check.  Also, this version uses the logging library, and has the ability to upload the file in debug mode.  Debug mode simply  takes a hash of the mysqldump export, uploads the file, downloads the file, takes a hash of the downloaded file and compares them.




Original readme from https://github.com/mybedisacomputer/ftpmysqldumps

ftpmysqldumps
-------------

###This python script will create a mysqldump file of your database and then upload a copy of it to an ftp server.

Before you can use this you will need to configure your passwords in the following places:

at line 9:
```
    #set database variables
    user = '<database user with mysqldump permissions>'
    password = '<dbase password>'
    host = '<host such as 127.0.0.1>'
    database = '<dbase name>'
```    

at line 26:
```
    #set ftp vars
    target = '<ftp host here>'
    ftpuser = '<username>'
    ftppass = '<ftp pass>'
    ftppath = '<directory>'
```

if you do not want to use TLS for a secure ftp connection simply change line 34:

from: 
```
    ftpConn = ftplib.FTP_TLS(target,ftpuser,ftppass)  
```    

to:
```
    ftpConn = ftplib.FTP(target,ftpuser,ftppass)    
```
    
