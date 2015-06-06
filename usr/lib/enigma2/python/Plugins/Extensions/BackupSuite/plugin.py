from schermen import skinstartfullhd, skinstarthd, skinstartsd, skinnewfullhd, skinnewhd, skinnewsd, skinflashfullhd, skinflashhd, skinflashsd
import os
import gettext
import enigma
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
from Tools.Directories import resolveFilename, fileExists, SCOPE_LANGUAGE, SCOPE_PLUGINS
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
ofgwrite_bin = "/usr/bin/ofgwrite"

def backupCommandHDD():
	cmd = BACKUP_HDD
	return cmd

def backupCommandUSB():
	cmd = BACKUP_USB
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
		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Backup > HDD"))
		self["key_yellow"] = Button(_("Backup > USB"))
		self["key_blue"] = Button(_("Restore backup"))
		self["help"] = StaticText()
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "EPGSelectActions", "HelpActions"],
		{
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

	def showHelp(self):
		from plugin import backupsuiteHelp
		if backupsuiteHelp:
			backupsuiteHelp.open(self.session)

	def flashimage(self):
		model = ""
		files = "^.*\.zip"
		if os.path.exists("/proc/stb/info/boxtype"):
			files = "^.*\.(zip|bin)"
		elif os.path.exists("/proc/stb/info/vumodel"):
			f = open("/proc/stb/info/vumodel")
			model = f.read().strip()
			f.close()
		else:
			return
		if model != "":
			if model == "solo2" or model == "duo2":
				files = "^.*\.(zip|bin|update)"
			else:
				files = "^.*\.(zip|bin|jffs2)"
		curdir = '/media/'
		self.session.open(FlashImageConfig, curdir, files)

	def cancel(self):
		self.close(False,self.session)

	def keyInfo(self):
		self.session.open(WhatisNewInfo)

	def backuphdd(self, ret = False ):
		if (ret == True):
			text = _('Full back-up on HDD')
			cmd = backupCommandHDD()
			self.session.openWithCallback(self.consoleClosed,Console,text,[cmd])

	def backupusb(self, ret = False ):
		if (ret == True):
			text = _('Full back-up to USB')
			cmd = backupCommandUSB()
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
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText("")
		self["key_yellow"] = StaticText("")
		self["curdir"] = StaticText(_("current:  %s")%(curdir or ''))
		self.founds = False
		self.filelist = FileList(curdir, matchingPattern=matchingPattern, enableWrapAround=True)
		self.filelist.onSelectionChanged.append(self.__selChanged)
		self["filelist"] = self.filelist

		self["FilelistActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"green": self.keyGreen,
				"red": self.keyRed,
				"yellow": self.keyYellow,
				"ok": self.keyOk,
				"cancel": self.keyRed
			})
		self.onLayoutFinish.append(self.__layoutFinished)

	def __layoutFinished(self):
		pass

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
		self["curdir"].setText(_("current:  %s")%(self.getCurrentSelected()))
		file_name = self.getCurrentSelected()
		try:
			if not self.filelist.canDescent() and file_name != '' and file_name != '/':
				filename = self.filelist.getFilename()
				if filename and filename.endswith(".zip"):
					self["key_yellow"].setText(_("Unzip"))
			elif self.filelist.canDescent() and file_name != '' and file_name != '/':
				self["key_green"].setText(_("Run flash"))
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
				self.session.openWithCallback(lambda r: self.confirmedWarning(r), MessageBox, _("Warning!\nUse at your own risk! Make always a backup before use!\nDon't use it if you use multiple ubi volumes in ubi layer!") , MessageBox.TYPE_INFO)

	def showparameterlist(self):
		if self["key_green"].getText() == _("Run flash"):
			dirname = self.getCurrentSelected()
			if dirname:
				backup_files = []
				no_backup_files = []
				text = _("Select parameter for start flash!\n")
				text += _('For flashing your receiver files are needed:\n')
				if os.path.exists("/proc/stb/info/boxtype"):
					backup_files = [("kernel.bin"), ("rootfs.bin")]
					no_backup_files = ["kernel_cfe_auto.bin", "root_cfe_auto.jffs2", "root_cfe_auto.bin"]
					text += 'kernel.bin, rootfs.bin'
				elif os.path.exists("/proc/stb/info/vumodel"):
					f = open("/proc/stb/info/vumodel")
					model = f.read().strip()
					f.close()
					if model in ["solo2", "duo2"]:
						backup_files = ["kernel_cfe_auto.bin", "root_cfe_auto.bin"]
						no_backup_files = ["kernel.bin", "root_cfe_auto.jffs2", "rootfs.bin"]
						text += 'kernel_cfe_auto.bin, root_cfe_auto.bin'
					else:
						backup_files = ["kernel_cfe_auto.bin", "root_cfe_auto.jffs2"]
						no_backup_files = ["kernel.bin", "root_cfe_auto.bin", "rootfs.bin"]
						text += 'kernel_cfe_auto.bin, root_cfe_auto.jffs2'
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
						(_("Standard (root and kernel)"), "Standard"),
						(_("Only root"), "root"),
						(_("Only kernel"), "kernel"),
						(_("Only root with use mtdy device"), "mtdy"),
						(_("Only kernel with use mtdx device"), "mtdx"),
					]
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
			elif ret == "Standard":
				text += _("Standard (root and kernel)")
				cmd = "%s -r -k '%s' > /dev/null 2>&1 &" % (ofgwrite_bin, dir_flash)
			elif ret == "root":
				text += _("Only root")
				cmd = "%s -r '%s' > /dev/null 2>&1 &" % (ofgwrite_bin, dir_flash)
			elif ret == "kernel":
				text += _("Only kernel")
				cmd = "%s -k '%s' > /dev/null 2>&1 &" % (ofgwrite_bin, dir_flash)
			elif ret == "mtdy":
				text += _("Only root with use mtdy device")
				cmd = "%s -rmtdy '%s' > /dev/null 2>&1 &" % (ofgwrite_bin, dir_flash)
			elif ret == "mtdx":
				text += _("Only kernel with use mtdx device")
				cmd = "%s -kmtdx '%s' > /dev/null 2>&1 &" % (ofgwrite_bin, dir_flash)
			else:
				return
			message = "echo -e '\n"
			message += _('NOT found files for flashing!\n')
			message += "'"
			if ret != "simulate":
				if self.founds:
					message = "echo -e '\n"
					message += _('ofgwrite will stop enigma2 now to run the flash.\n')
					message += _('Your STB will freeze during the flashing process.\n')
					message += _('Please: DO NOT reboot your STB and turn off the power.\n')
					message += _('The image or kernel will be flashing and auto booted in few minutes.\n')
					message += "'"
			else:
				if self.founds:
					message = "echo -e '\n"
					message += _('Show only found image and mtd partitions.\n')
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

def main(session, **kwargs):
	session.open(BackupStart)


def Plugins(path,**kwargs):
	from os import path
	if path.exists("/proc/stb/info/boxtype") or path.exists("/proc/stb/info/vumodel"):
		return [
			PluginDescriptor(
			name=_("BackupSuite"),
			description = _("Enables back-up & restore without an USB-stick"),
			where = PluginDescriptor.WHERE_PLUGINMENU,
			icon = 'plugin.png',
			fnc = main
			),
			PluginDescriptor(
			name =_("BackupSuite"), 
			description = _("Enables back-up & restore without an USB-stick"),
			where = PluginDescriptor.WHERE_EXTENSIONSMENU, 
			fnc = main)
		]

