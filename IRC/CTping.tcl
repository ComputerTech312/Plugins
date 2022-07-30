##################################################################################################
# CT-ping.tcl                                                                                    #
##################################################################################################
# Author    ComputerTech                                                                         #                                                      #
# Email     ComputerTech312@Gmail.com                                                            #
# GitHub    https://github.com/computertech312                                                   #
# Version   0.2                                                                                  #
# Released  15/04/2021                                                                           #
##################################################################################################
#                                                                                                #
# Description:                                                                                   #
#                                                                                                #
#               An Elaborate Public and Message Command Script.                                  #                                                               #
#                                                                                                #
#                                                                                                #
# Credits:                                                                                       #
#                                                                                                #
#               Special thanks to Suntop, Sir_Fz, Spyda, BdS, CrazyCat                           #
#               and many others for all of the help.                                             #
#                                                                                                #
# History:                                                                                       #
#                                                                                                #
#               - 0.2: Added namespace.                                                          #
#               - 0.1: First release.                                                            #
#                                                                                                #
##################################################################################################
namespace eval CTcommands {
variable ctp

##########################
# Start Of Configuration #                                                                     
#________________________#

##################
# Set trigger of the commands.
##
set ctp(trig) "!ping !p"


###################
# Set flag for Commands.
##
# Owner     = n
# Master    = m
# Op        = o
# Halfop    = h
# Voice     = v
# Friend    = f
# Everyone  = -   
##          
set ctp(flag) "omn"


##################
# Set to use Notice Or Privmsg for Output of Commands.
##
# 1 = Notice
# 2 = Privmsg
# 3 = Channel
##
set ctp(msg) "1"


##################
# Set Colour for output.
##
# Black       = 0
# Black       = 1
# Dark Blue   = 2
# Green       = 3
# Red         = 4
# Brown       = 5
# Purple      = 6
# Orange      = 7
# Yellow      = 8
# Light Green = 9
# DarkCyan    = 10
# LightCyan   = 11
# LightBlue   = 12
# Pink        = 13
# Dark Grey   = 14
# Light Grey  = 15
##
set ctp(col) "3"

########################
# End Of Configuration #
#______________________#

##################################################################################################

foreach ctp(word) $ctp(trig) {bind PUBM $ctp(flag) "$ctp(word)" [namespace current]::pingi}
 bind CTCR - PING [namespace current]::pingr

proc pingi {nick host hand chan text} {
	 global ping
    set ping(who) [lindex [split $text] 0]
  if {$ping(who) == ""} {set ping(who) $nick}
   putserv "PRIVMSG $ping(who) :\001PING [clock clicks -milliseconds]\001"
    set pingchan($nick) $chan
    utimer 20 {time:out $nick $text}
}
proc pingr {nick host hand dest key text} {
	 global ping pingchan
    set chan $pingchan($nick)
    set ping(time) [expr {([clock clicks -milliseconds] - $text) / 1000.000}]
        switch -- $ping(msg) {
        "0" {set ping(output) "NOTICE $nick"}
        "1" {set ping(output) "PRIVMSG $nick"}
        "2" {set ping(output) "PRIVMSG $pingchan($nick)"}
        }
        set ctp($nick) 1
    putserv "$ping(output) :\[0030{$ping(col)}PING\003\] reply from $ping(who): \[0030${ping(col)}$ping(time)\003\] seconds"
        unset pingchan($nick)
}
proc time:out {nick text} {
variable ping
 if {![info exists ctp($nick)]} {
 	  putserv "$ping(output) :\00304Error\003 Timeout trying to ping $ping(who)"
 } else {
 	  unset ping($nick)
   }
  }
}
##################################################################################################
