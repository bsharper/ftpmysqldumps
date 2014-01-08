#!/usr/bin/env python
import ConfigParser
import os
import time
import ftplib
import cStringIO
from subprocess import Popen, PIPE
import paramiko
import logging
import sys
import time

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='%s.log' % sys.argv[0].split('.', 1)[0],
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
#formatter = logging.Formatter('%(name)-30s: %(levelname)-8s %(message)s')

formatter = logging.Formatter('%(message)s')

# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('dbdump').addHandler(console)
ssh_log = logging.getLogger('dbdump.ssh')
sftp_log = logging.getLogger('dbdump.sftp')


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

def dump_remote_dbase(db_user=None, db_password=None, db_host=None, db=None, ssh_host=None, ssh_user=None, ssh_password=None, verbose=True):
    if not checkArgs([db_user, db_password, db_host, db, ssh_host, ssh_user, ssh_password]):
        print "db_user, db_password, db_host, db, ssh_host, ssh_user and ssh_password must be defined"
        return ""

    ssh = paramiko.SSHClient()

    #uncomment out this line if you want to always trust the remote system's key.  Not recommended!
    #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_log.info("Loading keys from system")
    ssh.load_system_host_keys()
    ssh_log.info("Connecting to %s" % (ssh_host))
    ssh.connect(ssh_host, username=ssh_user, password=ssh_password)
    dump_cmd = "mysqldump -u %s -p%s -h %s -e --opt -c %s" % (db_user,db_password,db_host,db)
    ssh_log.debug(dump_cmd)

    start = time.time()
    stdin, stdout, stderr = ssh.exec_command(dump_cmd)
    duration = time.time() - start

    ssh.close()
    output = stdout.read()

    buff = cStringIO.StringIO()
    buff.write(output)

    
    buff.seek(0)
    
    filestamp = time.strftime('%Y%m%d%I%M')
    filename = db+"_"+filestamp+".sql"
    rv = {"filename":filename, "buff":buff}
    ssh_log.info("DB Export complete (took %s seconds) " % duration)
    ssh_log.debug("Buffer length: %d, Filename %s" % (len(output), filename))
    return rv

def transfer_dump_sftp(buff=None, filename=None, sftp_host=None, sftp_port=22, sftp_user=None, sftp_pass=None, sftp_path=None, debug_mode=False):
    #since all arguments are made optional by setting them to None, check to make sure the required arguments are defined
    if not checkArgs([filename, sftp_host, sftp_user, sftp_pass]):
        print "filename, sftp_host, sftp_user, sftp_pass"
        return ""

    if not checkArgs([buff], "StringIO.StringO"):
        print "the buffer object 'buff' must be defined"
        return ""
    sftp_log.info('Connecting to %s' % (sftp_host))
    transport = paramiko.Transport((sftp_host, sftp_port))
    transport.connect(username = sftp_user, password = sftp_pass)
    ssh = paramiko.SFTPClient.from_transport(transport)

    if sftp_path:
        ssh.chdir(sftp_path)
    
    sftp_log.info("Transfering "+sftp_host+" to "+sftp_host)
    start = time.time()
    ssh.putfo(fl=buff, remotepath=filename)
    duration = time.time() - start
    sftp_log.info("Transfer complete (took %s seconds)" % duration)
    
    saved_buff = cStringIO.StringIO()
    if debug_mode:
        ls = ssh.listdir()
        sftp_log.debug(ls)
        ssh.getfo(fl=saved_buff, remotepath=filename)
        saved_buff.seek(0)
        ssh.remove(filename)

    buff.close() 
    ssh.close()
    transport.close()

    if debug_mode:
        return saved_buff
 
def getSHA(obj):
    import hashlib
    h = hashlib.sha256()
    h.update(obj.read())
    obj.seek(0)
    return h.hexdigest()

if __name__=="__main__":
    print """Example usage:
    from db_dump_internal import *

    db_dump_options = {
        "db_host":"localhost", 
        "db_user":"dbuser", 
        "db_password":"dbpass", 
        "db":"db", 
        "ssh_host":"remote_host", 
        "ssh_user":"sshuser", 
        "ssh_password":"sshpass"
    }
    export = dump_remote_dbase(**db_dump_options)
    
    sftp_options = {
        "buff":export['buff'],
        "filename":export['filename'],
        "sftp_host":"example.com",
        "sftp_user":"sftp_user",
        "sftp_pass":"sftp_pass",
        "sftp_path":"path"
    }

    transfer_dump_sftp(**sftp_options)
    
    """
