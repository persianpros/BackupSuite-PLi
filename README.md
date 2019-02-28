Backup Suite
===========
Created by Pedro Newbie

Maintainer : Persian Prince

Backup Suite for enigma2 images

Ready bitbake recipe:

https://github.com/OpenPLi/openpli-oe-core/blob/develop/meta-openpli/recipes-openpli/enigma2-plugins/enigma2-plugin-extensions-backupsuite.bb

For Dreambox you need:

https://github.com/OpenVisionE2/openvision-oe/blob/develop/recipes-openpli/enigma2-plugins/enigma2-plugin-extensions-backupsuite.bbappend

## kerneldev error:
If you got this error:
```
cat: can't open '/sys/firmware/devicetree/base/chosen/kerneldev': No such file or directory
```
It means Backup Suite couldn't detect "/dev/mtd# or /dev/mmcblk0p#" of your kernel and you need to tell us your machine name so we could add it to manual detection.
