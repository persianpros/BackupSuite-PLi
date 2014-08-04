# -*- coding: utf-8 -*-
from os import environ as os_environ
import gettext
import sys

def localeInit():
	gettext.bindtextdomain("BackupSuite","/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/locale")

localeInit()



def _(txt):
	t = gettext.dgettext("BackupSuite", txt)
	if t == txt:
		#print "[BackupSuite] fallback to default translation for", txt
		t = gettext.gettext(txt)
	return t


def message01():
	print _("No supported receiver found!")
	return 
	
def message02():
	print _("BACK-UP TOOL, FOR MAKING A COMPLETE BACK-UP")
	return
		
def message03():
	sys.stdout.write(_("Please be patient, a backup will now be made, this will take about: "))
	return

def message04():
	sys.stdout.write(_(" size to be backed up: "))
	return 
	
def message05():
	print _("not found, the backup process will be aborted!")
	return

def message06():
	print _("Some information about the task")
	return 

def message06a():
	sys.stdout.write(_("Create: root.ubifs"))
	return

def message07():
	print _("Create: kerneldump")
	return

def message08():
	print _("Almost there... Now building the USB-Image!")
	return

def message09():
	sys.stdout.write(_("Additional backup -> "))
	return

def message10():
	sys.stdout.write(_("USB Image created in: "))
	return

def message11():
	sys.stdout.write(_("and there is made an extra copy in: "))
	return

def message12():
	print _("To restore the image:")
	print _("Place the USB-flash drive in the (front) USB-port and switch the receiver off and on with the powerswitch on the back of the receiver.")
	print _("Follow the instructions on the front-display.")
	print _("Please wait.... almost ready!")
	return

def message13():
	print _("To restore the image:")
	print _("Place the USB-flash drive in the (front) USB-port and switch the receiver off and on with the powerswitch on the back of the receiver.")
	print _("Press arrow up from frontpanel to start loading.")
	print _("Please wait.... almost ready!")
	return 

def message14():
	print _("Please check the manual of the receiver on how to restore the image.")
	return

def message15():
	print _("Image creation FAILED!")
	return 

def message16():
	sys.stdout.write(_("available "))
	return 

def message17():
	print _("There is a valid USB-flashdrive detected in one of the USB-ports, therefore an extra copy of the back-up image will now be copied to that USB-flashdrive.")
	print _("This only takes about 20 seconds.....")
	return

def message18(): #XP1000
	print _("To restore the image:")
	print _("Place USB stick in the USB slot at the rear side of the XP1000 and switch the receiver off and on with the powerswitch")
	print _("When the record LED and standby LED become red press CH+ button on the receiver to start USB update.")
	print _("Wait until the standby LED will become blue.")
	print _("Please wait.... almost ready!")
	return

def message19():
	print _("Backup finished and copied to your USB-flashdrive.")
	return

def message20():
	sys.stdout.write(_("Full back-up to the harddisk"))
	return

def message21():
	print _("There is NO valid USB-stick found, so I've got nothing to do.")
	print " "
	print _("PLEASE READ THIS:")
	print _("To back-up directly to the USB-stick, the USB-stick MUST contain a file with the name:")
	print _("backupstick or")
	print _("backupstick.txt")
	print " "
	print _("If you place an USB-stick containing this file then the back-up will be automatically made onto the USB-stick and can be used to restore the current image if necessary.")
	print _("The program will exit now.")
	return

def message22():
	sys.stdout.write(_("Full back-up direct to USB"))
	return

def message23():
	print _("The content of the folder is:")
	return
	
	
def message24():
	sys.stdout.write(_("Time required for this process: "))
	return 
	
def message25():
	print _("minutes")
	return 
	
def message26():
	sys.stdout.write(_("Backup done with: "))
	return
	
def message27():
	print _("KB per second")
	return 

def message28():
	print _("Most likely this back-up can't be restored because of it's size, it's simply too big to restore. This is a limitation of the bootloader not of the back-up or the BackupSuite.")
	return

def message29():
	print _("There COULD be a problem with restoring this back-up because the size of the back-up comes close to the maximum size. This is a limitation of the bootloader not of the back-up or the BackupSuite.")
	return
	
def message30():
	print _("* * * WARNING * * *")
	sys.stdout.write(_("Not enough free space on "))
	return
	
def message31():
	print _(" to make a back-up!")
	return
	
def message32():
	print _(" MB available space")
	return

def message33():
	print _(" MB needed space")
	return
	
def message34():
	print _("The program will abort, please try another medium with more free space to create your back-up.")
	return

def message35(): #IXUSS
	print _("To restore the image:")
	print _("Place USB stick in the USB slot at the back side and switch the receiver off and on with the powerswitch")
	print _("When message at display at front If you want to upgrade..., please quickly press UP button on remote control.")
	print _("When message reboot, power off and remove USB.")
	print _("Power on!")
	return

globals()[sys.argv[2]]()
os_environ["LANGUAGE"] = sys.argv[1]




