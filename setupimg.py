#! /usr/bin/env python
# -*- coding: utf8 -*-
import os
import logging
import sys
import sqlite3
import subprocess
import shutil

s_curcwd = ""	#Current Working Path
s_imgdir = ""	#Location that saves disk images
s_cfgdir = ""	#Location that saves VM configures
s_sshdir = ""	#Place to save ssh key
cs_mountpoint = "/mnt/tempmp"
cs_hostnamefile = "/etc/hostname"
cs_sshrsafile = "/etc/ssh/ssh_host_rsa_key"
cs_sshrsapubfile = "/etc/ssh/ssh_host_rsa_key.pub"
cs_sshdsafile = "/etc/ssh/ssh_host_dsa_key"
cs_sshdsapubfile = "/etc/ssh/ssh_host_dsa_key.pub"
cs_interfacefile = "/etc/network/interfaces"

s_hostname = ""
s_ip = ""
s_gw = ""
s_imgfile = ""
i_VID = 0

def dbinit():
	'''Initiate a sqlite3 database'''
	global db_conn
	s_dbfile = s_cfgdir + '/config.db'
	db_conn = sqlite3.connect(s_dbfile)
	loginfo = "connected db:" + s_dbfile
	logging.info("dbinit:"+ loginfo)
	c = db_conn.cursor()
	db_conn.row_factory = sqlite3.Row


	#Check if VTPM table is existed
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='VTPM';")
	if c.fetchone() == None:
		#VTPM table not existed
		logging.info("dbinit: VTPM table not existing, Create it!")
		db_conn.execute('''
			CREATE TABLE VTPM (
			VID INT PRIMARY KEY,
			HOSTNAME TEXT DEFAULT NULL,
			IP TEXT DEFAULT NULL,
			SSHP TEXT DEFAULT NULL,
			CONF TEXT DEFAULT NULL,
			SRK TEXT DEFAULT NULL
			);
			''')
	else:
		logging.info("dbinit: VTPM table existed")

	logging.info("dbinit: Database Initiate Complete!")


def init():
	'''Create the Data File and Load Current Client Images'''
	#Incluse some global vars
	global s_curcwd
	global s_imgdir
	global s_cfgdir
	global s_sshdir


	logging.basicConfig(level=logging.INFO) 
	s_curcwd = os.getcwd()
	s_imgdir = os.path.abspath(s_curcwd+"/../img/")
	s_cfgdir = os.path.abspath(s_curcwd+"/../cfg/")
	s_sshdir = os.path.abspath(s_curcwd+"/../ssh/")

	#Check diractories availabitlity.
	b_imgdir = os.path.exists(s_imgdir)
	b_cfgdir = os.path.exists(s_cfgdir)
	b_sshdir = os.path.exists(s_sshdir)

	if b_imgdir == False:
		logging.error("init: Disk Image Path not exist!")
		exit()
	else:
		logging.info("init: Disk Image Path exists!")
	
	if b_cfgdir == False:
		logging.info("init: VM configure path not exist!")
		os.makedirs(s_cfgdir)
		if os.path.exists(s_cfgdir) == True:
			logging.info("init: VM configure path created successful")
	else:
		logging.info("init: VM configure path exist!")
	
	if b_sshdir == False:
		logging.info("init: SSH Key path not exist!")
		os.makedirs(s_sshdir)
		if os.path.exists(s_sshdir) == True:
			logging.info("init: SSH key path created successful")
	else:
		logging.info("init: SSH key path path exist!")

	return
def op_gensshkey():
	'''Generate SSH Key for the new VM'''
	global s_sshdir
		
	s_rsafile = str(i_VID) + "-ssh_host_rsa_key"
	s_dsafile = str(i_VID) + "-ssh_host_dsa_key"
	
	#Generate RSA KEY
	i_ret = subprocess.call(['ssh-keygen','-f', s_sshdir + "/" + s_rsafile, '-N', '', '-t', 'rsa', '-C', 'root@client' + str(i_VID)])
	if i_ret != 0:
		logging.error("openssh: RSA KEY GEN FAILD ID:%s",str(i_VID))
		exit(1)
	else:
		logging.info("openssh: RSA KEY GEN SUCCESSFUL ID:%s",str(i_VID))
		
	#Generate DSA KEY
	i_ret = subprocess.call(['ssh-keygen','-f', s_sshdir + "/" + s_dsafile, '-N', '', '-t', 'dsa', '-C', 'root@client' + str(i_VID)])
	if i_ret != 0:
		logging.error("openssh: DSA KEY GEN FAILD ID:%s",str(i_VID))
		exit(1)
	else:
		logging.info("openssh: DSA KEY GEN SUCCESSFUL ID:%s",str(i_VID))

def op_mount():
	'''Mount img to the mountpoint'''
	global s_imgdir

	global cs_mountpoint
	
	if os.path.exists(cs_mountpoint) == False:
		logging.error("Mount Point not exist")
		exit(1)
	
	#Construct image's file name
	s_imgfilename = s_imgdir + '/' + 'client' + str(i_VID) + '.img'


	#Start Mounting
	i_ret = subprocess.call(['mount','-t','auto','-o','loop',s_imgfilename,cs_mountpoint])
	if i_ret != 0:
		logging.error("Mounting Error!")
		exit(1)
	
	logging.info("Mount Successful!")

def op_umount():
	'''Umount the img file'''
	global cs_mountpoint
	i_ret = subprocess.call(['umount',cs_mountpoint])

	if i_ret != 0:
		logging.error("Umount Error!")
		exit(1)
	
	logging.info("Umount Success")


def op_update_fs():
	'''
	Update Hostname of VM
	Replace VMs SSH KEY
	Update VMs IP Addr
	'''

	global cs_mountpoint, cs_hostnamefile, cs_sshrsafile,\
	cs_sshrsapubfile, cs_sshdsafile, cs_sshdsapubfile
	global s_sshdir, i_VID

	#Replace SSH KEYS

	#Replace SSH RSA KEYS

	s_sfilename = s_sshdir + '/' + str(i_VID) + '-ssh_host_rsa_key' 
	shutil.copy(s_sfilename, cs_mountpoint + cs_sshrsafile)	
	s_sfilename = s_sshdir + '/' + str(i_VID) + '-ssh_host_rsa_key.pub'
	shutil.copy(s_sfilename, cs_mountpoint + cs_sshrsapubfile)

	#Replace SSH DSA Keys

	s_sfilename = s_sshdir + '/' + str(i_VID) + '-ssh_host_dsa_key'
	shutil.copy(s_sfilename, cs_mountpoint + cs_sshdsafile)	
	s_sfilename = s_sshdir + '/' + str(i_VID) + '-ssh_host_dsa_key.pub'
	shutil.copy(s_sfilename, cs_mountpoint + cs_sshdsapubfile)

	logging.info("UpdateFS: SSH KEY Replaced")

	#Change VM Hostname
	s_sfilename = cs_mountpoint + cs_hostnamefile
	f_hostname = open(s_sfilename,"w+b")

	f_hostname.write(s_hostname)
	f_hostname.close()
	logging.info('Hostname Updated')

	#Change VM IP Address
	s_sfilename = cs_mountpoint + cs_interfacefile
	f_interface = open(s_sfilename, "w+b")
	f_interface.write('# The loopback network interface\n')

	f_interface.write('auto lo\n')
	f_interface.write('iface lo inet loopback\n')
	f_interface.write('# The primary network interface\n')
	f_interface.write('auto eth0\n')
	f_interface.write('iface eth0 inet static\n')
	f_interface.write('\taddress '+s_ip +'\n' )
	f_interface.write('\tnetmask 255.255.255.0\n')
	f_interface.write('\tgateway '+s_gw+'\n')
	f_interface.close()
	logging.info("IP Set UP")


def db_update():
	'''Update the info to the database'''
	global db_conn

	c = db_conn.cursor()
	c.execute('''
		UPDATE VTPM SET 
		HOSTNAME=?,
		IP=?
		WHERE VID=?;		
		''',(s_hostname,s_ip,i_VID))
	db_conn.commit()
	logging.info("DB: Update DB Successful")

def cmd_paste():
	'''Paste Commandline to global vars'''
	global s_ip, s_hostname, s_gw, i_VID
	i = 1
	while i<len(sys.argv) -1:
		if sys.argv[i] == '-n':
			#VID
			i_VID = int(sys.argv[i+1])
			i = i+2
			continue

		if sys.argv[i] == '-hn':
			#HostName
			s_hostname = sys.argv[i+1]
			i = i+2
			continue

		if sys.argv[i] == '-ip':
			#IP Address
			s_ip = sys.argv[i+1]
			i = i+2
			continue

		if sys.argv[i] == '-gw':
			#Gateway
			s_gw = sys.argv[i+1]
			i = i+2
			continue

		i = i+1
	
	if (s_gw == "") or (s_ip == "") or (s_hostname == ""):
		logging.error("SETUP IMG: Params error!")
		exit(1)

	if (i_VID == 0):
		logging.error("SETUP IMG: Params error!")
		exit(1)
		

if __name__ == '__main__':
	init()
	dbinit()
	cmd_paste()
#	s_ip='192.168.35.5'
#	s_gw='192.168.35.1'
#	i_VID = 1
	op_gensshkey()
	op_mount()
#	s_hostname = 'Client1'
	op_update_fs()
	op_umount()
	db_update()
	print s_ip,s_gw,s_hostname, i_VID
	db_conn.close()


	pass
