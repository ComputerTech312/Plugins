# -*- coding: UTF-8 -*-

import hexchat
import requests
import json
import socket

__module_name__ = "ip-lookup"
__module_version__ = "1.0"
__module_description__ = "Looks up IP's"

def ip_cb(word, word_eol, userdata):
    ip = word[1]
    url = 'http://ipwho.is/' + ip
    response = requests.get(url)
    data = json.loads(response.text)
    country = data["country"]
    continent = data["continent"]
    city = data["city"]
    connection = data["connection"]
    isp = connection["isp"]
    rdns = socket.getnameinfo((ip, 0), 0)
    print(f'Location: {city} {country}, {continent}')
    print(f'ISP: {isp} {rdns}')
    return hexchat.EAT_ALL
    
hexchat.hook_command('ip', ip_cb, help='IP <ip>')
    