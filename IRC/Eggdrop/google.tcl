
######################################################################################
# Google.tcl
######################################################################################
#Author    ComputerTech
#IRC       irc.technet.chat  #ComputerTech
#Email     ComputerTech312@gmail.com
#GitHub    https://github.com/computertech312
#Version   0.3
#Released  21/03/2021
######################################################################################
# Description:
#
#               - An Elaborate Google Search Script.
#               - After 100 usages of the script, it will automatically stop until the next day.
#               - Grab your own API key from here
#                 https://developers.google.com/custom-search/v1/overview
#               - And a Engine ID from here
#                 https://cse.google.com/cse/
#
# Credits:
#
#               - Special thanks to launchd, spyda and CrazyCat.
#
# History:
#
#               - 0.3: Added Max results option.
#               - 0.2: Fixed a few minor bugs.
#               - 0.1: First release.
#
######################################################################################
# Start Of Configuration #
##########################
# Set trigger of the script.
##
set ctgg(trig) "!google"


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
set ctgg(flag) "-"


###################
# Set API Key
##
set ctgg(api) "Your-API-Key"


##################
# Set Engine ID
##
set ctgg(id) "Your-Engine-ID"


##################
# Set to use Notice Or Privmsg for Output of Commands
##
# 0 = Notice
# 1 = Privmsg
# 2 = Channel
##
set ctgg(msg) "2"


##################
# Set amount of results to output
##
set ctgg(max) "3"


########################
# End Of Configuration #
######################################################################################

bind PUB $ctgg(flag) $ctgg(trig) goo:gle

package require json
package require tls
package require http

proc goo:gle {nick host hand chan text} {
   global ctgg google
   set ::google "\00302G\00304o\00308o\00302g\00303l\00304e\003"
   http::register https 443 [list ::tls::socket]
   set url "https://www.googleapis.com/customsearch/v1?key=$ctgg(api)&cx=$ctgg(id)&q=[join $text +]"
   set data "[http::data [http::geturl "$url" -timeout 10000]]"
    http::cleanup $data
   set datadict [::json::json2dict $data]
   set items2 [dict get $datadict "searchInformation"]
          switch -- $ctgg(msg) {
         "0" {set ctgg(output) "NOTICE $nick "}
         "1" {set ctgg(output) "PRIVMSG $nick"}
         "2" {set ctgg(output) "PRIVMSG $chan"}
      }
    set time [dict get $items2 "formattedSearchTime"]
    set total [dict get $items2 "formattedTotalResults"]
    putserv "$ctgg(output) :$google  About $total results ($time seconds)"
    set items [dict get $datadict "items"]
   for {set i 0} {$i < $ctgg(max)} {incr i} {
      set item [lindex $items $i]
      set title [dict get $item "title"]
      set link [dict get $item "link"]
      set info [dict get $item "snippet"]
      putserv "$ctgg(output) : $title / $link / $info"
   }
      http::unregister https
}
putlog "$::google.tcl v0.3 by ComputerTech Loaded"
######################################################################################
