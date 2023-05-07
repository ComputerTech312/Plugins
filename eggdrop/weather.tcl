#################################
# CTweather
###
# Version: v0.0.3
# Author : ComputerTech
# GitHub : https://GitHub.com/computertech312
###
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
   variable api "API-Key"

   ## Metric type.
   # 0 = Metric
   # 1 = Imperial
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
         "1" {variable tempy "C" ; variable windy "KPH" ; variable typex "metric"}
         "0" {variable tempy "F" ; variable windy "MPH" ; variable typex "imperial"}
      }
      variable url "https://nominatim.openstreetmap.org/search/"
      variable params [::http::formatQuery q $text format jsonv2 ]
      variable jsonx [getdata $url $params]
      variable name [dict get [lindex $jsonx 0] "display_name"]
      variable lati [dict get [lindex $jsonx 0] "lat"]
      variable long [dict get [lindex $jsonx 0]  "lon"]
      variable url "https://api.openweathermap.org/data/2.5/weather"
      variable params [::http::formatQuery lat $lati lon $long appid $api units $typex]
      variable jsonx [getdata $url $params]
      variable temp [dict get [dict get $jsonx "main"] "temp"]
      variable speed [dict get [dict get $jsonx "wind"] "speed"]
      variable degre [dict get [dict get $jsonx "wind"] "deg"]
      variable humid [dict get [dict get $jsonx "main"] "humidity"]
      variable cover [dict get [dict get $jsonx "clouds"] "all"]
      variable desc [dict get [lindex [dict get $jsonx weather] 0] "description"]
      putserv "PRIVMSG $chan :\[\00309Weather\003\] Location: $name || Longitutde: $long  || Latitude: $lati || Temperature:: ${temp}$tempy"
      putserv "PRIVMSG $chan :Humidity: ${humid}% Wind:: ${speed}$windy  Degree: $degre || Description:: $desc  || Clouds: ${cover}%"
   }

   proc getdata {url params} {
      ::http::register https 443 [list ::tls::socket]
      ::http::config -useragent "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0"
      putlog "$url?$params"
      variable data [http::data [http::geturl "$url?$params" -timeout 10000]]
      ::http::cleanup $data
      variable jsonx [json::json2dict $data]
      return $jsonx
   }
}
