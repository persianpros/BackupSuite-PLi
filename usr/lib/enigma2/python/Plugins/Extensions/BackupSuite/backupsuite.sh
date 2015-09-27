#       FULL BACKUP UYILITY FOR ENIGMA2/OPENPLI, SUPPORTS VARIOUS MODELS      #
#                   MAKES A FULLBACK-UP READY FOR FLASHING.                   #
#                   Pedro_Newbie (backupsuite@outlook.com)                    #
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
	echo "Error: $1 is not executable..."
	} 2>&1 | tee -a $LOGFILE
	big_fail
fi
}
################### BACK-UP MADE AND REPORTING SIZE ETC. ######################
backup_made()
{
{
echo $LINE
$SHOW "message10" ; echo "$MAINDEST" 	# USB Image created in: 
$SHOW "message23"		# "The content of the folder is:"
ls "$MAINDEST" -e1rSh | sed 's/-r.....r..    1//' 
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
LOGFILE=/tmp/BackupSuite.log
MEDIA="$1"
MKFS=/usr/sbin/mkfs.ubifs
MTDPLACE=`cat /proc/mtd | grep -w "kernel" | cut -d ":" -f 1`
NANDDUMP=/usr/sbin/nanddump
START=$(date +%s)
LOOKUP="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/lookuptable.txt"
TARGET="XX"
UBINIZE=/usr/sbin/ubinize
USEDsizebytes=`df -B 1 /usr/ | grep [0-9]% | tr -s " " | cut -d " " -f 3`
USEDsizekb=`df -k /usr/ | grep [0-9]% | tr -s " " | cut -d " " -f 3` 
if [ -f "/var/lib/opkg/info/enigma2-plugin-extensions-backupsuite.control" ] ; then
	VERSION="Version: "`cat /var/lib/opkg/info/enigma2-plugin-extensions-backupsuite.control | grep "Version: " | cut -d " " -f 2 | cut -d "+" -f2`
else
	VERSION="Version unknown, probably not installed the right way."
fi
WORKDIR="$MEDIA/bi"

######################### START THE LOGFILE $LOGFILE ##########################
echo -n "" > $LOGFILE
log "*** THIS BACKUP IS CREATED WITH THE PLUGIN BACKUPSUITE ***"
log "***** This plugin is brought to you by Pedro_Newbie ******"
log $LINE
log "Plugin version     = "`cat /var/lib/opkg/info/enigma2-plugin-extensions-backupsuite.control | grep "Version: " | cut -d "+" -f 2- | cut -d "-" -f1`
log "Back-up media      = $MEDIA"
df -h "$MEDIA"  >> $LOGFILE
log $LINE
image_version >> $LOGFILE
log "Working directory  = $WORKDIR"

######################### TESTING FOR UBIFS OR JFFS2 ##########################
grep rootfs /proc/mounts | grep -q ubifs 
if [ "$?" = 1 ] ; then
	echo $RED
	$SHOW "message01" 2>&1 | tee -a $LOGFILE #NO UBIFS, THEN JFFS2 BUT NOT SUPPORTED ANYMORE
	big_fail
fi

###### TESTING IF ALL THE BINARIES FOR THE BUILDING PROCESS ARE PRESENT #######
echo $RED
checkbinary $NANDDUMP
checkbinary $MKFS
checkbinary $UBINIZE
echo -n $WHITE

#############################################################################
# TEST IF RECEIVER IS SUPPORTED AND READ THE VARIABLES FROM THE LOOKUPTABLE #
if [ -f /proc/stb/info/boxtype ] ; then			# All models except Vu+
	SEARCH=$( cat /proc/stb/info/boxtype )
elif [ -f /proc/stb/info/vumodel ] ; then		# Vu+ models
	SEARCH=$( cat /proc/stb/info/vumodel )
else
	echo $RED
	$SHOW "message01" 2>&1 | tee -a $LOGFILE # No supported receiver found!
	big_fail
fi

cat $LOOKUP | cut -f 2 | grep -qw "$SEARCH"
if [ "$?" = "1" ] ; then
	echo $RED
	$SHOW "message01" 2>&1 | tee -a $LOGFILE # No supported receiver found!
#	big_fail
	UNKNOWN="yes"
	echo "This is an unsupported receiver but I will try to make a back-up. After the back-up has ended you'll have to rename the folder where the back-up is stored to match it with the required folder. You'll also have to check the filenames if they are named as in an original image, if not rename them. This procedure is experimental, use it at your own risk."
	MODEL="$SEARCH"
	SHOWNAME="Unknown model, it represents itself as a model: $SEARCH"
	FOLDER="/rename_this_folder"
	MAINDEST="$MEDIA$FOLDER"
	EXTR1="/fullbackup_Unknown_$MODEL/$DATE"
	EXTR2=""
	EXTRA="$MEDIA$EXTR1$EXTR2"
	ROOTNAME="rootfs.bin"
	KERNELNAME="kernel.bin"
	ACTION="noforce"
	LEBSIZE=$( cat /sys/devices/virtual/ubi/ubi0/eraseblock_size ) 
	MINIOSIZE=$( cat /sys/devices/virtual/ubi/ubi0/min_io_size ) 
	ERASEBLOCK=$( cat /sys/devices/virtual/ubi/ubi0/total_eraseblocks ) 
	PEBSIZE=$( cat /sys/devices/platform/brcmnand.0/mtd/mtd0/erasesize )
	MKUBIFS_ARGS="-m $MINIOSIZE -e $LEBSIZE -c $ERASEBLOCK"
	UBINIZE_ARGS="-m $MINIOSIZE -p $PEBSIZE"
else
	UNKNOWN="no"
	MODEL=`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 2`
	SHOWNAME=`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 3`
	FOLDER="`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 4`"
	EXTR1="`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 5`/$DATE"
	EXTR2="`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 6`"
	EXTRA="$MEDIA$EXTR1$EXTR2"
	if  [ $HARDDISK = 1 ]; then
		MAINDEST="$MEDIA$EXTR1$FOLDER"
	else 
		MAINDEST="$MEDIA$FOLDER"
	fi
	#MAINDEST="$MEDIA$FOLDER"
	MKUBIFS_ARGS=`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 7`
	UBINIZE_ARGS=`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 8`
	ROOTNAME=`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 9`
	KERNELNAME=`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 10`
	ACTION=`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 11`
fi
log "Destination        = $MAINDEST"
log $LINE

############# START TO SHOW SOME INFORMATION ABOUT BRAND & MODEL ##############
echo -n $PURPLE
echo -n "$SHOWNAME " | tr  a-z A-Z		# Shows the receiver brand and model
if [ $UNKNOWN != "yes" ] ; then
	 $SHOW "message02"  			# BACK-UP TOOL FOR MAKING A COMPLETE BACK-UP 
fi
echo $BLUE
log "RECEIVER = $SHOWNAME "
log "MKUBIFS_ARGS = $MKUBIFS_ARGS"
log "UBINIZE_ARGS = $UBINIZE_ARGS"
echo "$VERSION"
echo "Pedro_Newbie"
echo $WHITE

############ CALCULATE SIZE, ESTIMATED SPEED AND SHOW IT ON SCREEN ############
$SHOW "message06" 	#"Some information about the task:"
KERNELHEX=`cat /proc/mtd | grep -w "kernel" | cut -d " " -f 2` # Kernelsize in Hex
KERNEL=$((0x$KERNELHEX))			# Total Kernel size in bytes
TOTAL=$(($USEDsizebytes+$KERNEL))	# Total ROOTFS + Kernel size in bytes
KILOBYTES=$(($TOTAL/1024))			# Total ROOTFS + Kernel size in KB
MEGABYTES=$(($KILOBYTES/1024))
{
echo -n "KERNEL" ; $SHOW "message04" ; printf '%6s' $(($KERNEL/1024)); echo ' KB'
echo -n "ROOTFS" ; $SHOW "message04" ; printf '%6s' $USEDsizekb; echo ' KB'
echo -n "=TOTAL" ; $SHOW "message04" ; printf '%6s' $KILOBYTES; echo " KB (= $MEGABYTES MB)"
} 2>&1 | tee -a $LOGFILE
ESTTIMESEC=$(($KILOBYTES/$ESTSPEED))
ESTMINUTES=$(( $ESTTIMESEC/60 ))
ESTSECONDS=$(( $ESTTIMESEC-(( 60*$ESTMINUTES ))))
echo $LINE
{
$SHOW "message03"  ; printf "%d.%02d " $ESTMINUTES $ESTSECONDS ; $SHOW "message25" # estimated time in minutes 
echo $LINE
} 2>&1 | tee -a $LOGFILE

####### WARNING IF THE IMAGESIZE OF THE XTRENDS GETS TOO BIG TO RESTORE ########
if [ ${MODEL:0:2} = "et" -a ${MODEL:0:3} != "et8" -a ${MODEL:0:3} != "et1" -a ${MODEL:0:3} != "et7" ] ; then
	if [ $MEGABYTES -gt 120 ] ; then
    echo -n $RED
	$SHOW "message28" 2>&1 | tee -a $LOGFILE #Image probably too big to restore
	echo $WHITE
	elif [ $MEGABYTES -gt 110 ] ; then
	echo -n $YELLOW
	$SHOW "message29" 2>&1 | tee -a $LOGFILE #Image between 111 and 120MB could cause problems
	echo $WHITE
	fi
fi

#=================================================================================
#exit 0  #USE FOR DEBUGGING/TESTING ###########################################
#=================================================================================

##################### PREPARING THE BUILDING ENVIRONMENT ######################
log "*** FIRST SOME HOUSEKEEPING ***"
rm -rf "$WORKDIR"		# GETTING RID OF THE OLD REMAINS IF ANY
log "Remove directory   = $WORKDIR"
mkdir -p "$WORKDIR"		# MAKING THE WORKING FOLDER WHERE EVERYTHING HAPPENS
log "Recreate directory = $WORKDIR"
mkdir -p /tmp/bi/root # this is where the complete content will be available
log "Create directory   = /tmp/bi/root"
sync
mount --bind / /tmp/bi/root # the complete root at /tmp/bi/root

####################### START THE REAL BACK-UP PROCESS ########################
############################# MAKING UBINIZE.CFG ##############################
echo \[ubifs\] > "$WORKDIR/ubinize.cfg"
echo mode=ubi >> "$WORKDIR/ubinize.cfg"
echo image="$WORKDIR/root.ubi" >> "$WORKDIR/ubinize.cfg"
echo vol_id=0 >> "$WORKDIR/ubinize.cfg"
echo vol_type=dynamic >> "$WORKDIR/ubinize.cfg"
echo vol_name=rootfs >> "$WORKDIR/ubinize.cfg"
echo vol_flags=autoresize >> "$WORKDIR/ubinize.cfg"
log $LINE
log "UBINIZE.CFG CREATED WITH THE CONTENT:"
cat "$WORKDIR/ubinize.cfg"  >> $LOGFILE
touch "$WORKDIR/root.ubi"
chmod 644 "$WORKDIR/root.ubi"
log "--------------------------"

############################## MAKING KERNELDUMP ##############################
log $LINE
$SHOW "message07" 2>&1 | tee -a $LOGFILE			# Create: kerneldump
log "Kernel resides on $MTDPLACE" 					# Just for testing purposes 
$NANDDUMP --noecc /dev/$MTDPLACE -qf "$WORKDIR/$KERNELNAME"

# ADDED TO TRUNCATE THE KERNEL
# INSPIRED BY CODE OF ATHOIK, SEEN IN: http://tinyurl.com/ofmcvuo
/usr/bin/python -c "
data=open('$WORKDIR/$KERNELNAME', 'rb').read()
cutoff=data.find('\xff\xff\xff\xff')
if cutoff:
    open('$WORKDIR/$KERNELNAME', 'wb').write(data[0:cutoff])
"

if [ -f "$WORKDIR/$KERNELNAME" ] ; then
	echo -n "Kernel dumped  :"  >> $LOGFILE
	ls -e1 "$WORKDIR/$KERNELNAME" | sed 's/-r.*   1//' >> $LOGFILE
else 
	log "$WORKDIR/$KERNELNAME NOT FOUND"
	big_fail
fi
log "--------------------------"

#############################  MAKING ROOT.UBI(FS) ############################
$SHOW "message06a" 2>&1 | tee -a $LOGFILE		#Create: root.ubifs
log $LINE
$MKFS -r /tmp/bi/root -o "$WORKDIR/root.ubi" $MKUBIFS_ARGS
if [ -f "$WORKDIR/root.ubi" ] ; then
	echo -n "ROOT.UBI MADE  :" >> $LOGFILE
	ls -e1 "$WORKDIR/root.ubi" | sed 's/-r.*   1//' >> $LOGFILE
	UBISIZE=`cat "$WORKDIR/root.ubi" | wc -c`
	if [ "$UBISIZE" -eq 0 ] ; then 
		echo "Probably you are trying to make the back-up in flash memory" 2>&1 | tee -a $LOGFILE
		big_fail
	fi
else 
	log "$WORKDIR/root.ubi NOT FOUND"
	big_fail
fi
log $LINE
echo "Start UBINIZING" >> $LOGFILE
$UBINIZE -o "$WORKDIR/root.ubifs" $UBINIZE_ARGS "$WORKDIR/ubinize.cfg" >/dev/null
chmod 644 "$WORKDIR/root.ubifs"
if [ -f "$WORKDIR/root.ubifs" ] ; then
	echo -n "ROOT.UBIFS MADE:" >> $LOGFILE
	ls -e1 "$WORKDIR/root.ubifs" | sed 's/-r.*   1//' >> $LOGFILE
else 
	echo "$WORKDIR/root.ubifs NOT FOUND"  >> $LOGFILE
	big_fail
fi
echo

############################ ASSEMBLING THE IMAGE #############################
make_folders
if  [ $HARDDISK != 1 ]; then
	mkdir -p "$EXTRA"
	echo "Created directory  = $EXTRA" >> $LOGFILE
fi
mv "$WORKDIR/root.ubifs" "$MAINDEST/$ROOTNAME" 
mv "$WORKDIR/$KERNELNAME" "$MAINDEST/$KERNELNAME"
if [ $ACTION = "noforce" ] ; then
	echo "rename this file to 'force' to force an update without confirmation" > "$MAINDEST/noforce"; 
elif [ $ACTION = "reboot" ] ; then
	echo "rename this file to 'force.update' to force an update without confirmation" > "$MAINDEST/reboot.update"
elif [ $ACTION = "force" ] ; then
	echo "rename this file to 'force.update' to be able to flash this backup" > "$MAINDEST/noforce.update"
fi

image_version > "$MAINDEST/imageversion" 
if  [ $HARDDISK != 1 ]; then
	cp -r "$MAINDEST" "$EXTRA" 	#copy the made back-up to images
fi
if [ -f "$MAINDEST/$ROOTNAME" -a -f "$MAINDEST/$KERNELNAME" -a -f "$MAINDEST/imageversion" ] ; then
		backup_made
		$SHOW "message14" 			# Instructions on how to restore the image.
		echo $LINE
else
	big_fail
fi

#################### CHECKING FOR AN EXTRA BACKUP STORAGE #####################
if  [ $HARDDISK = 1 ]; then						# looking for a valid usb-stick
	for candidate in /media/sd* /media/mmc* /media/usb* /media/*
	do
		if [ -f "${candidate}/"*[Bb][Aa][Cc][Kk][Uu][Pp][Ss][Tt][Ii][Cc][Kk]* ]
		then
		TARGET="${candidate}"
		fi    
	done
	if [ "$TARGET" != "XX" ] ; then
		echo -n $GREEN
		$SHOW "message17" 2>&1 | tee -a $LOGFILE 	# Valid USB-flashdrive detected, making an extra copy
		echo $LINE
		TOTALSIZE="$(df -h "$TARGET" | tail -n 1 | awk {'print $2'})"
		FREESIZE="$(df -h "$TARGET" | tail -n 1 | awk {'print $4'})"
		{
		$SHOW "message09" ; echo -n "$TARGET ($TOTALSIZE, " ; $SHOW "message16" ; echo "$FREESIZE)"
		} 2>&1 | tee -a $LOGFILE
		rm -rf "$TARGET$FOLDER"
		mkdir -p "$TARGET$FOLDER"
		cp -r "$MAINDEST/." "$TARGET$FOLDER"
		echo $LINE >> $LOGFILE
		echo "MADE AN EXTRA COPY IN: $TARGET" >> $LOGFILE
		df -h "$TARGET"  >> $LOGFILE
		$SHOW "message19" 2>&1 | tee -a $LOGFILE	# Backup finished and copied to your USB-flashdrive
	else 
		echo "NO additional USB-stick found to copy an extra backup" >> $LOGFILE
	fi
sync
fi
######################### END OF EXTRA BACKUP STORAGE #########################

################## CLEANING UP AND REPORTING SOME STATISTICS ##################
clean_up
END=$(date +%s)
DIFF=$(( $END - $START ))
MINUTES=$(( $DIFF/60 ))
SECONDS=$(( $DIFF-(( 60*$MINUTES ))))
echo -n $YELLOW
{
$SHOW "message24"  ; printf "%d.%02d " $MINUTES $SECONDS ; $SHOW "message25"
} 2>&1 | tee -a $LOGFILE

ROOTSIZE=`ls "$MAINDEST" -e1S | grep root | awk {'print $3'} ` 
KERNELSIZE=`ls "$MAINDEST" -e1S | grep kernel | awk {'print $3'} ` 
TOTALSIZE=$((($ROOTSIZE+$KERNELSIZE)/1024))
SPEED=$(( $TOTALSIZE/$DIFF ))

echo $SPEED > /usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/speed.txt
echo $LINE >> $LOGFILE
# "Back up done with $SPEED KB per second" 
{
$SHOW "message26" ; echo -n "$SPEED" ; $SHOW "message27"
} 2>&1 | tee -a $LOGFILE
#### ADD A LIST OF THE INSTALLED PACKAGES TO THE BackupSuite.LOG ####
echo $LINE >> $LOGFILE
echo $LINE >> $LOGFILE
echo "Installed packages contained in this backup:" >> $LOGFILE
echo "--------------------------------------------" >> $LOGFILE
opkg list-installed >> $LOGFILE

######################## COPY LOGFILE TO MAINDESTINATION ######################
echo -n $WHITE
cp $LOGFILE "$MAINDEST"
if  [ $HARDDISK != 1 ]; then
	cp $LOGFILE "$MEDIA$EXTR1$FOLDER"
fi
if [ "$TARGET" != "XX" ] ; then
	cp $LOGFILE "$TARGET$FOLDER"
fi
exit 
############### END OF PROGRAMM ################
