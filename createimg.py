#! /usr/bin/env python
# -*- coding: utf8 -*-
import os
import logging
import sys
import sqlite3
import shutil

s_curcwd = "/root/py"	#Current Working Path
s_imgdir = ""	#Location that saves disk images
s_cfgdir = ""	#Location that saves VM configures
l_debug = None	
i_imgnum = 0;	#The count of the images need to be copied
db_conn = None	#Database connection
const_basefile='base0.img'	#File name of the basefile


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

def db_insertVID(vid):
	'''Insert an VID in Table VTPM'''
	global db_conn

	c = db_conn.cursor()
	logging.info("Insert VID: %s",str(vid))
	try:
		c.execute('''INSERT INTO VTPM VALUES(?,NULL,NULL,NULL,NULL,NULL) ''', (vid,))
		db_conn.commit()
	except sqlite3.IntegrityError:
		logging.error('''Same VID existed''')




def db_consist():
	'''Check Database consistancy with files in ./img and repair
	it if necessary'''
	pass


def db_loadVID():
	'''Return a List contain VID from the db file.'''
	global db_conn

	c = db_conn.cursor()
	#Load VID From config.db
	c.execute('''SELECT VID FROM VTPM;''')
	l_VID = []
	item = c.fetchone()
	while item != None:
		l_VID.append(int(item['VID']))
		item = c.fetchone()
	
	logging.info("LoadVID: Load %s VID from DB",str(len(l_VID)))
	return l_VID


def img_to_num(l_img):
	'''Convert the list full of name to numbers'''
	l_imgid = []

	for item in l_img:
		s_num = item[6:-4]
		l_imgid.append(int(s_num))

	return l_imgid


def list_img():
	'''return a list contain the client img files in ./img location'''
	global s_imgdir

	#Get a full list of files in path
	rawlist = os.listdir(s_imgdir)
	imglist = []
	for item in rawlist:
		if len(item) > 10:
			if (item[-4:] == ".img") and (item[:6] == "client"):
				imglist.append(item)

	logging.info("list_img: imgs load complete! %s",str(imglist))	
	return imglist

def copy_img(last = 1, count = 1):
	'''Copy base0.img to client0.img'''
	#Check if basefile exist
	global const_basefile
	global s_imgdir

	s_basefile = s_imgdir + '/' + const_basefile
	if os.path.exists(s_basefile) == False:
		logging.error("CopyIMG: Base File not exist!")
		exit(1)
	
	#Basefile is existed Start Copying
	i = 1
	while i <= count:
		s_clientfile = "client" + str(i+last) + ".img"
		s_clientfile = s_imgdir + '/' + s_clientfile
		logging.info("CopyIMG: copy %s to %s", s_basefile, s_clientfile)
		
		#copy
		shutil.copy2(s_basefile, s_clientfile)
		#Logging this file to Database
		db_insertVID(i+last)
		i = i+1

	
	logging.info("CopyIMG: Copy Complete!")


def init():
	'''Create the Data File and Load Current Client Images'''
	#Incluse some global vars
	global s_curcwd
	global s_imgdir
	global s_cfgdir


	logging.basicConfig(level=logging.INFO) 
#	s_curcwd = os.getcwd()
	s_imgdir = os.path.abspath(s_curcwd+"/../img/")
	s_cfgdir = os.path.abspath(s_curcwd+"/../cfg/")
	#Check diractories availabitlity.
	b_imgdir = os.path.exists(s_imgdir)
	b_cfgdir = os.path.exists(s_cfgdir)
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
	

	return

#MAIN
if __name__ == '__main__':
	i = 1
	if len(sys.argv) == 1:
		logging.error("argv: Please specific a number of images")
		exit(1)
	
	while i < len(sys.argv):
		if sys.argv[i] == '-n' and i+1 < len(sys.argv):
			if sys.argv[i+1].isdigit() == True:
				i_imgnum = int(sys.argv[i+1])
				print i_imgnum
				break
			else:
				logging.error("argv: Error Input")
				exit()
		
		i = i+1
	
	if i == len(sys.argv):
		logging.error("argv: Please specific a number of images")
		exit(1)

	#Perform Initial Sequence
	init()
	dbinit()

	#List Current Images in the disk
	l_imglist = list_img()
	l_imgnum = img_to_num(l_imglist)
	l_imgnum.sort()
	if len(l_imgnum) == 0:
		i_last = 0
	else:
		i_last = l_imgnum[-1]
	
	#Begin to copy from the last number
	logging.info("Begin Copy from %s to %s", str(i_last + 1), str(i_last + i_imgnum))
	copy_img(last = i_last, count = i_imgnum)
	db_conn.close()




