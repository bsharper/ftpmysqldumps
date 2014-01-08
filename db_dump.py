#!/usr/bin/env python
import ConfigParser
import os
import time
import ftplib
import cStringIO
from subprocess import Popen, PIPE

def checkArgs(args, typecheck=None):
    #check the arguments (args) as strings (if typecheck is not defiend) or that the object is of type typecheck
    if typecheck==None:
        for arg in args:
            # both None and empty strings are evaluated as false
            if not arg:
                return False
        return True
    else:
        for arg in args:
            if not arg or str(type(arg)).find(typecheck) == -1:
                return False
        return True

def dump_dbase_buffer(db_user=None, db_password=None, db_host=None, db=None, ssh_host=None, ssh_user=None, callRemotely=False):
    #
    # Note!  To call mysqldump over SSH, you must use public key authentication 
    #

    #since all arguments are made option by setting them to None, check to make sure the required arguments are defined
    if not checkArgs([db_user, db_password, db_host, db]):
        print "db_user, db_password, db_host and db must be defined"
        return ""
    if callRemotely and not checkArgs([ssh_host,ssh_user]):
        print "if callRemotely is enabled, ssh_host and ssh_user must be defined"
        return ""

    #construct the mysqldump command which is common between both local and remote runs
    dump_cmd = "mysqldump -u %s -p%s -h %s -e --opt -c %s" % (db_user,db_password,db_host,db)
    if callRemotely:
        #popen can take an array instead of a string of arguments.  dump_cmd is techically an argument for ssh at this point
        cmd = ["ssh", "%s@%s" % (ssh_user, ssh_host), "%s" % (dump_cmd)]
    else:
        #just create an array with a concatenated string
        cmd = [dump_cmd]
    
    print "Getting DB dump from %s and returning it as a file-like (cStringIO) object" % (db)
    
    output = ""

    #open the process and grab its output live
    proc = Popen(cmd, stdout=PIPE, bufsize=1)
    for line in iter(proc.stdout.readline, b''):
        output += line

    #close the process when it is done 
    proc.communicate()

    #create the string buffer that will act like a file
    buff = cStringIO.StringIO()
    buff.write(output)

    #reset the buffer to position 0
    buff.seek(0)

    #create the filename
    filestamp = time.strftime('%Y%m%d%I%M')
    filename = db+"_"+filestamp+".sql"

    #return a dict of the filename and the buffer
    return {"filename":filename, "buff":buff}

def transfer_dump_buffer(buff=None, filename=None, target=None, ftp_user=None, ftp_pass=None, ftp_path=None):
    #since all arguments are made option by setting them to None, check to make sure the required arguments are defined
    if not checkArgs([filename, target, ftp_user, ftp_pass]):
        print "filename, target, ftp_user and ftp_pass must be defined"
        return ""

    if not checkArgs([buff], "StringIO.StringO"):
        print "the buffer object 'buff' must be defined"
        return ""

    ftpConn = ftplib.FTP_TLS(target,ftp_user,ftp_pass)
    if ftp_path:
        ftpConn.cwd(ftp_path)
    
    #transfer file
    print "Transfering "+filename+" to "+target+"."
    ftpConn.storbinary('STOR %s' % filename, buff) 

    #close file, close ftp connection
    buff.close() 
    ftpConn.quit()
 
    
 
if __name__=="__main__":
    export = dump_dbase_buffer(db_host="localhost", db_user="dbuser", db_password="dbpass", db="db", callRemotely=True, ssh_host="remote_host", ssh_user="ssh_user")
    transfer_dump_buffer(buff=export['buff'], filename=export['filename'], target="ftp.example.com", ftp_user="ftp_user", ftp_pass="ftp_pass")


    