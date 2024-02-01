#############################################
# PubCMD.tcl 2.0.0               # 01/11/20 #
#############################################
#Author  ComputerTech                       #
#Irc     irc.rizon.net #ComputerTech        #
#Email   ComputerTech312@Gmail.com          #
#GitHub  https://github.com/computertech312 #
#################################################################################################################################################################
#Start Of Settings

#Set trigger of the commands

set pubcmd ";"

#if you want to change which flags can use which command change the following e.g  o|o

#set flag for normal commands

set flag "o|o"

#set flag for important commands e.g rehash,restart,die

set topflag "n|n"

#Type of IRCd Your Network Uses
#1 = Unrealircd 1
#2 = Inspircd
#3 = Freenode 
#4 = Undernet

set ircd "1"
#################################################################################################################################################################
#End Of Settings

bind pub ${flag} ${pubcmd}op pub:op
bind pub ${flag} ${pubcmd}deop pub:deop
bind pub ${flag} ${pubcmd}halfop pub:halfop
bind pub ${flag} ${pubcmd}dehalfop pub:dehalfop
bind pub ${flag} ${pubcmd}voice pub:voice
bind pub ${flag} ${pubcmd}devoice pub:devoice
bind pub ${flag} ${pubcmd}ban pub:ban
bind pub ${flag} ${pubcmd}unban pub:unban
bind pub ${flag} ${pubcmd}mute pub:mute
bind pub ${flag} ${pubcmd}unmute pub:unmute
bind pub ${flag} ${pubcmd}rehash pub:rehash
bind pub ${flag} ${pubcmd}restart pub:restart
bind pub ${flag} ${pubcmd}die pub:die
bind pub ${flag} ${pubcmd}kick pub:kick
bind pub ${flag} ${pubcmd}kickban pub:kickban
bind pub ${flag} ${pubcmd}link pub:link
bind pub ${flag} ${pubcmd}unlink pub:unlink
bind pub ${flag} ${pubcmd}topic pub:topic
bind pub ${flag} ${pubcmd}join pub:join
bind pub ${flag} ${pubcmd}part pub:part
bind pub ${flag} ${pubcmd}chanset pub:chanset
bind pub ${flag} ${pubcmd}cycle pub:cycle
bind pub ${flag} ${pubcmd}invite pub:invite
bind pub ${flag} ${pubcmd}addban pub:addban
bind pub ${flag} ${pubcmd}delban pub:delban
bind pub ${flag} ${pubcmd}bans pub:bans
bind pub ${flag} ${pubcmd}ignores pub:ignores
bind pub ${flag} ${pubcmd}addignore pub:addignore
bind pub ${flag} ${pubcmd}delignore pub:delignore
bind pub ${flag} ${pubcmd}ping pPingPubCommand

proc do_pub_help { nick uhost hand chan text } {
   global pubcmd
   putserv "Notice $nick :The Following Are The Commands Of PubCmd :"
   putserv "Notice $nick :${pubcmd}ban | ${pubcmd}unban | ${pubcmd}mute | ${pubcmd}unmute | ${pubcmd}voice | ${pubcmd}devoice | ${pubcmd}rehash | ${pubcmd}restart | ${pubcmd}op | ${pubcmd}deop"
   putserv "Notice $nick :${pubcmd}kick | ${pubcmd}kickban | ${pubcmd}link | ${pubcmd}unlink | ${pubcmd}topic | ${pubcmd}join | ${pubcmd}part | ${pubcmd}mode | ${pubcmd}puthelp"
   putserv "Notice $nick :/msg $::botnick ${pubcmd}say message (this is the only command that doesnt change)"
   if {[matchattr $nick $::topflag]} {
      putserv "Notice $nick :Admin Commands Of PubCmd : ${pubcmd}ignore , ${pubcmd}ignores , ${pubcmd}die"
   }
}

proc pub:addignore {nick host hand chan text} {
	set bad [lindex [split $text] 0]
	set breason [lindex [split $text] 1]
	set btime [lindex [split $text] 2]
    set bhost "[maskhost $bad![getchanhost $bad $chan] 2]"
    newignore "$bhost" "$nick" "$breason" $btime  
}

proc pub:delignore {nick uhost hand chan arg} {
	set unbanmask [lindex [split $arg] 0]
	if {![isban $unbanmask ]} {putquick "PRIVMSG $chan :\037ERROR\037: Banmask not found."; return}
	killignore $unbanmask
	putquick "NOTICE $nick :Successfully Deleted Ignore: $unbanmask"
	return 0
}

proc pub:ignores {nick uhost hand chan arg} {
	putserv "NOTICE $nick :********* \002Ignore List\002 **********"

	foreach botignore [ignorelist] {
		putserv "NOTICE $nick :\002BotIgnores\002: $botignore"
	}
	putserv "NOTICE $nick :********** \002Ignore List \037END\037\002 **********"
}

proc pub:addban {nick host hand chan text} {
	set bad [lindex [split $text] 0]
	set breason [lindex [split $text] 1]
	set btime [lindex [split $text] 2]
	set bhost "[maskhost $bad![getchanhost $bad $chan] 2]"
	if {$breason == ""} { set reason "requested" }
	newchanban "$chan" "$bhost" "$nick" "$breason" $btime
}

proc pub:delban {nick uhost hand chan arg} {
	set unbanmask [lindex [split $arg] 0]
	if {![isignore $unbanmask]} {putquick "PRIVMSG $chan :\037ERROR\037: Banmask not found."; return}
	killchanban $chan $unbanmask
	putquick "NOTICE $nick :Successfully Deleted Ban: $unbanmask for $chan"
	return 0
}

proc pub:bans {nick uhost hand chan arg} {
	putquick "PRIVMSG $chan :\002BANLIST\002 for $chan sent to $nick"
	putserv "NOTICE $nick :********* \002$chan BanList\002 **********"

	foreach botban [banlist $chan] {
		putserv "NOTICE $nick :\002BOTBAN\002: $botban"
	}
	putserv "NOTICE $nick :********** \002$chan BanList \037END\037\002 **********"
}

proc pub:op {nick uhost hand chan text} {
	set var0 "[lindex [split $text] 0 ]"
	if {![botisop $chan]} {
		return 0
	}
	if {[lindex [split $text] 0 ] !=""} {
         foreach cible [split $text] {
            pushmode $chan +o $cible
         }
         flushmode $chan
      } else {
         putnow "mode $chan +o $nick"
}
}

proc pub:deop {nick uhost hand chan text} {
	set var0 "[lindex [split $text] 0 ]"
	if {![botisop $chan]} {
		return 0
	}
	if {[lindex [split $text] 0 ] !=""} {
         foreach cible [split $text] {
            pushmode $chan -o $cible
         }
         flushmode $chan
      } else {
         putquick "mode $chan -o $nick"
}
}

proc pub:halfop {nick uhost hand chan text} {
	global ircd
    if {!($ircd == "1")} {return 0}
    set var0 "[lindex [split $text] 0 ]"
	if {![botisop $chan]} {return 0}
	if {[lindex [split $text] 0 ] !=""} {
         foreach cible [split $text] {
            pushmode $chan +h $cible 
      }
         flushmode $chan
      } else {
         putquick "mode $chan +h $nick"
}
}

proc pub:dehalfop {nick uhost hand chan text} {
global ircd
    if {!($ircd == "1")} {return 0}
    set var0 "[lindex [split $text] 0 ]"
	if {![botisop $chan]} {return 0}
	if {[lindex [split $text] 0 ] !=""} {
         foreach cible [split $text] {
            pushmode $chan -h $cible 
      }
         flushmode $chan
      } else {
         putquick "mode $chan -h $nick"
}
}

proc pub:voice {nick uhost hand chan text} {
	set var0 "[lindex [split $text] 0 ]"
	if {![botisop $chan]} {
		return 0
	}
	if {[lindex [split $text] 0 ] !=""} {
         foreach cible [split $text] {
            pushmode $chan +v $cible
         }
         flushmode $chan
      } else {
         putquick "mode $chan +v $nick"
}
}

proc pub:devoice {nick uhost hand chan text} {
	set var0 "[lindex [split $text] 0 ]"
	if {![botisop $chan]} {
		return 0
	}
	if {[lindex [split $text] 0 ] !=""} {
         foreach cible [split $text] {
            pushmode $chan -v $cible
         }
         flushmode $chan
      } else {
         putquick "mode $chan -v $nick"
}
}

proc pub:ban {nick uhost hand chan text} {
	set var0 "[lindex [split $text] 0 ]"
	if {![botisop $chan]} {
		return 0
	}
	if {[isbotnick $var0]} {
		return 0
	}
	if {[matchattr [nick2hand $var0] n]} {
		return 0
	}
	if {[onchan $var0 $chan]} {
		set host "[maskhost $var0![getchanhost $var0 $chan] 2]"
		putnow "mode $chan +b $host"
	} else {
		putnow "mode $chan +b $var0"
	}
}

proc pub:kick {nick uhost hand chan text} {
	set var0 "[lindex [split $text] 0 ]"
	if {![botisop $chan]} {
		return 0
	}
	if {[isbotnick $var0]} {
	} elseif {[matchattr [nick2hand $var0] n]} {
		return 0
	} else {
		putquick "kick $chan $var0 $text"

	}
}

proc pub:kickban {nick uhost hand chan text} {
	set var0 "[lindex [split $text] 0 ]"
	if {![botisop $chan]} {
		return 0
	}
	if {[isbotnick $var0]} {
		return 0
	}
	if {[matchattr [nick2hand $var0] n]} {
	}
	if {[onchan $var0 $chan]} {
		set host "[maskhost $var0![getchanhost $var0 $chan] 2]"
		putquick "mode $chan +b $host"
		putquick "kick $chan $var0 $text"
	}
}

proc pub:unban {nick uhost hand chan text} {
	set var0 "[lindex [split $text] 0 ]"
	if {![botisop $chan]} {
		return 0
	}
	if {[onchan $var0 $chan]} {
		set host "[maskhost $var0![getchanhost $var0 $chan] 2]"
		putquick "mode $chan -b $host"
	} else {
		putnow "mode $chan -b $var0"
	}
}

proc pub:mute {nick uhost hand chan text} {
	global ircd
    set var0 "[lindex [split $text] 0 ]"
	if {![botisop $chan]} {return 0}
	if {[isbotnick $var0]} {return 0}
	if {[matchattr [nick2hand $var0] n]} {return 0}
	if {[onchan $var0 $chan]} {
		set host "[maskhost $var0![getchanhost $var0 $chan] 2]"
		if {($ircd == "1")} {putquick "mode $chan +b ~q:$host"}
        if {($ircd == "2")} {putquick "mode $chan +b m:$host"}
        if {($ircd == "3")} {putquick "mode $chan +q $var0"}
	} else {
		putquick "mode $chan +b ~q:$var0"
	}
}

proc pub:unmute {nick uhost hand chan text} {
	global ircd
    set var0 "[lindex [split $text] 0 ]"
	if {![botisop $chan]} {return 0}
	if {[isbotnick $var0]} {return 0}
	if {[matchattr [nick2hand $var0] n]} {return 0}
	if {[onchan $var0 $chan]} {
		set host "[maskhost $var0![getchanhost $var0 $chan] 2]"
		if {($ircd == "1")} {putquick "mode $chan -b ~q:$host"}
        if {($ircd == "2")} {putquick "mode $chan -b m:$host"}
        if {($ircd == "3")} {putquick "mode $chan -q $var0"}
	} else {
		putquick "mode $chan -b ~q:$var0"
	}
}

proc pub:rehash {nick uhost hand chan text} {
	putquick "PRIVMSG $chan :Rehashing..."
	rehash
}

proc pub:restart {nick uhost hand chan text} {
	putquick "PRIVMSG $chan :Restarting..."
	restart
}

proc pub:die {nick uhost hand chan text} {
	if {$text == ""} {
		die $nick
	} else { die $text }
}

proc pub:link {nick ushost handle chan text} {
	global pubcmd
	set var0 "[lindex [split $text] 0 ]"
	if {![llength [split $text]]} {
		putquick "privmsg $chan :Syntax: ${pubcmd}link <bot>"
		return 0
	}
	putquick "NOTICE $nick :Linking To $var0"
	link $var0
}

proc pub:unlink {nick ushost handle chan text} {
	global pubcmd
	set var0 "[lindex [split $text] 0 ]"
	if {![llength [split $text]]} {
		putquick "privmsg $chan :Syntax: ${pubcmd}link <bot>"
		return 0
	}
	putquick "NOTICE $nick :UnLinking from $var0"
	unlink $var0
}

proc pub:topic {nick uhost handle chan text} {
	if {![botisop $chan]} {
		return 0
	} else {
		set new2topic [lrange $text 0 end]
		putquick "topic $chan :$new2topic"
	}
}

proc pub:join {nick uhost handle chan text} {
	global pubcmd
	set var0 "[lindex [split $text] 0 ]"
	if {![llength [split $text]]} {
		putquick "privmsg $chan :Syntax: ${pubcmd}join <channel>"
		return 0
	}
	channel add $var0
	putquick "privmsg $chan :Successfully Joined $var0"
}

proc pub:part {nick uhost handle chan text} {
	global pubcmd
	set var0 "[lindex [split $text] 0 ]"
	if {![llength [split $text]]} {
		putquick "privmsg $chan :Syntax: ${pubcmd}part <channel>"
		return 0
	}
	channel remove $var0
	putquick "privmsg $chan :Successfully Parted $var0"
}

proc pub:chanset {nick uhost hand chan arg} {
	foreach {set value} [split $arg] {break}
	if {![info exists value]} {
		catch {channel set $chan $set} error
	} {
		catch {channel set $chan $set $value} error
	}
	if {$error == ""} {
		puthelp "privmsg $chan :Successfully set $arg"
	} {
		puthelp "privmsg $chan :Error setting $arg: [lindex $error 0]..."
	}
}

proc pub:cycle {nick uhost hand chan text} {
	set var0 "[lindex [split $text] 0 ]"
	if {[lindex [split $text] 0 ] != ""} {
	} else {
		set 2cycle $chan
	}
	putquick "PART $2cycle"
}

proc pub:invite {nick uhost hand chan text} {
	set var0 "[lindex [split $text] 0 ]"
	putquick "INVITE :$var0 $chan"
	putserv "privmsg $chan :Invited $var0 to $chan"
}

set vPingVersion 1.1

setudef flag ping

bind CTCR - PING pPingCtcrReceive
bind RAW - 401 pPingRawOffline

proc pPingTimeout {} {
	global vPingOperation
	set schan [lindex $vPingOperation 0]
	set snick [lindex $vPingOperation 1]
	set tnick [lindex $vPingOperation 2]
	putserv "PRIVMSG $schan :\00304Error\003 (\00314$snick\003) operation timed out attempting to ping \00307$tnick\003"
	unset vPingOperation
	return 0
}

proc pPingCtcrReceive {nick uhost hand dest keyword text} {
	global vPingOperation
	if {[info exists vPingOperation]} {
		set schan [lindex $vPingOperation 0]
		set snick [lindex $vPingOperation 1]
		set tnick [lindex $vPingOperation 2]
		set time1 [lindex $vPingOperation 3]
		if {([string equal -nocase $nick $tnick]) && ([regexp -- {^[0-9]+$} $text])} {
			set time2 [expr {[clock clicks -milliseconds] % 16777216}]
			set elapsed [expr {(($time2 - $time1) % 16777216) / 1000.0}]
			set char "O"
			if {[expr {round($elapsed / 0.5)}] > 10} {set red 10} else {set red [expr {round($elapsed / 0.5)}]}
			set green [expr {10 - $red}]
			set output \00303[string repeat $char $green]\003\00304[string repeat $char $red]\003
			putserv "PRIVMSG $schan :\00310Compliance\003 (\00314$snick\003) $output $elapsed seconds from \00307$tnick\003"
			unset vPingOperation
			pPingKillutimer
		}
	}
	return 0
}

proc pPingKillutimer {} {
	foreach item [utimers] {
		if {[string equal pPingTimeout [lindex $item 1]]} {
			killutimer [lindex $item 2]
		}
	}
	return 0
}

proc pPingPubCommand {nick uhost hand channel text} {
	global vPingOperation
	switch -- [llength [split [string trim $text]]] {
		0 {set tnick $nick}
		1 {set tnick [string trim $text]}
		default {
			putserv "PRIVMSG $channel :\00304Error\003 (\00314$nick\003) correct syntax is \00307!ping ?target?\003"
			return 0
		}
	}
	if {![info exists vPingOperation]} {
		if {[regexp -- {^[\x41-\x7D][-\d\x41-\x7D]*$} $tnick]} {
			set time1 [expr {[clock clicks -milliseconds] % 16777216}]
			putquick "PRIVMSG $tnick :\001PING [unixtime]\001"
			utimer 20 pPingTimeout
			set vPingOperation [list $channel $nick $tnick $time1]
		} else {putserv "PRIVMSG $channel :\00304Error\003 (\00314$nick\003) \00307$tnick\003 is not a valid nick"}
	} else {putserv "PRIVMSG $channel :\00304Error\003 (\00314$nick\003) a ping operation is still pending, please wait"}
	return 0
}

proc pPingRawOffline {from keyword text} {
	global vPingOperation
	if {[info exists vPingOperation]} {
		set schan [lindex $vPingOperation 0]
		set snick [lindex $vPingOperation 1]
		set tnick [lindex $vPingOperation 2]
		if {[string equal -nocase $tnick [lindex [split $text] 1]]} {
			putserv "PRIVMSG $schan :\00304Error\003 (\00314$snick\003) \00307$tnick\003 is not online"
			unset vPingOperation
			pPingKillutimer
		}
	}
	return 0
}
putlog "\00309PubCMD.tcl By ComputerTech Loaded\002"
#################################################################################################################################################################
