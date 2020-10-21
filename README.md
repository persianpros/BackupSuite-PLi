BackupSuite [![Build Status](https://travis-ci.org/OpenVisionE2/BackupSuite.svg?branch=master)](https://travis-ci.org/OpenVisionE2/BackupSuite) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
===========
Created by Pedro Newbie revamped by Persian Prince

Backup Suite (old generation) for enigma2 images (except Open Vision)

Ready bitbake recipe:

https://github.com/OpenPLi/openpli-oe-core/blob/develop/meta-openpli/recipes-openpli/enigma2-plugins/enigma2-plugin-extensions-backupsuite.bb

## kerneldev error
If you got this error:
```
cat: can't open '/sys/firmware/devicetree/base/chosen/kerneldev': No such file or directory
```
It means Backup Suite couldn't detect "/dev/mtd# or /dev/mmcblk0p#" of your kernel and needs to be added to the manual detection.

## lookuptable.txt
If you want to edit lookuptable.txt you need Notepad++/Notepadqq with Tab size 30
(Settings->Preferences->Languages)
