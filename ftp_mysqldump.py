#!/usr/bin/env python
import ConfigParser
import os
import time
import ftplib
 
def dump_dbase():

    #set database variables
    user = '<database user with mysqldump permissions>'
    password = '<dbase password>'
    host = '<host such as 127.0.0.1>'
    database = '<dbase name>'

    #This builds the export filename
    filestamp = time.strftime('%Y%m%d%I%M')
    filename = database+"_"+filestamp+".sql"

    #Export file
    print "\nExporting "+filename+" to local directory."
    os.popen("mysqldump -u %s -p%s -h %s -e --opt -c %s > %s" % (user,password,host,database,filename))
    return filename

def transfer_dump(filename):

    #set ftp vars
    target = '<ftp host here>'
    ftpuser = '<username>'
    ftppass = '<ftp pass>'
    ftppath = '<directory>'

    
    #open FTP connection (you can use ftplib.FTP or ftplib.FTP_TLS)
    ftpConn = ftplib.FTP_TLS(target,ftpuser,ftppass)
    ftpConn.cwd(ftppath)
    
    #open file to transfer
    infile = open(filename,'rb')

    #transfer file
    print "Transfering "+filename+" to "+target+"."
    ftpConn.storbinary('STOR %s' % filename, infile) 

    #close file, close ftp connection
    infile.close() 
    ftpConn.quit()
    
 
if __name__=="__main__":
    export = dump_dbase()
    transfer_dump(export)
