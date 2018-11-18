from schermen import *
import os
import gettext
import enigma
import glob
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Console import Console
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.FileList import FileList
from Components.Language import language
from Components.Harddisk import harddiskmanager
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from os import environ
import NavigationInstance
from Tools import Notifications
from enigma import getDesktop

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("BackupSuite", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/BackupSuite/locale"))

def _(txt):
	t = gettext.dgettext("BackupSuite", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

######################################################################################################
#Set default configuration

wherechoises = [('none', 'None'), ("/media/net", _("NAS"))]
for p in harddiskmanager.getMountedPartitions():
	d = os.path.normpath(p.mountpoint)
	if os.path.exists(p.mountpoint):
		if p.mountpoint != '/':
			wherechoises.append((d, p.mountpoint))

# Global variables
autoStartTimer = None
_session = None

##################################
# Configuration GUI

BACKUP_HDD = "/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/backuphdd.sh en_EN"
BACKUP_USB = "/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/backupusb.sh en_EN"
BACKUP_MMC = "/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/backupmmc.sh en_EN"
BACKUP_DMM_HDD = "/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/backuphdd-dmm.sh en_EN"
BACKUP_DMM_USB = "/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/backupusb-dmm.sh en_EN"
BACKUP_DMM_MMC = "/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/backupmmc-dmm.sh en_EN"
ofgwrite_bin = "/usr/bin/ofgwrite"
LOGFILE = "BackupSuite.log"
VERSIONFILE = "imageversion"
ENIGMA2VERSIONFILE = "/tmp/enigma2version"

with open("/var/lib/opkg/info/enigma2-plugin-extensions-backupsuite.control") as origin:
	for versie in origin:
		if not "Version: " in versie:
			continue
		try:
			versienummer = versie.split('+')[1]
		except IndexError:
			print

def backupCommandHDD():
	try:
		if os.path.exists(BACKUP_HDD):
			os.chmod(BACKUP_HDD, 0755)
	except:
		pass
	try:
		if os.path.exists(BACKUP_DMM_HDD):
			os.chmod(BACKUP_DMM_HDD, 0755)
	except:
		pass
	cmd = BACKUP_HDD
	for dvbmod in glob.glob('/etc/modules-load.d/*dreambox-dvb-modules-dm*.conf'):
		if os.path.exists(dvbmod):
			cmd = BACKUP_DMM_HDD
	return cmd

def backupCommandUSB():
	try:
		if os.path.exists(BACKUP_USB):
			os.chmod(BACKUP_USB, 0755)
	except:
		pass
	try:
		if os.path.exists(BACKUP_DMM_USB):
			os.chmod(BACKUP_DMM_USB, 0755)
	except:
		pass
	cmd = BACKUP_USB
	for dvbmod in glob.glob('/etc/modules-load.d/*dreambox-dvb-modules-dm*.conf'):
		if os.path.exists(dvbmod):
			cmd = BACKUP_DMM_USB
	return cmd

def backupCommandMMC():
	try:
		if os.path.exists(BACKUP_MMC):
			os.chmod(BACKUP_MMC, 0755)
	except:
		pass
	try:
		if os.path.exists(BACKUP_DMM_MMC):
			os.chmod(BACKUP_DMM_MMC, 0755)
	except:
		pass
	cmd = BACKUP_MMC
	for dvbmod in glob.glob('/etc/modules-load.d/*dreambox-dvb-modules-dm*.conf'):
		if os.path.exists(dvbmod):
			cmd = BACKUP_DMM_MMC
	return cmd

try:
	from Plugins.SystemPlugins.MPHelp import registerHelp, XMLHelpReader
	from Tools.Directories import resolveFilename, SCOPE_PLUGINS
	reader = XMLHelpReader(resolveFilename(SCOPE_PLUGINS, "Extensions/BackupSuite/mphelp.xml"))
	backupsuiteHelp = registerHelp(*reader)
except Exception as e:
	print("[BackupSuite] Unable to initialize MPHelp:", e,"- Help not available!")
	backupsuiteHelp = None

class BackupStart(Screen):
	def __init__(self, session, args = 0):
		try:
			sz_w = getDesktop(0).size().width()
		except:
			sz_w = 720
		if sz_w == 1920:
			self.skin = skinstartfullhd
		elif sz_w >= 1280:
			self.skin = skinstarthd
		else:
			self.skin = skinstartsd
		self.session = session
		self.setup_title = _("Make a backup or restore a backup")
		Screen.__init__(self, session)
		self["key_menu"] = Button(_("Backup > MMC"))
		self["key_red"] = Button(_("Close"))
		self["key_green"] = Button(_("Backup > HDD"))
		self["key_yellow"] = Button(_("Backup > USB"))
		self["key_blue"] = Button(_("Restore backup"))
		self["help"] = StaticText()
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "EPGSelectActions", "HelpActions"],
		{
			"menu": self.confirmmmc,
			"red": self.cancel,
			"green": self.confirmhdd,
			"yellow": self.confirmusb,
			"blue": self.flashimage,
			"info": self.keyInfo,
			"cancel": self.cancel,
			"displayHelp": self.showHelp,
			}, -2)
		self.setTitle(self.setup_title)

	def confirmhdd(self):
		self.session.openWithCallback(self.backuphdd, MessageBox, _("Do you want to make an USB-back-up image on HDD? \n\nThis only takes a few minutes and is fully automatic.\n") , MessageBox.TYPE_YESNO, timeout = 20, default = True)
		
	def confirmusb(self):
		self.session.openWithCallback(self.backupusb, MessageBox, _("Do you want to make a back-up on USB?\n\nThis only takes a few minutes depending on the used filesystem and is fully automatic.\n\nMake sure you first insert an USB flash drive before you select Yes.") , MessageBox.TYPE_YESNO, timeout = 20, default = True)

	def confirmmmc(self):
		self.session.openWithCallback(self.backupmmc, MessageBox, _("Do you want to make an USB-back-up image on MMC? \n\nThis only takes a few minutes and is fully automatic.\n") , MessageBox.TYPE_YESNO, timeout = 20, default = True)
		
	def showHelp(self):
		from plugin import backupsuiteHelp
		if backupsuiteHelp:
			backupsuiteHelp.open(self.session)

	def flashimage(self):
		model = ""
		files = "^.*\.(zip|bin)"
		if os.path.exists("/proc/stb/info/boxtype"):
			try:
				f = open("/proc/stb/info/boxtype")
				model = f.read().strip()
				f.close()
			except:
				pass
		elif os.path.exists("/proc/stb/info/vumodel"):
			try:
				f = open("/proc/stb/info/vumodel")
				model = f.read().strip()
				f.close()
			except:
				pass
		elif os.path.exists("/proc/stb/info/hwmodel"):
			try:
				f = open("/proc/stb/info/hwmodel")
				model = f.read().strip()
				f.close()
			except:
				pass
		elif os.path.exists("/proc/stb/info/gbmodel"):
			try:
				f = open("/proc/stb/info/gbmodel")
				model = f.read().strip()
				f.close()
			except:
				pass
		else:
			for dvbmod in glob.glob('/etc/modules-load.d/*dreambox-dvb-modules-dm*.conf'):
				if os.path.exists(dvbmod):
					try:
						f = open("/proc/stb/info/model")
						model = f.read().strip()
						f.close()
					except:
						pass
				else:
					return
		if model != "":
			if model in ["duo", "solo", "ultimo", "uno"] or "ebox" in model:
				files = "^.*\.(zip|bin|jffs2)"
			elif "4k" or "uhd" in model or model in ["hd51", "hd60", "h7", "sf4008", "sf5008", "sf8008", "u4", "u5", "u5pvr", "u51", "u52", "u53", "vs1500", "et11000", "et13000", "cc1"]:
				files = "^.*\.(zip|bin|bz2)"
			elif model in ["h9", "h9combo", "i55plus"]:
				files = "^.*\.(zip|bin|ubi)"
			elif model.startswith("dm"):
				self.session.open(MessageBox, _("No supported receiver found!"), MessageBox.TYPE_ERROR)
				return
			else:
				files = "^.*\.(zip|bin)"
		curdir = '/media/'
		self.session.open(FlashImageConfig, curdir, files)

	def cancel(self):
		self.close(False,self.session)

	def keyInfo(self):
		self.session.open(WhatisNewInfo)

	def writeEnigma2VersionFile(self):
		from Components.About import getEnigmaVersionString
		with open(ENIGMA2VERSIONFILE, 'wt') as f:
			f.write(getEnigmaVersionString())

	def backuphdd(self, ret = False ):
		if (ret == True):
			self.writeEnigma2VersionFile()
			text = _('Full back-up on HDD')
			cmd = backupCommandHDD()
			self.session.openWithCallback(self.consoleClosed,Console,text,[cmd])

	def backupusb(self, ret = False ):
		if (ret == True):
			self.writeEnigma2VersionFile()
			text = _('Full back-up to USB')
			cmd = backupCommandUSB()
			self.session.openWithCallback(self.consoleClosed,Console,text,[cmd])
			
	def backupmmc(self, ret = False ):
		if (ret == True):
			self.writeEnigma2VersionFile()
			text = _('Full back-up on MMC')
			cmd = backupCommandMMC()
			self.session.openWithCallback(self.consoleClosed,Console,text,[cmd])

	def consoleClosed(self, answer=None): 
		return

## What is new information
class WhatisNewInfo(Screen):
	def __init__(self, session):
		try:
			sz_w = getDesktop(0).size().width()
		except:
			sz_w = 720
		if sz_w == 1920:
			self.skin = skinnewfullhd
		elif sz_w >= 1280:
				self.skin = skinnewhd
		else:
			self.skin = skinnewsd
		Screen.__init__(self, session)
		self["Title"].setText(_("What is new since the last release?"))
		self["key_red"] = Button(_("Close"))
		self["AboutScrollLabel"] = ScrollLabel(_("Please wait"))
		self["actions"] = ActionMap(["SetupActions", "DirectionActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown
			})
		with open('/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/whatsnew.txt') as file:
			whatsnew = file.read()
		self["AboutScrollLabel"].setText(whatsnew)

class FlashImageConfig(Screen):
	def __init__(self, session, curdir, matchingPattern=None):
		try:
			sz_w = getDesktop(0).size().width()
		except:
			sz_w = 720
		if sz_w == 1920:
			self.skin = skinflashfullhd
		elif sz_w >= 1280:
			self.skin = skinflashhd
		else:
			self.skin = skinflashsd
		Screen.__init__(self, session)
		self["Title"].setText(_("Select the folder with backup"))
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText("")
		self["key_yellow"] = StaticText("")
		self["key_blue"] = StaticText("")
		self["curdir"] = StaticText(_("current:  %s")%(curdir or ''))
		self.founds = False
		self.dualboot = self.dualBoot()
		self.ForceMode = self.ForceMode()
		self.filelist = FileList(curdir, matchingPattern=matchingPattern, enableWrapAround=True)
		self.filelist.onSelectionChanged.append(self.__selChanged)
		self["filelist"] = self.filelist
		self["FilelistActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"green": self.keyGreen,
				"red": self.keyRed,
				"yellow": self.keyYellow,
				"blue": self.KeyBlue,
				"ok": self.keyOk,
				"cancel": self.keyRed
			})
		self.onLayoutFinish.append(self.__layoutFinished)

	def __layoutFinished(self):
		pass

	def dualBoot(self):
		if os.path.exists("/proc/stb/info/boxtype"):
			try:
				fd = open("/proc/stb/info/boxtype")
				model = fd.read().strip()
				fd.close()
				if model == "et8500":
					rootfs2 = False
					kernel2 = False
					f = open("/proc/mtd")
					l = f.readlines()
					for x in l:
						if 'rootfs2' in x:
							rootfs2 = True
						if 'kernel2' in x:
							kernel2 = True
					f.close()
					if rootfs2 and kernel2:
						return True
			except:
				pass
		return False

	def ForceMode(self):
		if os.path.exists("/proc/stb/info/hwmodel"):
			try:
				fd = open("/proc/stb/info/hwmodel")
				model = fd.read().strip()
				fd.close()
				if model in ["h9", "h9combo", "i55plus"]:
					return True
			except:
				pass
		elif os.path.exists("/proc/stb/info/boxtype"):
			try:
				fd = open("/proc/stb/info/boxtype")
				model = fd.read().strip()
				fd.close()
				if model in ["h9", "i55plus"]:
					return True
			except:
				pass
		return False

	def getCurrentSelected(self):
		dirname = self.filelist.getCurrentDirectory()
		filename = self.filelist.getFilename()
		if not filename and not dirname:
			cur = ''
		elif not filename:
			cur = dirname
		elif not dirname:
			cur = filename
		else:
			if not self.filelist.canDescent() or len(filename) <= len(dirname):
				cur = dirname
			else:
				cur = filename
		return cur or ''

	def __selChanged(self):
		self["key_yellow"].setText("")
		self["key_green"].setText("")
		self["key_blue"].setText("")
		self["curdir"].setText(_("current:  %s")%(self.getCurrentSelected()))
		file_name = self.getCurrentSelected()
		try:
			if not self.filelist.canDescent() and file_name != '' and file_name != '/':
				filename = self.filelist.getFilename()
				if filename and filename.endswith(".zip"):
					self["key_yellow"].setText(_("Unzip"))
			elif self.filelist.canDescent() and file_name != '' and file_name != '/':
				self["key_green"].setText(_("Run flash"))
				if os.path.isfile(file_name + LOGFILE) and os.path.isfile(file_name + VERSIONFILE):
					self["key_yellow"].setText(_("Backup info"))
					self["key_blue"].setText(_("Delete"))
		except:
			pass

	def keyOk(self):
		if self.filelist.canDescent():
			self.filelist.descent()

	def confirmedWarning(self, result):
		if result:
			self.founds = False
			self.showparameterlist()

	def keyGreen(self):
		if self["key_green"].getText() == _("Run flash"):
			dirname = self.filelist.getCurrentDirectory()
			if dirname:
				warning_text = "\n"
				if self.dualboot:
					warning_text += _("\nYou are using dual multiboot!")
				self.session.openWithCallback(lambda r: self.confirmedWarning(r), MessageBox, _("Warning!\nUse at your own risk! Make always a backup before use!\nDon't use it if you use multiple ubi volumes in ubi layer!")  + warning_text, MessageBox.TYPE_INFO)

	def showparameterlist(self):
		if self["key_green"].getText() == _("Run flash"):
			dirname = self.getCurrentSelected()
			if dirname:
				backup_files = []
				no_backup_files = []
				text = _("Select parameter for start flash!\n")
				text += _('For flashing your receiver files are needed:\n')
				if os.path.exists("/proc/stb/info/hwmodel"):
					try:
						f = open("/proc/stb/info/hwmodel")
						model = f.read().strip()
						f.close()
						if model in ["hd51", "hd60", "h7", "sf4008", "sf5008", "sf8008", "u4", "u5", "u5pvr", "u51", "u52", "u53", "vs1500", "et11000", "et13000", "bre2ze4k", "spycat4k", "spycat4kmini", "protek4k", "cc1"]:
							backup_files = [("kernel.bin"), ("rootfs.tar.bz2")]
							no_backup_files = [("kernel_cfe_auto.bin"), ("rootfs.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("kernel_auto.bin")]
							text += "kernel.bin, rootfs.tar.bz2"
						elif model in ["h9", "h9combo", "i55plus"]:
							backup_files = [("uImage"), ("rootfs.ubi")]
							no_backup_files = [("kernel_cfe_auto.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("rootfs.tar.bz2"), ("kernel_auto.bin"), ("kernel.bin"), ("rootfs.tar.bz2")]
							text += "uImage, rootfs.ubi"
						elif model.startswith(("et4", "et5", "et6", "et7", "et8", "et9", "et10")):
							backup_files = [("kernel.bin"), ("rootfs.bin")]
							no_backup_files = [("kernel_cfe_auto.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("rootfs.tar.bz2"), ("kernel_auto.bin")]
							text += "kernel.bin, rootfs.bin"
						elif "4k" or "uhd" in model:
							backup_files = [("oe_kernel.bin"), ("rootfs.tar.bz2")]
							no_backup_files = [("kernel_cfe_auto.bin"), ("rootfs.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("oe_rootfs.bin"), ("kernel.bin"), ("kernel_auto.bin")]
							text += "oe_kernel.bin, rootfs.tar.bz2"
						elif "ebox" in model:
							backup_files = [("kernel_cfe_auto.bin"), ("root_cfe_auto.jffs2")]
							no_backup_files = [("rootfs.bin"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("kernel.bin"), ("rootfs.tar.bz2"), ("kernel_auto.bin")]
							text += "kernel_cfe_auto.bin, root_cfe_auto.jffs2"
						elif model.startswith(("fusion", "pure", "optimus", "force", "iqon", "ios", "tm2", "tmn", "tmt", "tms", "lunix", "mediabox", "vala")):
							backup_files = [("oe_kernel.bin"), ("oe_rootfs.bin")]
							no_backup_files = [("kernel_cfe_auto.bin"), ("rootfs.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("kernel.bin"), ("rootfs.tar.bz2"), ("kernel_auto.bin")]
							text += "oe_kernel.bin, oe_rootfs.bin"
						else:
							backup_files = [("kernel.bin"), ("rootfs.bin")]
							no_backup_files = [("kernel_cfe_auto.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("rootfs.tar.bz2"), ("kernel_auto.bin")]
							text += "kernel.bin, rootfs.bin"
					except:
						pass
				elif os.path.exists("/proc/stb/info/gbmodel"):
					try:
						f = open("/proc/stb/info/gbmodel")
						model = f.read().strip()
						f.close()
						if not "4k" in model:
							backup_files = [("kernel.bin"), ("rootfs.bin")]
							no_backup_files = [("kernel_cfe_auto.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("rootfs.tar.bz2"), ("kernel_auto.bin")]
							text += "kernel.bin, rootfs.bin"
						else:
							backup_files = [("kernel.bin"), ("rootfs.tar.bz2")]
							no_backup_files = [("kernel_cfe_auto.bin"), ("rootfs.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("kernel_auto.bin")]
							text += "kernel.bin, rootfs.tar.bz2"
					except:
						pass
				elif os.path.exists("/proc/stb/info/boxtype"):
					try:
						f = open("/proc/stb/info/boxtype")
						model = f.read().strip()
						f.close()
						if model in ["hd51", "hd60", "h7", "sf4008", "sf5008", "sf8008", "u4", "u5", "u5pvr", "u51", "u52", "u53", "vs1500", "et11000", "et13000", "bre2ze4k", "spycat4k", "spycat4kmini", "protek4k", "cc1"]:
							backup_files = [("kernel.bin"), ("rootfs.tar.bz2")]
							no_backup_files = [("kernel_cfe_auto.bin"), ("rootfs.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("kernel_auto.bin")]
							text += "kernel.bin, rootfs.tar.bz2"
						elif model in ["h9", "h9combo", "i55plus"]:
							backup_files = [("uImage"), ("rootfs.ubi")]
							no_backup_files = [("kernel_cfe_auto.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("rootfs.tar.bz2"), ("kernel_auto.bin"), ("kernel.bin"), ("rootfs.tar.bz2")]
							text += "uImage, rootfs.ubi"
						elif model.startswith(("et4", "et5", "et6", "et7", "et8", "et9", "et10")):
							backup_files = [("kernel.bin"), ("rootfs.bin")]
							no_backup_files = [("kernel_cfe_auto.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("rootfs.tar.bz2"), ("kernel_auto.bin")]
							text += "kernel.bin, rootfs.bin"
						elif "4k" or "uhd" in model:
							backup_files = [("oe_kernel.bin"), ("rootfs.tar.bz2")]
							no_backup_files = [("kernel_cfe_auto.bin"), ("rootfs.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("oe_rootfs.bin"), ("kernel.bin"), ("kernel_auto.bin")]
							text += "oe_kernel.bin, rootfs.tar.bz2"
						elif "ebox" in model:
							backup_files = [("kernel_cfe_auto.bin"), ("root_cfe_auto.jffs2")]
							no_backup_files = [("rootfs.bin"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("kernel.bin"), ("rootfs.tar.bz2"), ("kernel_auto.bin")]
							text += "kernel_cfe_auto.bin, root_cfe_auto.jffs2"
						elif model.startswith(("fusion", "pure", "optimus", "force", "iqon", "ios", "tm2", "tmn", "tmt", "tms", "lunix", "mediabox", "vala")):
							backup_files = [("oe_kernel.bin"), ("oe_rootfs.bin")]
							no_backup_files = [("kernel_cfe_auto.bin"), ("rootfs.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("kernel.bin"), ("rootfs.tar.bz2"), ("kernel_auto.bin")]
							text += "oe_kernel.bin, oe_rootfs.bin"
						else:
							backup_files = [("kernel.bin"), ("rootfs.bin")]
							no_backup_files = [("kernel_cfe_auto.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("rootfs.tar.bz2"), ("kernel_auto.bin")]
							text += "kernel.bin, rootfs.bin"
					except:
						pass
				elif os.path.exists("/proc/stb/info/vumodel"):
					try:
						f = open("/proc/stb/info/vumodel")
						model = f.read().strip()
						f.close()
						if "4k" in model:
							backup_files = [("kernel_auto.bin"), ("rootfs.tar.bz2")]
							no_backup_files = [("kernel_cfe_auto.bin"), ("rootfs.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("kernel.bin")]
							text += "kernel_auto.bin, rootfs.tar.bz2"
						elif model in ["duo2", "solose", "solo2", "zero"]:
							backup_files = [("kernel_cfe_auto.bin"), ("root_cfe_auto.bin")]
							no_backup_files = [("rootfs.bin"), ("root_cfe_auto.jffs2"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("kernel.bin"), ("rootfs.tar.bz2"), ("kernel_auto.bin")]
							text += "kernel_cfe_auto.bin, root_cfe_auto.bin"
						else:
							backup_files = [("kernel_cfe_auto.bin"), ("root_cfe_auto.jffs2")]
							no_backup_files = [("rootfs.bin"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("kernel.bin"), ("rootfs.tar.bz2"), ("kernel_auto.bin")]
							text += "kernel_cfe_auto.bin, root_cfe_auto.jffs2"
					except:
						pass
				else:
					for dvbmod in glob.glob('/etc/modules-load.d/*dreambox-dvb-modules-dm*.conf'):
						if os.path.exists(dvbmod):
							try:
								f = open("/proc/stb/info/model")
								model = f.read().strip()
								f.close()
								if "dm9" in model:
									backup_files = [("kernel.bin"), ("rootfs.tar.bz2")]
									no_backup_files = [("kernel_cfe_auto.bin"), ("rootfs.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("kernel_auto.bin")]
									text += "kernel.bin, rootfs.tar.bz2"
								elif model in ["dm520", "dm525", "dm7080", "dm820"]:
									backup_files = [("*.xz")]
									no_backup_files = [("kernel_cfe_auto.bin"), ("rootfs.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("kernel_auto.bin"), ("kernel.bin"), ("rootfs.tar.bz2")]
									text += "*.xz"
								else:
									backup_files = [("*.nfi")]
									no_backup_files = [("kernel_cfe_auto.bin"), ("rootfs.bin"), ("root_cfe_auto.jffs2"), ("root_cfe_auto.bin"), ("oe_kernel.bin"), ("oe_rootfs.bin"), ("kernel_auto.bin"), ("kernel.bin"), ("rootfs.tar.bz2")]
									text += "*.nfi"
							except:
								pass
				try:
					self.founds = False
					text += _('\nThe found files:')
					for name in os.listdir(dirname):
						if name in backup_files:
							text += _("  %s (maybe ok)") % name
							self.founds = True
						if name in no_backup_files:
							text += _("  %s (maybe error)") % name
							self.founds = True
					if not self.founds:
						text += _(' nothing!')
				except:
					pass
				if self.founds:
					open_list = [
						(_("Simulate (no write)"), "simulate"),
						(_("Standard (root and kernel)"), "standard"),
						(_("Only root"), "root"),
						(_("Only kernel"), "kernel"),
					]
					open_list2 = [
						(_("Simulate second partition (no write)"), "simulate2"),
						(_("Second partition (root and kernel)"), "standard2"),
						(_("Second partition (only root)"), "rootfs2"),
						(_("Second partition (only kernel)"), "kernel2"),
					]
					if self.dualboot:
						open_list += open_list2
				else:
					open_list = [
						(_("Exit"), "exit"),
					]
				self.session.openWithCallback(self.Callbackflashing, MessageBox, text, simple = True, list = open_list)

	def Callbackflashing(self, ret):
		if ret:
			if ret == "exit":
				self.close()
				return
			if self.session.nav.RecordTimer.isRecording():
				self.session.open(MessageBox, _("A recording is currently running. Please stop the recording before trying to start a flashing."), MessageBox.TYPE_ERROR)
				self.founds = False
				return
			dir_flash = self.getCurrentSelected()
			text = _("Flashing: ")
			cmd = "echo -e"
			if ret == "simulate":
				text += _("Simulate (no write)")
				cmd = "%s -n '%s'" % (ofgwrite_bin, dir_flash)
			elif ret == "standard":
				text += _("Standard (root and kernel)")
				if self.ForceMode:
					cmd = "%s -f -r -k '%s' > /dev/null 2>&1 &" % (ofgwrite_bin, dir_flash)
				else:
					cmd = "%s -r -k '%s' > /dev/null 2>&1 &" % (ofgwrite_bin, dir_flash)
			elif ret == "root":
				text += _("Only root")
				cmd = "%s -r '%s' > /dev/null 2>&1 &" % (ofgwrite_bin, dir_flash)
			elif ret == "kernel":
				text += _("Only kernel")
				cmd = "%s -k '%s' > /dev/null 2>&1 &" % (ofgwrite_bin, dir_flash)
			elif ret == "simulate2":
				text += _("Simulate second partition (no write)")
				cmd = "%s -kmtd3 -rmtd4 -n '%s'" % (ofgwrite_bin, dir_flash)
			elif ret == "standard2":
				text += _("Second partition (root and kernel)")
				cmd = "%s -kmtd3 -rmtd4 '%s' > /dev/null 2>&1 &" % (ofgwrite_bin, dir_flash)
			elif ret == "rootfs2":
				text += _("Second partition (only root)")
				cmd = "%s -rmtd4 '%s' > /dev/null 2>&1 &" % (ofgwrite_bin, dir_flash)
			elif ret == "kernel2":
				text += _("Second partition (only kernel)")
				cmd = "%s -kmtd3 '%s' > /dev/null 2>&1 &" % (ofgwrite_bin, dir_flash)
			else:
				return
			message = "echo -e '\n"
			message += _('NOT found files for flashing!\n')
			message += "'"
			if ret == "simulate" or ret == "simulate2":
				if self.founds:
					message = "echo -e '\n"
					message += _('Show only found image and mtd partitions.\n')
					message += "'"
			else:
				if self.founds:
					message = "echo -e '\n"
					message += _('ofgwrite will stop enigma2 now to run the flash.\n')
					message += _('Your STB will freeze during the flashing process.\n')
					message += _('Please: DO NOT reboot your STB and turn off the power.\n')
					message += _('The image or kernel will be flashing and auto booted in few minutes.\n')
					message += "'"
			try:
				if os.path.exists(ofgwrite_bin):
					os.chmod(ofgwrite_bin, 0755)
			except:
				pass
			self.session.open(Console, text,[message, cmd])

	def keyRed(self):
		self.close()

	def keyYellow(self):
		if self["key_yellow"].getText() == _("Unzip"):
			filename = self.filelist.getFilename()
			if filename and filename.endswith(".zip"):
				self.session.openWithCallback(self.doUnzip, MessageBox, _("Do you really want to unpack %s ?") % filename, MessageBox.TYPE_YESNO)
		elif self["key_yellow"].getText() == _("Backup info"):
			self.session.open(MessageBox, "\n\n\n%s" % self.getBackupInfo(), MessageBox.TYPE_INFO)

	def getBackupInfo(self):
		backup_dir = self.getCurrentSelected()
		backup_info = ""
		for line in open(backup_dir + VERSIONFILE, "r"):
			backup_info += line
		return backup_info

	def doUnzip(self, answer):
		if answer is True:
			dirname = self.filelist.getCurrentDirectory()
			filename = self.filelist.getFilename()
			if dirname and filename:
				try:
					os.system('unzip -o %s%s -d %s'%(dirname,filename,dirname))
					self.filelist.refresh()
				except:
					pass

	def confirmedDelete(self, answer):
		if answer is True:
			backup_dir = self.getCurrentSelected()
			cmdmessage = "echo -e 'Removing backup:   %s\n'" % os.path.basename(backup_dir.rstrip('/'))
			cmddelete = "rm -rf %s > /dev/null 2>&1" % backup_dir
			self.session.open(Console, _("Delete backup"), [cmdmessage, cmddelete], self.filelist.refresh)

	def KeyBlue(self):
		if self["key_blue"].getText() == _("Delete"):
			self.session.openWithCallback(self.confirmedDelete, MessageBox, _("You are about to delete this backup:\n\n%s\nContinue?") % self.getBackupInfo(), MessageBox.TYPE_YESNO)

def main(session, **kwargs):
	session.open(BackupStart)


def Plugins(path,**kwargs):
	global plugin_path
	plugin_path = path
	return [
		PluginDescriptor(
		name=_("BackupSuite"),
		description = _("Backup and restore your image") + ", " + versienummer,
		where = PluginDescriptor.WHERE_PLUGINMENU,
		icon = 'plugin.png',
		fnc = main
		),
		PluginDescriptor(
		name =_("BackupSuite"), 
		description = _("Backup and restore your image") + ", " + versienummer,
		where = PluginDescriptor.WHERE_EXTENSIONSMENU, 
		fnc = main)
	]
