
ftpmysqldumps

This python script will create a mysqldump file of your database and then upload a copy of it to an ftp server.

Before you can use this you will need to configure your passwords in the following places:

at line 9:
    #set database variables
    user = '<database user with mysqldump permissions>'
    password = '<dbase password>'
    host = '<host such as 127.0.0.1>'
    database = '<dbase name>'

at line 26:
    #set ftp vars
    target = '<ftp host here>'
    ftpuser = '<username>'
    ftppass = '<ftp pass>'
    ftppath = '<directory>'


if you do not want to use TLS for a secure ftp connection simply change line 34:

from: 
    ftpConn = ftplib.FTP_TLS(target,ftpuser,ftppass)    

to:
    ftpConn = ftplib.FTP(target,ftpuser,ftppass)    

    