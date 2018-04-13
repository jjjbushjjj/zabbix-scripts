#!/usr/bin/python

#Get json output from status service web page
import urllib, json, sys
from socket import gethostname, getfqdn
import subprocess

# this require presence of xmltodict rpm package !
sys.path.append('/usr/local/lib/python2.7/dist-packages')
import xmltodict
# zbxsend.py must be present in current directory

zabbix_server_url = 'fqdn of zabbix server or proxy'
zabbix_server_port = 'port'


hostname = getfqdn()

def metric_send( item, val, host = hostname, zbx_serv = zabbix_server_url, zbx_serv_port = zabbix_server_port ):
    print "This is sent to zabbix: item - %s value - %s" % (item, val)
    subprocess.call(["/usr/sbin/zabbix-sender",
                     "-z",
                     zbx_serv,
                     "-p",
                     zbx_serv_port,
                     "-s",
                     host,
                     "-k",
                     item,
                     "-o",
                     val
                   ])

# we pass 2 params to this script
# 1 name of kannel instance You could set any meaningful name here
# 2 admin port

name = sys.argv[1]
url_metrics = "http://localhost:"+sys.argv[2]+"/status.xml"
response = urllib.urlopen(url_metrics)


o = xmltodict.parse( response.read() )
#print json.dumps(o, indent =3)

#print "%s.status.state %s " % ( name, o['gateway']['status'].split(',')[0] )
metric_send( name+'.status.state', o['gateway']['status'].split(',')[0] )

#print "%s.sms.inbound %s" % ( name, o['gateway']['sms']['inbound'] )
metric_send( name+'.sms.inbound', o['gateway']['sms']['inbound'] )

#print "%s.sms.received.total %s" % ( name, o['gateway']['sms']['received']['total'] )
metric_send( name+'.sms.received.total', o['gateway']['sms']['received']['total'] )

#print "%s.sms.received.queued %s" % ( name, o['gateway']['sms']['received']['queued'] )
metric_send( name+'.sms.received.queued', o['gateway']['sms']['received']['queued'] )

#print "%s.sms.outbound %s" % ( name, o['gateway']['sms']['outbound'] )
metric_send( name+'.sms.outbound', o['gateway']['sms']['outbound'] )

#print "%s.sms.sent.total %s" % ( name, o['gateway']['sms']['sent']['total'] )
metric_send( name+'.sms.sent.total', o['gateway']['sms']['sent']['total'] )

#print "%s.sms.sent.queued %s" % ( name, o['gateway']['sms']['sent']['queued'] )
metric_send( name+'.sms.sent.queued', o['gateway']['sms']['sent']['queued'] )

#print "%s.sms.storesize %s" % ( name, o['gateway']['sms']['storesize'] )
metric_send( name+'.sms.storesize', o['gateway']['sms']['storesize'] )

#print "%s.smscs.count %s" % ( name, o['gateway']['smscs']['count'] )
metric_send( name+'.smscs.count', o['gateway']['smscs']['count'] )

if int(o['gateway']['smscs']['count']) > 1:
# here we could have list of our sms providers loop over it to get all values
	for i in range(int(o['gateway']['smscs']['count']) ):
		# get id nam use it in name
		provider = o['gateway']['smscs']['smsc'][i]['id']
#		print "%s.smscs.smsc.%s.status %s " % ( name, i, o['gateway']['smscs']['smsc'][i]['status'].split()[0] )
		metric_send( name+'.smscs.smcs.'+provider+'.status', o['gateway']['smscs']['smsc'][i]['status'].split()[0] )

		if isinstance(o['gateway']['smscs']['smsc'][i]['received'], dict):
#			print "%s.smscs.smsc.%s.received %s " % ( name, i, o['gateway']['smscs']['smsc'][i]['received']['sms'] )
			metric_send( name+'.smscs.smcs.'+provider+'.received', o['gateway']['smscs']['smsc'][i]['received']['sms'] )
		else:
#			print "%s.smscs.smsc.%s.received %s " % ( name, i, o['gateway']['smscs']['smsc'][i]['received'] )
			metric_send( name+'.smscs.smcs.'+provider+'.received', o['gateway']['smscs']['smsc'][i]['received'] )

#		print "%s.smscs.smsc.%s.name %s " % ( name, i, o['gateway']['smscs']['smsc'][i]['name'] )
		metric_send( name+'.smscs.smcs.'+provider+'.name', o['gateway']['smscs']['smsc'][i]['name'] )

#		print "%s.smscs.smsc.%s.queued %s " % ( name, i, o['gateway']['smscs']['smsc'][i]['queued'] )
		metric_send( name+'.smscs.smcs.'+provider+'.queued', o['gateway']['smscs']['smsc'][i]['queued'] )

#		print "%s.smscs.smsc.%s.failed %s " % ( name, i, o['gateway']['smscs']['smsc'][i]['failed'] )
		metric_send( name+'.smscs.smcs.'+provider+'.failed', o['gateway']['smscs']['smsc'][i]['failed'] )

#		print "%s.smscs.smsc.%s.id %s " % ( name, i, o['gateway']['smscs']['smsc'][i]['id'] )
#		metric_send( name+'.smscs.smcs.'+provider+'.id', o['gateway']['smscs']['smsc'][i]['id'] )

		if isinstance(o['gateway']['smscs']['smsc'][i]['sent'], dict ):
#			print "%s.smscs.smsc.%s.sent %s " % ( name, i, o['gateway']['smscs']['smsc'][i]['sent']['sms'] )
			metric_send( name+'.smscs.smcs.'+provider+'.sent', o['gateway']['smscs']['smsc'][i]['sent']['sms'] )
		else:
#			print "%s.smscs.smsc.%s.sent %s " % ( name, i, o['gateway']['smscs']['smsc'][i]['sent'] )
			metric_send( name+'.smscs.smcs.'+provider+'.sent', o['gateway']['smscs']['smsc'][i]['sent'] )
else:
#	print "%s.smscs.smsc.status %s " % ( name, o['gateway']['smscs']['smsc']['status'].split()[0] )
	metric_send( name+'.smscs.smcs.status', o['gateway']['smscs']['smsc']['status'].split()[0] )

	if isinstance(o['gateway']['smscs']['smsc']['received'], dict):
#		print "%s.smscs.smsc.received %s " % ( name, o['gateway']['smscs']['smsc']['received']['sms'] )
		metric_send( name+'.smscs.smcs.received', o['gateway']['smscs']['smsc']['received']['sms'] )
	else:
#		print "%s.smscs.smsc.%s.received %s " % ( name, i, o['gateway']['smscs']['smsc']['received'] )
		metric_send( name+'.smscs.smcs.received', o['gateway']['smscs']['smsc']['received'] )

#	print "%s.smscs.smsc.name %s " % ( name, o['gateway']['smscs']['smsc']['name'] )
	metric_send( name+'.smscs.smcs.name', o['gateway']['smscs']['smsc']['name'] )

#	print "%s.smscs.smsc.queued %s " % ( name, o['gateway']['smscs']['smsc']['queued'] )
	metric_send( name+'.smscs.smcs.queued', o['gateway']['smscs']['smsc']['queued'] )

#	print "%s.smscs.smsc.failed %s " % ( name, o['gateway']['smscs']['smsc']['failed'] )
	metric_send( name+'.smscs.smcs.failed', o['gateway']['smscs']['smsc']['failed'] )

#	print "%s.smscs.smsc.id %s " % ( name, o['gateway']['smscs']['smsc']['id'] )
	metric_send( name+'.smscs.smcs.id', o['gateway']['smscs']['smsc']['id'] )

	if isinstance(o['gateway']['smscs']['smsc']['sent'], dict ):
#		print "%s.smscs.smsc.sent %s " % ( name, o['gateway']['smscs']['smsc']['sent']['sms'] )
		metric_send( name+'.smscs.smcs.sent', o['gateway']['smscs']['smsc']['sent']['sms']  )
	else:
#		print "%s.smscs.smsc.%s.sent %s " % ( name, i, o['gateway']['smscs']['smsc']['sent'] )
		metric_send( name+'.smscs.smcs.sent', o['gateway']['smscs']['smsc']['sent'] )

