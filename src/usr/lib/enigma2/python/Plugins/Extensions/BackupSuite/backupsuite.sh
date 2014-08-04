#       FULL BACKUP UYILITY FOR ENIGMA2/OPENPLI, SUPPORTS VARIOUS MODELS      #
#                   MAKES A FULLBACK-UP READY FOR FLASHING.                   #
#                   Pedro_Newbie (backupsuite@outlook.com)                    #
###############################################################################
#
#!/bin/sh

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
clean_up
echo -n $RED
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
echo $LINE
}

#################### CLEAN UP AND MAKE DESTINATION FOLDERS ####################
make_folders()
{
rm -rf "$MAINDEST"
echo "Removed directory  = $MAINDEST"  >> $LOGFILE
mkdir -p "$MAINDEST"
echo "Created directory  = $MAINDEST"  >> $LOGFILE
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
$SHOW "message11" ; echo "$EXTRA"		# and there is made an extra copy in:
echo $LINE
} 2>&1 | tee -a $LOGFILE
}
############################## END PROGRAM BLOCKS #############################


########################## DECLARATION OF VARIABLES ###########################
BACKUPDATE=`date +%Y.%m.%d_%H:%M`
DATE=`date +%Y%m%d_%H%M`
ESTSPEED=`cat /usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/speed.txt`
FLASHED=`date -r /etc/version +%Y.%m.%d_%H:%M`
ISSUE=`cat /etc/issue | grep . | tail -n 1 ` 
IMVER=${ISSUE%?????}
LASTUPDATE=`date -r /var/lib/opkg/status +%Y.%m.%d_%H:%M`
LOGFILE=/tmp/BackupSuite.log
MEDIA="$1"
MKFS=/usr/sbin/mkfs.ubifs
MTDPLACE=`cat /proc/mtd | grep "kernel" | cut -d ":" -f 1`
NANDDUMP=/usr/sbin/nanddump
START=$(date +%s)
LOOKUP="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/lookuptable.txt"
TARGET="XX"
UBINIZE=/usr/sbin/ubinize
USEDsizebytes=`df -B 1 /usr/ | grep [0-9]% | tr -s " " | cut -d " " -f 3`
USEDsizekb=`df -k /usr/ | grep [0-9]% | tr -s " " | cut -d " " -f 3` 
VERSION="Version 17.7 - 30-07-2014"
WORKDIR="$MEDIA/bi"

######################### START THE LOGFILE $LOGFILE ##########################
echo "*** THIS BACKUP IS CREATED WITH THE PLUGIN BACKUPSUITE ***" > $LOGFILE
echo "***** This plugin is brought to you by Pedro_Newbie ******" >> $LOGFILE
echo $LINE >> $LOGFILE
echo "Plugin version     = $VERSION" >> $LOGFILE
echo "Back-up media      = $MEDIA" >> $LOGFILE
df -h "$MEDIA"  >> $LOGFILE
echo $LINE >> $LOGFILE
image_version >> $LOGFILE
echo "Working directory  = $WORKDIR" >> $LOGFILE

######################### TESTING FOR UBIFS OR JFFS2 ##########################
grep rootfs /proc/mounts | grep -q ubifs 
if [ "$?" = 1 ] ; then
	echo $RED
	$SHOW "message01" 2>&1 | tee -a $LOGFILE #NO UBIFS, THEN JFFS2 BUT NOT SUPPORTED ANYMORE
	big_fail
fi

####### TESTING IF ALL THE TOOLS FOR THE BUILDING PROCESS ARE PRESENT #########
echo $RED
if [ ! -f $NANDDUMP ] ; then
	{
	echo -n "$NANDDUMP " ; $SHOW "message05"  	# nanddump not found.
	} 2>&1 | tee -a $LOGFILE
	big_fail
fi


if [ ! -f $MKFS ] ; then
	{
	echo -n "$MKFS " ; $SHOW "message05"  		# mkfs.ubifs not found.
	} 2>&1 | tee -a $LOGFILE
	big_fail
fi


if [ ! -f $UBINIZE ] ; then
	{
	echo -n "$UBINIZE " ; $SHOW "message05"  	# ubinize not found.
	} 2>&1 | tee -a $LOGFILE
	big_fail
fi
echo -n $WHITE

#==============================================================================
# TEST IF RECEIVER IS SUPPORTED AND READ THE VARIABLES FROM THE LOOKUPTABLE   #
#==============================================================================
if [ -f /proc/stb/info/boxtype ] ; then			# Xtrends and XP1000
	SEARCH=$( cat /proc/stb/info/boxtype )
elif [ -f /proc/stb/info/vumodel ] ; then		# Vu models
	SEARCH=$( cat /proc/stb/info/vumodel )
else
	echo $RED
	$SHOW "message01" 2>&1 | tee -a $LOGFILE # No supported receiver found!
	big_fail
fi

cat $LOOKUP | grep -qw "$SEARCH"
if [ "$?" = "1" ] ; then
	echo $RED
	$SHOW "message01" 2>&1 | tee -a $LOGFILE # No supported receiver found!
	big_fail
fi

MODEL=`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 2`
SHOWNAME=`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 3`
FOLDER="`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 4`"
MAINDEST="$MEDIA$FOLDER"
EXTR1="`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 5`/$DATE"
EXTR2="`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 6`"
EXTRA="$MEDIA$EXTR1$EXTR2"
MKUBIFS_ARGS=`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 7`
UBINIZE_ARGS=`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 8`
ROOTNAME=`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 9`
KERNELNAME=`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 10`
ACTION=`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 11`
MESSAGE=`cat $LOOKUP | grep -w -m1 "$SEARCH" | cut -f 12`
echo "Destination        = $MAINDEST" >> $LOGFILE
echo $LINE >> $LOGFILE

############# START TO SHOW SOME INFORMATION ABOUT BRAND & MODEL ##############
echo -n $PURPLE
echo -n "$SHOWNAME " | tr  a-z A-Z		# Shows the receiver brand and model
$SHOW "message02"  			# BACK-UP TOOL FOR MAKING A COMPLETE BACK-UP 
echo $BLUE
echo "RECEIVER = $SHOWNAME " | tr  a-z A-Z >> $LOGFILE
echo "MKUBIFS_ARGS = $MKUBIFS_ARGS" >> $LOGFILE
echo "UBINIZE_ARGS = $UBINIZE_ARGS" >> $LOGFILE
echo "$VERSION"
echo "Pedro_Newbie (e-mail: backupsuite@outlook.com)"
echo $WHITE

############ CALCULATE SIZE, ESTIMATED SPEED AND SHOW IT ON SCREEN ############
$SHOW "message06" 	#"Some information about the task:"
KERNELHEX=`cat /proc/mtd | grep kernel | cut -d " " -f 2` # Kernelsize in Hex
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
if [ ${MODEL:0:2} = et ] ; then
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
echo "*** FIRST SOME HOUSEKEEPING ***" >> $LOGFILE
rm -rf "$WORKDIR"		# GETTING RID OF THE OLD REMAINS IF ANY
echo "Remove directory   = $WORKDIR" >> $LOGFILE
mkdir -p "$WORKDIR"		# MAKING THE WORKING FOLDER WHERE EVERYTHING HAPPENS
echo "Recreate directory = $WORKDIR" >> $LOGFILE
mkdir -p /tmp/bi/root # this is where the complete content will be available
echo "Create directory   = /tmp/bi/root" >> $LOGFILE
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
echo $LINE >> $LOGFILE
echo "UBINIZE.CFG CREATED WITH THE CONTENT:"  >> $LOGFILE
cat "$WORKDIR/ubinize.cfg"  >> $LOGFILE
touch "$WORKDIR/root.ubi"
chmod 644 "$WORKDIR/root.ubi"
echo "--------------------------" >> $LOGFILE

#############################  MAKING ROOT.UBI(FS) ############################
$SHOW "message06a" 2>&1 | tee -a $LOGFILE		#Create: root.ubifs
echo $LINE >> $LOGFILE
$MKFS -r /tmp/bi/root -o "$WORKDIR/root.ubi" $MKUBIFS_ARGS
if [ -f "$WORKDIR/root.ubi" ] ; then
	echo -n "ROOT.UBI MADE  :" >> $LOGFILE
	ls -e1 "$WORKDIR/root.ubi" | sed 's/-r.*   1//' >>$LOGFILE
	UBISIZE=`cat "$WORKDIR/root.ubi" | wc -c`
	if [ "$UBISIZE" -eq 0 ] ; then 
		echo "Probably you are trying to make the back-up in flash memory" 2>&1 | tee -a $LOGFILE
		big_fail
	fi
else 
	echo "$WORKDIR/root.ubi NOT FOUND"  >> $LOGFILE
	big_fail
fi
echo $LINE >> $LOGFILE
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

############################## MAKING KERNELDUMP ##############################
echo $LINE >> $LOGFILE
$SHOW "message07" 2>&1 | tee -a $LOGFILE			# Create: kerneldump
echo "Kernel resides on $MTDPLACE" >> $LOGFILE # Just for testing purposes 
$NANDDUMP /dev/$MTDPLACE -q > "$WORKDIR/$KERNELNAME"

KERNELCHECK=`ls "$WORKDIR" -e1S | grep kernel | awk {'print $3'} ` 
if [ $KERNELCHECK != $KERNEL ] ; then
	echo "The size of the Kernel = $KERNELCHECK bytes, expected it to be $KERNEL bytes" >> $LOGFILE
	echo "Now checking if there are reported badblocks, if there are badblocks reported then there is probably no problem" >> $LOGFILE
	mtdinfo -M /dev/$MTDPLACE | grep -q BAD
	if [ "$?" = "1" ] ; then
		echo "There were no known badblocks in the kernel partition ($MTDPLACE), this could point at troubles" >> $LOGFILE
	else 
		echo "The badblocks were already marked as such in the kernelpartion /dev/$MTDPLACE, so there are probably no problems" >> $LOGFILE
	fi
fi

if [ -f "$WORKDIR/$KERNELNAME" ] ; then
	echo -n "Kernel dumped  :" >> $LOGFILE
	ls -e1 "$WORKDIR/$KERNELNAME" | sed 's/-r.*   1//' >> $LOGFILE
else 
	echo "$WORKDIR/$KERNELNAME NOT FOUND"  >> $LOGFILE
	big_fail
fi
echo "--------------------------" >> $LOGFILE

############################ ASSEMBLING THE IMAGE #############################
make_folders
mkdir -p "$EXTRA"
echo "Created directory  = $EXTRA" >> $LOGFILE
mv "$WORKDIR/root.ubifs" "$MAINDEST/$ROOTNAME" 
mv "$WORKDIR/$KERNELNAME" "$MAINDEST/$KERNELNAME"
if [ $ACTION = "noforce" ] ; then
	echo "rename this file to 'force' to force an update without confirmation" > "$MAINDEST/noforce"; 
elif [ $ACTION = "reboot" ] ; then	
	touch "$MAINDEST/reboot.update"
	echo "rename this file to 'force.update' to force an update without confirmation" > "$MAINDEST/noforce.update"
	echo "and remove reboot.update, otherwise the box is flashed again after completion" >> "$MAINDEST/noforce.update"
	chmod 644 "$MAINDEST/reboot.update"
fi

image_version > "$MAINDEST/imageversion" 
cp -r "$MAINDEST" "$EXTRA" 	#copy the made back-up to images
if [ -f "$MAINDEST/$ROOTNAME" -a -f "$MAINDEST/$KERNELNAME" -a -f "$MAINDEST/imageversion" ] ; then
		backup_made
		$SHOW $MESSAGE 			# Instructions on how to restore the image.
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
		echo $GREEN
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

######################## COPY LOGFILE TO MAINDESTINATION ######################
echo -n $WHITE
cp $LOGFILE "$MAINDEST"
if [ $EXTRA2="/vuplus" ] ; then
	cp $LOGFILE "$MEDIA$EXTR1$FOLDER"
else 
	cp $LOGFILE "$EXTRA$FOLDER"
fi
if [ "$TARGET" != "XX" ] ; then
	cp $LOGFILE "$TARGET$FOLDER"
fi
exit 
############### END OF PROGRAMM ################
