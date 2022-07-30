#################################
# CTweather
###
# Version: v0.0.3 (+variable-adjusted)
# Author : ComputerTech
# GitHub : https://GitHub.com/computertech312
###

##################################
###  +variable-adjusted Notes  ###
# Corrected the usage of [variable] inside procs.
# Corrected the "Metric type" setting explanation.
##################################

namespace eval CTweather {
   ## Triggers.
   # Current weather.
   variable trig "!w"
   ##

   ## Flags.
   # n = Owner.
   # m = master
   # o = Op.
   # h = Halfop.
   # v = Voice.
   # f = Friend.
   # - = Nothing.
   variable flag "-|-"
   ##

   ## OpenWeatherMap API Key.
   variable api "8c2a600d5d63d7fb13432fd58dcc419b"

   ## Metric type.
   # 0 = Imperial
   # 1 = Metric
   variable type "0"

   ###

   package require json
   package require tls
   package require http

   bind PUB $flag $trig [namespace current]::current:weather

   proc current:weather {nick host hand chan text} {
      variable api ; variable type
      if {![llength [split $text]]} {
         putserv "privmsg $chan :Syntax: !w \[zip code | Location \]"
         return 0
      }
      switch -exact $type {
         "0" {set tempy "F" ; set windy "MPH" ; set typex "imperial"}
         "1" {set tempy "C" ; set windy "KPH" ; set typex "metric"}
      }

      set url "https://nominatim.openstreetmap.org/search/"
      set params [::http::formatQuery q $text format jsonv2 ]
      set jsonx [getdata $url $params]
      set name [dict get [lindex $jsonx 0] "display_name"]
      set lati [dict get [lindex $jsonx 0] "lat"]
      set long [dict get [lindex $jsonx 0]  "lon"]

      set url "https://api.openweathermap.org/data/2.5/weather"
      set params [::http::formatQuery lat $lati lon $long appid $api units $typex]
      set jsonx [getdata $url $params]
      set temp [dict get [dict get $jsonx "main"] "temp"]
      set speed [dict get [dict get $jsonx "wind"] "speed"]
      set degre [dict get [dict get $jsonx "wind"] "deg"]
      set humid [dict get [dict get $jsonx "main"] "humidity"]
      set cover [dict get [dict get $jsonx "clouds"] "all"]
      set desc [dict get [lindex [dict get $jsonx weather] 0] "description"]

      putserv "PRIVMSG $chan :\[\00309Weather\003\] Location: $name || Longitutde: $long  || Latitude: $lati || Temperature:: ${temp}$tempy"
      putserv "PRIVMSG $chan :Humidity: ${humid}% || Wind:: ${speed}$windy  Degree: $degre || Description:: $desc  || Clouds: ${cover}%"
   }

   proc getdata {url params} {
      ::http::register https 443 [list ::tls::socket]
      ::http::config -useragent "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0"

      putlog "$url?$params"

      set data [http::data [http::geturl "$url?$params" -timeout 10000]]
      ::http::cleanup $data
      set jsonx [json::json2dict $data]
      return $jsonx
   }
}
