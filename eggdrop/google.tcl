######################################################################################
# Google.tcl
######################################################################################
#Author    ComputerTech
#IRC       ircs://irc.rizon.net:6697/computertech
#Email     computertech312@gmail.com
#GitHub    https://github.com/computertech312
#Version   0.4
#Released  03/03/2023
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
# History:
#
#               - 0.4: Added safesearch option and fixed/improved code.
#               - 0.3: Added Max results option.
#               - 0.2: Fixed a few minor bugs.
#               - 0.1: First release.
#
######################################################################################

namespace eval Googler {

    #########################
   # Start of configuration.
   ##
   
    # Set the trigger command for the script
    variable trig !google
   
    # Set the flags for the script
    variable flags ofmn
   
    # Set the API key for the Google Custom Search API
    variable api_key "Your-API-Key"
   
    # Set the ID for the search engine associated with the API key
    variable engine_id "Your-Engine-ID"
   
    # Set the message type for the script
    #
    # The message type determines whether the output should be sent as a notice
    # to the user, a private message to the user, or a message to the channel.
    #
    # 0 = notice
    # 1 = private message
    # 2 = channel message
    variable message_type 2
   
    # Set the maximum number of search results to display
    #
    # This setting determines the maximum number of search results to display
    # in the output. The default is 3, but it can be set to any positive integer.
    variable max_results 3
   
    # Set the safe search mode for the script
    #
    # The safe search mode determines how explicit or potentially offensive
    # search results should be filtered. The available options are:
    #
    # "off": No filtering is applied.
    # "medium": Potentially explicit results are filtered, but not offensive
    #            content that is considered safe by some users.
    # "high": All explicit or potentially offensive content is filtered.
    #
    # The default setting is "high".
    variable safe_search "high"
   
   # Set logo
   variable logo "\0032G\0034o\0038o\0032g\0033l\0034e\003"
   
   #########################
   ## End of configuration.
   
    package require json
    package require tls
    package require http
    bind PUB $flags $trig [namespace current]::google_search
   
   proc google_search {nick host hand chan text} {
   http::register https 443 [list ::tls::socket]
   variable data [http::data [http::geturl "https://www.googleapis.com/customsearch/v1?[::http::formatQuery key $::Googler::api_key cx $::Googler::engine_id q [join $text +] safe $::Googler::safe_search]" -timeout 10000]]
   variable result_dict [::json::json2dict $data]
   variable search_info [dict get $result_dict "searchInformation"]
   variable search_results [dict get $result_dict "items"]
   variable num_results [dict get $search_info "formattedTotalResults"]
   variable search_time [dict get $search_info "formattedSearchTime"]
   switch -- $::Googler::message_type {
        "0" {set output "NOTICE $nick"}
        "1" {set output "PRIVMSG $nick"}
        "2" {set output "PRIVMSG $chan"}
    }
   variable output_string "$::Googler::logo About $num_results results ($search_time seconds)"
   putserv "$output :$output_string"
    foreach result [lrange $search_results 0 [expr {$::Googler::max_results - 1}]] {
        set title [dict get $result "title"]
        set link [dict get $result "link"]
        set snippet [dict get $result "snippet"]
        putserv "$output :$title / $link / $snippet"
    }
    http::unregister https
    http::cleanup $data
   
    putlog "$::Googler::logo.tcl v0.4 by ComputerTech Loaded"
   }
}
