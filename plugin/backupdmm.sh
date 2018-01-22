#       FULL BACKUP UYILITY FOR ENIGMA2/OPENPLI, SUPPORTS VARIOUS MODELS      #
#                   MAKES A FULLBACK-UP READY FOR FLASHING.                   #
#                                                                             #
###############################################################################
#
#!/bin/sh

## ADD A POSTRM ROUTINE TO ENSURE A CLEAN UNINSTALL
## This is normally added while building but despite several requests it isn't added yet
## So therefore this workaround.
POSTRM="/var/lib/opkg/info/enigma2-plugin-extensions-backupsuite.postrm"
if [ ! -f $POSTRM ] ; then
	echo "#!/bin/sh" > "$POSTRM"
	echo "rm -rf /usr/lib/enigma2/python/Plugins/Extensions/BackupSuite" >> "$POSTRM"
	echo 'echo "Plugin removed!"' >> "$POSTRM"
	echo "exit 0" >> "$POSTRM"
	chmod 755 "$POSTRM"
fi
## END WORKAROUND

##TESTING IF PROGRAM IS RUN FROM COMMANDLINE OR CONSOLE, JUST FOR THE COLORS ##
if tty > /dev/null ; then		# Commandline
	RED='-e \e[00;31m'
	GREEN='-e \e[00;32m'
	YELLOW='-e \e[01;33m'
	BLUE='-e \e[01;34m'
	PURPLE='-e \e[01;31m'
	WHITE='-e \e[00;37m'
else							# On the STB
	RED='\c00??0000'
	GREEN='\c0000??00'
	YELLOW='\c00????00'
	BLUE='\c0000????'
	PURPLE='\c00?:55>7'   
	WHITE='\c00??????'
fi
###################### FIRST DEFINE SOME PROGRAM BLOCKS #######################
############################# START LOGGING ###################################
log()
{
echo "$*" >> $LOGFILE
}
########################## DEFINE CLEAN-UP ROUTINE ############################
clean_up()
{
umount /tmp/bi/root > /dev/null 2>&1
rmdir /tmp/bi/root > /dev/null 2>&1
rmdir /tmp/bi > /dev/null 2>&1
rm -rf "$WORKDIR" > /dev/null 2>&1
}
###################### BIG OOPS!, HOLY SH... (SHELL SCRIPT :-))################
big_fail()
{
if [ -d $WORKDIR ] ; then 
	log "FAIL!"
	log "Content so far of the working directory $WORKDIR "
	ls -el $WORKDIR >> $LOGFILE
fi
clean_up
echo $RED
$SHOW "message15" 2>&1 | tee -a $LOGFILE # Image creation FAILED!
echo $WHITE
exit 0
}
############################ DEFINE IMAGE_VERSION #############################
image_version()
{
echo "Back-up = $BACKUPDATE"
echo "Version = $IMVER"
echo "Flashed = $FLASHED"
echo "Updated = $LASTUPDATE"
echo -n "Drivers = "
opkg list-installed | grep dvb-modules
echo "Enigma2 = $ENIGMA2DATE"
echo 
echo $LINE
}
#################### CLEAN UP AND MAKE DESTINATION FOLDERS ####################
make_folders()
{
rm -rf "$MAINDEST"
log "Removed directory  = $MAINDEST"
mkdir -p "$MAINDEST"
log "Created directory  = $MAINDEST"
}
################ CHECK FOR THE NEEDED BINARIES IF THEY EXIST ##################
checkbinary()
{
if [ ! -f "$1" ] ; then {
	echo -n "$1 " ; $SHOW "message05"
	} 2>&1 | tee -a $LOGFILE
	big_fail
elif [ ! -x "$1" ] ; then
	{
	echo "Error: $1 " ; $SHOW "message35"
	} 2>&1 | tee -a $LOGFILE
	big_fail
fi
}
############## CHECK FOR THE NEEDED DEPENDENCIES IF THEY EXIST ################
check_dependency(){
   log "Checking Dependencies ..."
   UPDATE=0
   for pkg in mtd-utils mtd-utils-ubifs mtd-utils-jffs2 dreambox-buildimage;
   do   
      opkg status $pkg | grep -q "install user installed"
      if [ $? -ne 0 ] ; then
         [ $UPDATE -eq 0 ] && opkg update && UPDATE=1
         opkg install $pkg 2>/dev/null
      fi
   done
}
################### BACK-UP MADE AND REPORTING SIZE ETC. ######################
backup_made()
{
{
echo $LINE
$SHOW "message10" ; echo "$MAINDEST" 	# USB Image created in: 
$SHOW "message23"		# "The content of the folder is:"
ls "$MAINDEST" -e1rSh | sed 's/-.........    1//' 
echo $LINE
if  [ $HARDDISK != 1 ]; then
	$SHOW "message11" ; echo "$EXTRA"		# and there is made an extra copy in:
	echo $LINE
fi
} 2>&1 | tee -a $LOGFILE
}
############################## END PROGRAM BLOCKS #############################


########################## DECLARATION OF VARIABLES ###########################
BACKUPDATE=`date +%Y.%m.%d_%H:%M`
DATE=`date +%Y%m%d_%H%M`
if [ -f "/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/speed.txt" ] ; then
	ESTSPEED=`cat /usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/speed.txt`
	if [ $ESTSPEED -lt 50 ] ; then 
		ESTSPEED="250"
	fi
else
	ESTSPEED="250"
fi
FLASHED=`date -r /etc/version +%Y.%m.%d_%H:%M`
ISSUE=`cat /etc/issue | grep . | tail -n 1 ` 
IMVER=${ISSUE%?????}
LASTUPDATE=`date -r /var/lib/opkg/status +%Y.%m.%d_%H:%M`
ENIGMA2DATE=`cat /tmp/enigma2version`
LOGFILE=/tmp/BackupSuite.log
MEDIA="$1"
MKFS=/usr/sbin/mkfs.ubifs
MKFSJFFS2=/usr/sbin/mkfs.jffs2
BUILDIMAGE=/usr/bin/buildimage
MTDPLACE=`cat /proc/mtd | grep -w "kernel" | cut -d ":" -f 1`
NANDDUMP=/usr/sbin/nanddump
START=$(date +%s)
if [ -f "/etc/lookuptable.txt" ] ; then
	LOOKUP="/etc/lookuptable.txt"
	$SHOW "message36"
else
	LOOKUP="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/lookuptable.txt"
fi
TARGET="XX"
UBINIZE=/usr/sbin/ubinize
USEDsizebytes=`df -B 1 /usr/ | grep [0-9]% | tr -s " " | cut -d " " -f 3`
USEDsizekb=`df -k /usr/ | grep [0-9]% | tr -s " " | cut -d " " -f 3` 
if [ -f "/var/lib/opkg/info/enigma2-plugin-extensions-backupsuite.control" ] ; then
	VERSION="Version: "`cat /var/lib/opkg/info/enigma2-plugin-extensions-backupsuite.control | grep "Version: " | cut -d "+" -f 2`
else
	VERSION=`$SHOW "message37"`
fi
WORKDIR="$MEDIA/bi"

######################### START THE LOGFILE $LOGFILE ##########################
echo -n "" > $LOGFILE
log "*** THIS BACKUP IS CREATED WITH THE PLUGIN BACKUPSUITE ***"
log "***** ********************************************* ******"
log $LINE
log "Plugin version     = "`cat /var/lib/opkg/info/enigma2-plugin-extensions-backupsuite.control | grep "Version: " | cut -d "+" -f 2- | cut -d "-" -f1`
log "Back-up media      = $MEDIA"
df -h "$MEDIA"  >> $LOGFILE
log $LINE
image_version >> $LOGFILE
log "Working directory  = $WORKDIR"

###### TESTING IF ALL THE BINARIES FOR THE BUILDING PROCESS ARE PRESENT #######
echo $RED
check_dependency
checkbinary $NANDDUMP
checkbinary $MKFS
checkbinary $MKFSJFFS2
checkbinary $BUILDIMAGE
checkbinary $UBINIZE
echo -n $WHITE

#############################################################################
# TEST IF RECEIVER IS SUPPORTED AND READ THE VARIABLES FROM THE LOOKUPTABLE #
if [ -f /proc/stb/info/model ] ; then
	SEARCH=$( cat /proc/stb/info/model )

else
	echo $RED
	$SHOW "message01" 2>&1 | tee -a $LOGFILE # No supported receiver found!
	big_fail
fi
log "Destination        = $MAINDEST"
log $LINE

############# START TO SHOW SOME INFORMATION ABOUT BRAND & MODEL ##############
echo -n $PURPLE
echo -n "$SHOWNAME " | tr  a-z A-Z		# Shows the receiver brand and model
$SHOW "message02"  			# BACK-UP TOOL FOR MAKING A COMPLETE BACK-UP 
echo $BLUE
log "RECEIVER = $SHOWNAME "
log "MKUBIFS_ARGS = $MKUBIFS_ARGS"
log "UBINIZE_ARGS = $UBINIZE_ARGS"
echo "$VERSION"
echo $WHITE

# athoik's code #

CREATE_ZIP="$2"
IMAGENAME="$3"

cleanup_mounts(){
   if [ ! -z "$TBI" ] ; then
      if [ -d "$TBI/boot" ] ; then
         if grep -q "$TBI/boot" /proc/mounts ; then 
            umount "$TBI/boot" 2>/dev/null || log "Cannot umount boot" && exit 6
         fi
         rmdir "$TBI/boot" 2>/dev/null
      fi
      if [ -d "$TBI/root" ] ; then
         if grep -q "$TBI/root" /proc/mounts ; then
            umount "$TBI/root" 2>/dev/null || log "Cannot umount root" && exit 7
         fi
         rmdir "$TBI/root" 2>/dev/null
      fi
   fi
}

control_c(){
   log "Control C was pressed, quiting..."
   cleanup_mounts
   rm -rf "$SBI" 2>/dev/null
   rm -rf "$TBI" 2>/dev/null
   exit 255
}

trap control_c SIGINT

#
# Read Dreambox Model
#
MACHINE="$(cat /proc/stb/info/model)"
log "Found Dreambox $MACHINE ..."

#
# Set Backup Location
#
BACKUP_LOCATION=""

if [ -z $1 ] ; then 
   if [ -d /media/usb ] && df /media/usb 1>/dev/null 2>/dev/null ; then
      BACKUP_LOCATION="/media/usb"
   elif [ -d /media/hdd ] && df /media/hdd 1>/dev/null 2>/dev/null ; then
      BACKUP_LOCATION="/media/hdd"
   else
      log "Error: Backup Location not found!"
      exit 2
   fi
elif [ -d $1 ] && [ $1 != "/" ] && df $1 1>/dev/null 2>/dev/null ; then
    BACKUP_LOCATION=$1
else
   log "Error: Invalid Backup Location $1"
   exit 2
fi
log "Backup on $BACKUP_LOCATION"

EXTRA="$BACKUP_LOCATION/automatic_fullbackup/$DATE"
MAINDEST="$BACKUP_LOCATION/$MACHINE"

SBI="$BACKUP_LOCATION/bi"
TBI="/tmp/bi"
#
# Initialize Parameters
#
EXTRA_BUILDCMD=""
EXTRA_IMAGECMD=""

DREAMBOX_ERASE_BLOCK_SIZE=""
DREAMBOX_FLASH_SIZE=""
DREAMBOX_SECTOR_SIZE=""
MKUBIFS_ARGS=""
UBINIZE_ARGS=""

UBINIZE_VOLSIZE="0"
UBINIZE_DATAVOLSIZE="0"
UBI_VOLNAME="rootfs"

DREAMBOX_IMAGE_SIZE=""
DREAMBOX_PART0_SIZE=""
DREAMBOX_PART1_SIZE=""
DREAMBOX_PART2_SIZE=""

#
# Set parameters based on box
# dm7020hdv2 is recognized from /sys/devices/virtual/mtd/mtd0/writesize
# No support for xz images: dm520,dm7080,dm820
# No support for bz2 images: dm900,dm920
case $MACHINE in
   dm800|dm500hd|dm800se)
      EXTRA_BUILDCMD="--brcmnand"
      DREAMBOX_ERASE_BLOCK_SIZE="0x4000"
      DREAMBOX_FLASH_SIZE="0x4000000"
      DREAMBOX_SECTOR_SIZE="512"
      MKUBIFS_ARGS="-m 512 -e 15KiB -c 3798 -x favor_lzo -X 1 -F -j 4MiB"
      UBINIZE_ARGS="-m 512 -p 16KiB -s 512"
      DREAMBOX_IMAGE_SIZE="64"
      DREAMBOX_PART0_SIZE="0x40000"
      DREAMBOX_PART1_SIZE="0x3C0000"
      DREAMBOX_PART2_SIZE="0x3C00000"
      ;;
   dm500hdv2|dm800sev2|dm7020hdv2)
      EXTRA_BUILDCMD="--hw-ecc --brcmnand"
      DREAMBOX_ERASE_BLOCK_SIZE="0x20000"
      DREAMBOX_FLASH_SIZE="0x40000000"
      DREAMBOX_SECTOR_SIZE="2048"
      MKUBIFS_ARGS="-m 2048 -e 124KiB -c 3320 -x favor_lzo -F"
      UBINIZE_ARGS="-m 2048 -p 128KiB -s 2048"
      UBINIZE_VOLSIZE="402MiB"
      UBINIZE_DATAVOLSIZE="569MiB"
      DREAMBOX_IMAGE_SIZE="1024"
      DREAMBOX_PART0_SIZE="0x100000"
      DREAMBOX_PART1_SIZE="0x700000"
      DREAMBOX_PART2_SIZE="0x3F800000"
      ;;
   dm7020hd)
      EXTRA_BUILDCMD="--hw-ecc --brcmnand"
      DREAMBOX_ERASE_BLOCK_SIZE="0x40000"
      DREAMBOX_FLASH_SIZE="0x40000000"
      DREAMBOX_SECTOR_SIZE="4096"
      MKUBIFS_ARGS="-m 4096 -e 248KiB -c 1640 -x favor_lzo -F"
      UBINIZE_ARGS="-m 4096 -p 256KiB -s 4096"
      UBINIZE_VOLSIZE="397MiB"
      UBINIZE_DATAVOLSIZE="574MiB"
      DREAMBOX_IMAGE_SIZE="1024"
      DREAMBOX_PART0_SIZE="0x100000"
      DREAMBOX_PART1_SIZE="0x700000"
      DREAMBOX_PART2_SIZE="0x3F800000"

      # dm7020hdv2 when writesize = 2048
      WRITESIZE="4096"
      if [ -f /sys/devices/virtual/mtd/mtd0/writesize ] ; then 
         WRITESIZE=$(cat /sys/devices/virtual/mtd/mtd0/writesize)
      fi
      if [ $WRITESIZE = "2048" ] ; then
         log "Found version2 of dm7020hd..."
         DREAMBOX_ERASE_BLOCK_SIZE="0x20000"
         DREAMBOX_SECTOR_SIZE="2048"
         MKUBIFS_ARGS="-m 2048 -e 124KiB -c 3320 -x favor_lzo -F"
         UBINIZE_ARGS="-m 2048 -p 128KiB -s 2048"
         UBINIZE_VOLSIZE="402MiB"
         UBINIZE_DATAVOLSIZE="569MiB"
      fi
      ;;
   dm8000)
      EXTRA_BUILDCMD=""
      DREAMBOX_ERASE_BLOCK_SIZE="0x20000"
      DREAMBOX_FLASH_SIZE="0x10000000"
      DREAMBOX_SECTOR_SIZE="2048"
      MKUBIFS_ARGS="-m 2048 -e 126KiB -c 1961 -x favor_lzo -F"
      UBINIZE_ARGS="-m 2048 -p 128KiB -s 512"
      DREAMBOX_IMAGE_SIZE="256"
      DREAMBOX_PART0_SIZE="0x100000"
      DREAMBOX_PART1_SIZE="0x700000"
      DREAMBOX_PART2_SIZE="0xF800000"
      ;;
   *)
      log "Error: Unknown dreambox?"
      exit 3
      ;;
esac

EXTRA_IMAGECMD="-e $DREAMBOX_ERASE_BLOCK_SIZE -n -l"

#
# Setup temporary files and variables
#
SECSTAGE="$SBI/secondstage.bin"
UBINIZE_CFG="$TBI/ubinize.cfg"
BOOT="$SBI/boot.jffs2"
ROOTFS="$SBI/rootfs.jffs2"

cleanup_mounts

echo "Starting Full Backup!\nOptions control panel will not be available 2-15 minutes.\nPlease wait ..."
echo "--------------------------\n"

echo "\nWARNING!\n"
echo "To stop creating a backup, press the 'Menu' button.\n"
sleep 2

rm -rf "$SBI" 2>/dev/null
rm -rf "$TBI" 2>/dev/null
mkdir -p "$SBI"
mkdir -p "$TBI"

#
# Export secondstage
#
log "Exporting secondstage"
/usr/sbin/nanddump --noecc --omitoob --bb=skipbad --file="$SECSTAGE" /dev/mtd1
if [ $? -ne 0 ] && [ ! -f "$SECSTAGE" ] ; then
   rm -rf "$SBI" 2>/dev/null
   rm -rf "$TBI" 2>/dev/null
   log "Error: nanddump failed to dump secondstage!"
   exit 8
fi

#
# Trim 0xFFFFFF from secondstage
#
/usr/bin/python -c "
data=open('$SECSTAGE', 'rb').read()
cutoff=data.find('\xff\xff\xff\xff')
if cutoff:
    open('$SECSTAGE', 'wb').write(data[0:cutoff])
"

SIZE="$(du -k "$SECSTAGE" | awk '{ print $1 }')"
if [ $SIZE -gt 200 ] ; then 
   log "Error: Size of secondstage must be less than 200k"
   log "Reinstall secondstage before creating backup"
   log "opkg install --force-reinstall dreambox-secondstage-$MACHINE"
   rm -rf "$SBI" 2>/dev/null
   rm -rf "$TBI" 2>/dev/null
   exit 9
fi

#
# Export boot partition
#
log "Exporting boot partition"
mkdir -p "$TBI/boot"
mount -t jffs2 /dev/mtdblock/2 "$TBI/boot"

/usr/sbin/mkfs.jffs2 \
   --root="$TBI/boot" \
   --compression-mode=none \
   --output="$BOOT" \
   $EXTRA_IMAGECMD

umount "$TBI/boot" 2>/dev/null

#
# Export root partition
#
if grep -q ubi0:rootfs /proc/mounts ; then

   log "Exporting rootfs (UBI)"
   ROOTFS="$SBI/rootfs.ubi"
   ROOTUBIFS="$SBI/rootfs.ubifs"
   mkdir -p "$TBI/root"
   mount --bind / "$TBI/root"

   echo [root] > $UBINIZE_CFG
   echo mode=ubi >> $UBINIZE_CFG
   echo image=$ROOTUBIFS >> $UBINIZE_CFG
   echo vol_id=0 >> $UBINIZE_CFG
   echo vol_name=$UBI_VOLNAME >> $UBINIZE_CFG
   echo vol_type=dynamic >> $UBINIZE_CFG
   if [ "$UBINIZE_VOLSIZE" = "0" ] ; then
      echo vol_flags=autoresize >> $UBINIZE_CFG
   else
      echo vol_size=$UBINIZE_VOLSIZE >> $UBINIZE_CFG
      if [ "$UBINIZE_DATAVOLSIZE" != "0" ] ; then
         echo [data] >> $UBINIZE_CFG
         echo mode=ubi >> $UBINIZE_CFG
         echo vol_id=1 >> $UBINIZE_CFG
         echo vol_type=dynamic >> $UBINIZE_CFG
         echo vol_name=data >> $UBINIZE_CFG
         echo vol_size=$UBINIZE_DATAVOLSIZE >> $UBINIZE_CFG
         echo vol_flags=autoresize >> $UBINIZE_CFG
      fi
   fi

   /usr/sbin/mkfs.ubifs -r "$TBI/root" -o $ROOTUBIFS $MKUBIFS_ARGS
   log "mkfs.ubifs return value: $?"
   /usr/sbin/ubinize -o $ROOTFS $UBINIZE_ARGS $UBINIZE_CFG
   log "ubinize return value: $?"

   umount "$TBI/root" 2>/dev/null
else
   log "Export rootfs (JFFS2)"
   mkdir -p "$TBI/root"
   mount -t jffs2 /dev/mtdblock/3 "$TBI/root"

   /usr/sbin/mkfs.jffs2 \
      --root="$TBI/root" \
      --disable-compressor=lzo \
      --compression-mode=size \
      --output=$ROOTFS \
      $EXTRA_IMAGECMD
   log "mkfs.jffs2 return value: $?"
   umount "$TBI/root" 2>/dev/null
fi

#
# Build NFI image
#
log "Building NFI image"
/usr/bin/buildimage --arch $MACHINE $EXTRA_BUILDCMD \
   --erase-block-size $DREAMBOX_ERASE_BLOCK_SIZE \
   --flash-size $DREAMBOX_FLASH_SIZE \
   --sector-size $DREAMBOX_SECTOR_SIZE \
   --boot-partition $DREAMBOX_PART0_SIZE:$SECSTAGE \
   --data-partition $DREAMBOX_PART1_SIZE:$BOOT \
   --data-partition $DREAMBOX_PART2_SIZE:$ROOTFS \
   > "$SBI/backup.nfi"

#
# Archive NFI image
#
log "Transfering image to backup folder"
TSTAMP="$(date "+%Y-%m-%d-%Hh%Mm")"
rm -rf "$MAINDEST" 2>/dev/null

mkdir -p "$MAINDEST"
NFI="$MAINDEST/$TSTAMP-$MACHINE.nfi"
mv "$SBI/backup.nfi" "$NFI"
log "Backup image created $NFI"
log "$(du -h $NFI)"

if [ -z "$CREATE_ZIP" ] ; then
   mkdir -p "$EXTRA"
   touch "$NFI/$IMVER"
   cp -r "$NFI" "$EXTRA"
   touch "$BACKUP_LOCATION/fullbackup/.timestamp"
else
   if [ $CREATE_ZIP != "none" ] ; then
      log "Create zip archive..."
      cd $BACKUP_LOCATION && $CREATE_ZIP -r $BACKUP_LOCATION/backup-$IMAGENAME-$MACHINE-$TSTAMP.zip . -i /$MACHINE/*
      cd
   fi
fi

#
# Cleanup
#
log "Remove temporary files..."
cleanup_mounts
rm -rf "$SBI" 2>/dev/null
rm -rf "$TBI" 2>/dev/null

if [ -f "$NFI" ] ; then
	echo " "
	echo "BACK-UP MADE SUCCESSFULLY IN: $MAINDEST\n"
else
	echo " "
	echo "Image creation FAILED!\n"
fi
#
# The End
#
log "Completed!"
sleep 3
END=$(date +%s)
DIFF=$(( $END - $START ))
MINUTES=$(( $DIFF/60 ))
SECONDS=$(( $DIFF-(( 60*$MINUTES ))))
if [ $SECONDS -le  9 ] ; then 
	SECONDS="0$SECONDS"
fi
echo "BACKUP FINISHED IN $MINUTES.$SECONDS MINUTES\n"
exit 0
