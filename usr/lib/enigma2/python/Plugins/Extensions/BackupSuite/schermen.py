

skinstarthd = """
	<screen name="BackupSuite" position="fill" size="1280,720" title=" " >
		<eLabel position="0,0" size="1280,88" backgroundColor="#00000000" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/smallshadowline.png" position="0,88" size="1280,2" zPosition="2"/>
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/smallshadowline.png" position="0,630" size="1280,2" zPosition="2"/>
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/red.png"	position="145,641" size="30,30" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/green.png"	position="420,641" size="30,30" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/yellow.png" position="695,641" size="30,30" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/blue.png"	position="970,641" size="30,30" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/key_info.png" alphatest="on" position="110,645" size="35,25" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/key_help.png" alphatest="on" position="70,645" size="35,25" />
		<widget source="Title" render="Label" position="25,30" size="1085,55" backgroundColor="#00000000" transparent="1" zPosition="1" font="Regular;24" valign="center"/>
		<widget source="global.CurrentTime" render="Label" position="1100,24" size="150,55" backgroundColor="#18101214" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right">
			<convert type="ClockToText">Format:%H:%M</convert>
		</widget>
		<widget source="global.CurrentTime" render="Label" position="950,44" size="300,55" backgroundColor="#18101214" transparent="1" zPosition="1" font="Regular;16" valign="center" halign="right">
			<convert type="ClockToText">Date</convert>
		</widget>
		<eLabel text=" " position="85,30" size="1085,55" backgroundColor="#18101214" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="left" />
		<widget source="session.VideoPicture" render="Pig" position="25,98" size="440,248" backgroundColor="#ff000000" zPosition="2" />
		<widget source="session.CurrentService" render="Label" position="25,98" size="440,20" zPosition="3" borderWidth="1" borderColor="#00000000" foregroundColor="#00f0f0f0" backgroundColor="#ff000000" transparent="1" font="Regular;18" noWrap="1" valign="center" halign="center">
			<convert type="ServiceName">Name</convert>
		</widget>
		<widget name="key_red" 		position="180,643" size="220,28"  valign="top" halign="left" zPosition="4"  foregroundColor="#00ff0000" font="Regular;22" /> 
		<widget name="key_green"	position="455,643" size="220,28"  valign="top" halign="left" zPosition="4"  foregroundColor="#0053b611" font="Regular;22" /> 
		<widget name="key_yellow" 	position="730,643" size="220,28"  valign="top" halign="left" zPosition="4"  foregroundColor="#00F9C731" font="Regular;22" />
		<widget name="key_blue" 	position="1005,643" size="220,28" valign="top" halign="left" zPosition="4"  foregroundColor="#003a71c3" font="Regular;22" />
		<widget source="help" render="Label" position="5,345" size="590,83" font="Regular;21" />
	</screen>"""

skinstartsd = """
	<screen name="BackupSuite" position="fill" size="720,576" title=" " >
		<eLabel position="0,0" size="720,88" backgroundColor="#00000000" />
		<widget source="Title" render="Label" transparent="1" zPosition="1" halign="center" valign="center" position="60,30" size="600,45" font="Regular;20" foregroundColor="#006CA4C5"/>
		<ePixmap pixmap="skin_default/buttons/key_info.png" zPosition="1" position="10,540" size="35,25" alphatest="blend"/>
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/key_help.png" zPosition="1" position="50,540" size="35,25" alphatest="blend"/>
		<ePixmap pixmap="skin_default/buttons/button_red.png" zPosition="1" position="10,516" size="15,16" alphatest="blend"/>
		<ePixmap pixmap="skin_default/buttons/button_green.png" zPosition="1" position="190,516" size="15,16" alphatest="blend"/>
		<ePixmap pixmap="skin_default/buttons/button_yellow.png" zPosition="1" position="370,516" size="15,16" alphatest="blend"/>
		<ePixmap pixmap="skin_default/buttons/button_blue.png" zPosition="1" position="550,516" size="15,16" alphatest="blend"/>
		<widget source="key_red" render="Label" position="30,514" zPosition="1" size="150,45" font="Regular;20" foregroundColor="#00ff0000" halign="left" valign="top" />
		<widget source="key_green" render="Label" position="210,514" zPosition="1" size="150,45" font="Regular;20" foregroundColor="#0053b611" halign="left" valign="top" />
		<widget source="key_yellow" render="Label" position="390,514" zPosition="1" size="150,45" font="Regular;20" foregroundColor="#00F9C731" halign="left" valign="top" />
		<widget source="key_blue" render="Label" position="570,514" zPosition="1" size="150,45" font="Regular;20" foregroundColor="#003a71c3" halign="left" valign="top" />
	</screen>"""


skinnewhd = """
	<screen name="WhatisNewInfo" position="center,center" size="1280,720" title=" " >
		<eLabel position="0,0" size="1280,88" backgroundColor="#00000000" />
		<eLabel text=" " position="25,30" size="1085,55" backgroundColor="#18101214" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="left" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/smallshadowline.png" position="0,88" size="1280,2" zPosition="2"/>
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/smallshadowline.png" position="0,630" size="1280,2" />	
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/red.png" 	position="145,641" size="30,30" alphatest="on" />
		<widget source="Title" render="Label" position="25,30" size="1085,55" backgroundColor="#00000000" transparent="1" zPosition="1" font="Regular;24" valign="center" />
		<widget source="global.CurrentTime" render="Label" position="1100,24" size="150,55" backgroundColor="#18101214" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right">
			<convert type="ClockToText">Format:%H:%M</convert>
		</widget>
		<widget source="global.CurrentTime" render="Label" position="950,44" size="300,55" backgroundColor="#18101214" transparent="1" zPosition="1" font="Regular;16" valign="center" halign="right">
			<convert type="ClockToText">Date</convert>
		</widget>
		<widget name="AboutScrollLabel" font="Regular;22" position="25,125" size="1230,500" zPosition="2" halign="left" />
		<widget name="key_red" 		position="180,643" size="220,28"  valign="top" halign="left" zPosition="4"  foregroundColor="#00ff0000" font="Regular;22" /> 
	</screen>"""


skinnewsd = """
	<screen name="BackupSuite" position="fill" size="720,576" title=" " >
		<eLabel position="0,0" size="720,88" backgroundColor="#00000000" />
		<widget source="Title" render="Label" transparent="1" zPosition="1" halign="center" valign="center" position="60,30" size="600,45" font="Regular;20" foregroundColor="#006CA4C5"/>
		<ePixmap pixmap="skin_default/buttons/button_red.png" zPosition="1" position="10,516" size="15,16" alphatest="blend"/>
		<widget source="key_red" render="Label" position="30,514" zPosition="1" size="150,45" font="Regular;20" foregroundColor="#00ff0000" halign="left" valign="top" />
		<widget name="AboutScrollLabel" font="Regular;20" position="10,88" size="700,400" zPosition="2" halign="left" />
	</screen>"""

skinflashhd = """
	<screen name="FlashImageConfig" position="center,center" size="1280,720" title=" " >
		<eLabel position="0,0" size="1280,88" backgroundColor="#00000000" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/smallshadowline.png" position="0,88" size="1280,2" zPosition="2"/>
		<widget source="Title" render="Label" position="25,30" size="1085,55" backgroundColor="#00000000" transparent="1" zPosition="1" font="Regular;24" valign="center" />
		<widget source="global.CurrentTime" render="Label" position="1100,24" size="150,55" backgroundColor="#18101214" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="right">
			<convert type="ClockToText">Format:%H:%M</convert>
		</widget>
		<widget source="global.CurrentTime" render="Label" position="950,44" size="300,55" backgroundColor="#18101214" transparent="1" zPosition="1" font="Regular;16" valign="center" halign="right">
			<convert type="ClockToText">Date</convert>
		</widget>
		<eLabel text=" " position="85,30" size="1085,55" backgroundColor="#18101214" transparent="1" zPosition="1" font="Regular;24" valign="center" halign="left" />
		<widget source="session.VideoPicture" render="Pig" position="25,98" size="440,248" backgroundColor="#ff000000" zPosition="2" />
		<widget source="session.CurrentService" render="Label" position="25,98" size="440,20" zPosition="3" borderWidth="1" borderColor="#00000000" foregroundColor="#00f0f0f0" backgroundColor="#ff000000" transparent="1" font="Regular;18" noWrap="1" valign="center" halign="center">
			<convert type="ServiceName">Name</convert>
		</widget>
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/smallshadowline.png" position="0,630" size="1280,2" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/red.png" position="145,641" size="30,30" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/green.png" position="420,641" size="30,30" alphatest="on" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img/yellow.png" position="695,641" size="30,30" alphatest="on" />
		<widget source="key_red" 	render="Label" position="180,643" size="220,28" valign="top" halign="left" zPosition="4" foregroundColor="#00ff0000" font="Regular;22"    />
		<widget source="key_green" 	render="Label" position="455,643" size="220,28" valign="top" halign="left" zPosition="4" foregroundColor="#0053b611" font="Regular;22" /> 
		<widget source="key_yellow"	render="Label" position="730,643" size="220,28" valign="top" halign="left" zPosition="4" foregroundColor="#00F9C731" font="Regular;22"  />
		<widget source="curdir" 	render="Label" position="525,100" size="1000,40" valign="top" halign="left" zPosition="4" foregroundColor="#00f0f0f0" font="Regular;22"  backgroundColor="#00000000" transparent="1" noWrap="1" />
		<widget name="filelist" position="525,150" size="500,460" scrollbarMode="showOnDemand" />
	</screen>"""

skinflashsd = """
	<screen name="FlashImageConfig" position="fill" size="720,576" title=" " >
		<eLabel position="0,0" size="720,88" backgroundColor="#00000000" />
		<widget source="Title" render="Label" transparent="1" zPosition="1" halign="center" valign="center" position="60,30" size="600,45" font="Regular;20" foregroundColor="#006CA4C5"/>
		<ePixmap pixmap="skin_default/buttons/button_red.png" zPosition="1" position="10,516" size="15,16" alphatest="blend"/>
		<ePixmap pixmap="skin_default/buttons/button_green.png" zPosition="1" position="190,516" size="15,16" alphatest="blend"/>
		<ePixmap pixmap="skin_default/buttons/button_yellow.png" zPosition="1" position="370,516" size="15,16" alphatest="blend"/>
		<widget source="key_red" render="Label" position="30,514" zPosition="1" size="150,45" font="Regular;20" foregroundColor="#00ff0000" halign="left" valign="top" />
		<widget source="key_green" render="Label" position="210,514" zPosition="1" size="150,45" font="Regular;20" foregroundColor="#0053b611" halign="left" valign="top" />
		<widget source="key_yellow" render="Label" position="390,514" zPosition="1" size="150,45" font="Regular;20" foregroundColor="#00F9C731" halign="left" valign="top" />
		<widget source="curdir" 	render="Label" position="10,88" size="700,40" valign="top" halign="left" zPosition="4" foregroundColor="#00f0f0f0" font="Regular;18"  backgroundColor="#00000000" transparent="1" noWrap="1" />
		<widget name="filelist" position="20,120" size="690,390" scrollbarMode="showOnDemand" />
	</screen>"""
