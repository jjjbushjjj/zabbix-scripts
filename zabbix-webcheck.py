#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import re
import sys


#### OUTPUT
# 2 digits
# 1st Web server response code 200 - 1 (Not 200 - 0)
# 2nd String to find (0 - Not found) (1 - Found) (2 - We don't supply string)

# Force encoding in code to UTF8 this need to be done 
# because user who run this code can have C locale and we can't decode args to utf for using in regexp func (re.findall)
reload(sys)
sys.setdefaultencoding('UTF8')

url = sys.argv[1]
regstr = sys.argv[2]
#regstr_utf = regstr.encode('cp1251').decode('utf8')

# in code we use utf string 
#regstr = regstr_utf

# We use this proxis by default you can overwrite them using command line
proxies = {
         "http": "http://zabbix_user:zabbix_passwd@proxy.roseurobank.ru:3128",  
         "https": "http://zabbix_user:zabbix_passwd@proxy.roseurobank.ru:3128"  
}

session = requests.session()
response = session.get(url, allow_redirects = True, proxies = proxies )

print response.text

# If we don't supply string to find just check webservers status code and exit
try:
    regstr
except NameError:
    if response.status_code is 200:
        del response
	# Return server is up and we don't looking for string
        print 12
        exit(1)
    else:
        del response
	# Return server return bad status code
        print 0
        exit(0)

# Try to find our substr. passed as second argument
m = re.findall(regstr, response.text)
if m:
    del response
    # Return server is up and we found req string on supplied url
    print 11
    exit(1)

# Find redirects in javascript code we looking for something like v16.blablabla
m = re.findall(r"location.replace\(\"(v\d+[a-zA-z0-9/.?=]+)\"\)", response.text)
if m:
    # now we have string with redirect generate new url and go there
    r_url = url + '/' + m[0] 
    response = session.get(r_url, allow_redirects = True, proxies = proxies )
    
    m = re.findall(regstr, response.text )
    if m:
        del response
	# Return server is up and we found string on page where javascript redirects us
        print 11
        exit(1) 
    else:
	del response
	# Return server is up but we don't find string on redirected page
	print 10
	exit(0)
	
del response

# fuck no luck!
print 0
exit(0) 
