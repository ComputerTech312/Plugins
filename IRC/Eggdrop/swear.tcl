#################################################################################################################################################################
# swear.tcl
#################################################################################################################################################################
#Author    ComputerTech
#IRC       ircs://irc.technet.chat/6697 #computertech
#Email     ComputerTech312@gmail.com
#GitHub    https://github.com/computertech312
#Version   0.1
#Released  28/02/2021
#################################################################################################################################################################
# Description:
#
#               A Elaborate Bad word script
#  
#               .chanset #channel +ctswear   to enable the script
#
# History:
#
#               - 0.1: First Release.
#
#################################################################################################################################################################
# Start Of Configuration #
##########################
## Swear Words
##
set ctswear(words) {
"*fuck*"
"*cunt*"
"*wanker"
"*tranny*"
"*bastard*"
}

###########################
## Seconds of undo of each warning value
##
set ctswear(reset) "60"

###########################
## Ban Time(in minutes)
##
set ctswear(time) "60"

###########################
## Max warnings(Set to 0 to disable)
##
set ctswear(max) "2"

###########################
## Punishment
##
#Disable = 0
#kick    = 1
#ban     = 2
#kickban = 3
set ctswear(pun) "3"

###########################
## Output
##
#Channel = 0
#Privmsg = 1
#Notice  = 2

set ctswear(out) "2"

###########################
## Reason
##
# %nick    = Nick
# %badword = Swear word
# %chan    = Channel
# %time    = Ban time

set ctswear(rea) "Reason: Usage of Swear Word ( %badword )  Bantime: %time  Channel: %chan"

##################
## Ban hostmask Type
##
#0 *!user@host
#1 *!*user@host
#2 *!*@host
#3 *!*user@*.host
#4 *!*@*.host
#5 nick!user@host
#6 nick!*user@host
#7 nick!*@host
#8 nick!*user@*.host
#9 nick!*@*.host

set ctswear(btype) "2"

########################
# End Of Configuration #
#################################################################################################################################################################
setudef flag ct:swear

namespace eval ct:swear {

bind pubm - * ::ct:swear::swear:pub

proc swear:pub {nick host hand chan text} {
global ctswear botnick
if {[channel get $chan ctswear]} {
   foreach badword $ctswear(words) {
set ctswear(reason) [string map [list %nick $nick %badword $badword %time $ctswear(time) %chan $chan] $ctswear(words)] 
set ctswear(host) "[maskhost $nick![getchanhost $nick $chan] $ctswear(btype)]"
switch -- $ctswear(out) {
  0 {set ctswear(output) "PRIVMSG $chan"}
  1 {set ctswear(output) "PRIVMSG $nick"}
  2 {set ctswear(output) "NOTICE $nick"}
}
    if {[string match -nocase $badword $text]} {
incr ctswear($host) +1
if {![$ctswear($host) > $ctswear(max)]} {
putserv "$ctswear(output) :Warning! Swearing is prohibited on $chan, cease immediately"
utimer $ctswear(reset) {incr warn($host) -1 }
} else {
switch -- $ctswear(pun) {
  0 {return 0}
  1 {putquick "KICK $chan $nick $ctswear(reason)"}
  2 {newchanban "$chan" "$ctswear(host)" "$::botnick" "$ctswear(reason)" $ctswear(time)}              
  3 {[newchanban "$chan" "$ctswear(host)" "$::botnick" "$ctswear(reason)" $ctswear(time)] && [putquick "KICK $chan $nick $ctswear(reason)"]}
}
set warn($host) "0"
     }
    }
   }
  }
 }
}
