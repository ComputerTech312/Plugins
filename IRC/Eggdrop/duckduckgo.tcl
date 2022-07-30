######################################################################################
# DuckDuckGo.tcl
######################################################################################
#Author    ComputerTech
#IRC       irc.technet.chat  #ComputerTech
#Email     ComputerTech312@gmail.com
#GitHub    https://github.com/computertech312
#Version   0.1
#Released  21/03/2021
######################################################################################
# Description:
#
#               - A Script which uses DuckDuckGo's API key to Search.
#              
# History:
#
#               - 0.1: First release.
#
######################################################################################
# Start Of Configuration #
##########################
# Set trigger of the script. 
##
set ctddg(trig) "!duckduckgo"

###################
# Set flag for Commands.
##
# Owner     = n
# Master    = m
# Op        = o
# Voice     = v
# Friend    = f
# Everyone  = -
##
set ctddg(flag) "ofmn"

##################
# Set to use Notice Or Privmsg for Output of Commands
##
# 0 = Notice
# 1 = Privmsg
# 2 = Channel
##
set ctddg(msg) "2"

########################
# End Of Configuration #
######################################################################################

bind PUB $ctddg(flag) $ctddg(trig) duck:duck:go

proc duck:duck:go {nick host hand chan text} {
 global ctddg
 http::register https 443 [list ::tls::socket]
   set url "https://api.duckduckgo.com/?q=[join $text +]&format=json&no_html&pretty=1"
    set data [http::data [http::geturl "$url" -timeout 10000]]
     set datadict [::json::json2dict $data]
      set heading [dict get $datadict "Heading"]
       set result [dict get $datadict "Text"]
        set link [dict get $datadict "FirstURL"]
        switch -- $ctddg(msg) {
        "0" {set ctddg(output) "NOTICE $nick"}
        "1" {set ctddg(output) "PRIVMSG $nick"}
        "2" {set ctddg(output) "PRIVMSG $chan"}
        }
        putserv "$ctddg(output) :\0037,0DuckDuckGo\003 $heading / $link / $result"
  http::unregister https
  http::cleanup $data
}
######################################################################################
