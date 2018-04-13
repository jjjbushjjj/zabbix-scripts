#!/usr/bin/python

#Get json output from status service web page
import urllib, json, sys
from socket import gethostname, getfqdn
import subprocess

# this require presence of xmltodict rpm package !
sys.path.append('/usr/local/lib/python2.7/dist-packages')
import xmltodict

name = sys.argv[1]
url_metrics = "http://localhost:"+sys.argv[2]+"/status.xml"
response = urllib.urlopen(url_metrics)

rez = '{\n"data":\n[\n'

o = xmltodict.parse( response.read() )
#print json.dumps(o, indent =3)
if sys.argv[3] == 'providers':
	for i in range(int(o['gateway']['smscs']['count']) ):
		# get id use it in name
		provider = o['gateway']['smscs']['smsc'][i]['id']
		rez+= '{"{#KNL_PROV}":"'+provider+'"}'
		if i!= (int(o['gateway']['smscs']['count'])-1):
			rez+= ',\n'
elif sys.argv[3] == 'boxes':
	for i in o['gateway']['boxes']['box']:
		rez+= '{"{#KNL_BOX}":"'+i['id']+'"}'
		if i != o['gateway']['boxes']['box'][-1]:
			rez+= ',\n'

rez+= '\n]\n}'

print rez

