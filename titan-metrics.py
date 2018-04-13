#!/usr/bin/python

#Get json output from status service web page
import urllib, json
import re
import os
import subprocess

from socket import gethostname

# WARNING those url must NOT be under balancer we need directly ask local service for it's metrics!
url_metrics = "http://localhost:8080/titan-sv/metrics"
response = urllib.urlopen(url_metrics)
metrics = json.loads(response.read())

# WARNING those url must NOT be under balancer we need directly ask local service for it's metrics!
url_health = "http://localhost:8080/titan-sv/health"
response = urllib.urlopen(url_health)
health = json.loads(response.read())

# Zabbix server fqdn
zabbix_server_url = 'your zabbix server fqdn'
zabbix_server_port = 'port'

#Hostname the name of host that send those messages correspond to REAL Hostname in zabbix (UPPER CASE) name
hostname = gethostname().upper()


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



# Metrics
#print "Metrics"
for key, val in metrics.items():
    if type(val) is not dict:
        continue
    for element, value in val.items():
        if type(value) is not dict:
            continue
        for a, b in value.items():
            # Remove bad sybols from item names so zabbix could acept them
            item = re.sub('[ !@#$\']', '', key) + "." + re.sub('[!@#$]', '', element) + "." + re.sub('[!@#$]', '', a)
    #        print "Item: %s ---- Value: %s type - %s" % ( item, str(metrics[key][element][a]), type(metrics[key][element][a]) )
            metric_send( item, str(metrics[key][element][a]) )
#Health
#print
#print "Health"
for key, val in health.items():
    if type(val) is not dict:
        continue
    for element, value in val.items():
            # Remove bad sybols from item names so zabbix could acept them
            item = re.sub('[ !@#$\']', '', key) + "." + re.sub('[!@#$]', '', element)
     #       print "Item: %s ---- Value: %s - %s" % ( item, str(health[key][element]), type(health[key][element]) )
	    metric_send( item, str(health[key][element]) )


#What we can get from metrics
#metric_send( 'gauges.oracle.aq.queue.size.AQ_SVISTA_MESSAGE_QUEUES_E', metrics['gauges']['oracle.aq.queue.size.AQ$_SVISTA_MESSAGE_QUEUES_E']['value'] )
#metric_send( 'gauges.oracle.aq.queue.size.SVISTA_CBS2PC_RESP', metrics['gauges']['oracle.aq.queue.size.SVISTA_CBS2PC_RESP']['value'] )
#metric_send( 'gauges.oracle.aq.queue.size.SVISTA_OUT', metrics['gauges']['oracle.aq.queue.size.SVISTA_OUT']['value'])
#metric_send( 'gauges.oracle.aq.queue.size.SVISTA_PC2CBS_FORPOST', metrics['gauges']['oracle.aq.queue.size.SVISTA_PC2CBS_FORPOST']['value'] )
#metric_send( 'gauges.oracle.aq.queue.size.SVISTA_PC2CBS_RESP', metrics['gauges']['oracle.aq.queue.size.SVISTA_PC2CBS_RESP']['value'] )
# Counters
#metric_send('counters.pcToCbs-async.count', metrics['counters']['pcToCbs-async']['count'] )
#metric_send( 'meters.cbsToPc-async.average', metrics['meters']['cbsToPc-async.average']['count'] )
#metric_send( 'meters.cbsToPc-sync.average', metrics['meters']['cbsToPc-sync.average']['count'] )
#metric_send( 'meters.pcToCbs-async.average', metrics['meters']['pcToCbs-async.average']['count'] )
#metric_send( 'meters.pcToCbs-sync.average', metrics['meters']['pcToCbs-sync.average']['count'] )
#Timers
#metric_send( 'timers.FAILED.null_route21', metrics['timers']['FAILED.null_route21']['count'] )
#metric_send( 'timers.FAILED.pcToCbs-async_pcToCbs.async.responseToPC', metrics['timers']['FAILED.pcToCbs-async_pcToCbs.async.responseToPC']['count'] )
#metric_send( 'timers.FAILED.pcToCbs-async_pcToCbs.async.toForpost', metrics['timers']['FAILED.pcToCbs-async_pcToCbs.async.toForpost']['count'] )
#metric_send( 'timers.null_route21', metrics['timers']['null_route21']['count'] )
#metric_send( 'timers.pcToCbs-async_pcToCbs.async.toForpost', metrics['timers']['pcToCbs-async_pcToCbs.async.toForpost']['count'] )
#metric_send( 'timers.pcToCbs-async_pcToCbs.wsEntry', metrics['timers']['pcToCbs-async_pcToCbs.wsEntry']['count'] )
# What we can get from health
#metric_send( 'AtomikosConnectionFactoryBeanforpostJms.healthy', str(health["AtomikosConnectionFactoryBean 'forpostJms'"]['healthy']) )
#metric_send( 'titanJmsFp.healthy', str(health["AtomikosConnectionFactoryBean 'titanJmsFp'"]['healthy']) )
#metric_send( 'titanJmsFpRs.healthy', str(ihealth["AtomikosConnectionFactoryBean 'titanJmsFpRs'"]['healthy']) )
#metric_send( 'titanJmsIn.healthy', str(health["AtomikosConnectionFactoryBean 'titanJmsIn'"]['healthy']) )
#metric_send( 'titanJmsOut.healthy', str(health["AtomikosConnectionFactoryBean 'titanJmsOut'"]['healthy']) )
#metric_send( 'oracle.aq.queue.size.NON_ZERO.AQ_SVISTA_MESSAGE_QUEUES_E.healthy', str (health["oracle.aq.queue.size.NON_ZERO.AQ$_SVISTA_MESSAGE_QUEUES_E"]['healthy']) )
#metric_send( 'oracle.aq.queue.size.NON_ZERO.AQ_SVISTA_MESSAGE_QUEUES_E.message', health["oracle.aq.queue.size.NON_ZERO.AQ$_SVISTA_MESSAGE_QUEUES_E"]['message'] )
#metric_send( 'oracle.aq.queue.size.SVISTA_CBS2PC_RESP.healthy', str(health["oracle.aq.queue.size.SVISTA_CBS2PC_RESP"]['healthy']) )
#metric_send( 'oracle.aq.queue.size.SVISTA_CBS2PC_RESP.message', health["oracle.aq.queue.size.SVISTA_CBS2PC_RESP"]['message'] )
#metric_send( 'oracle.aq.queue.size.SVISTA_OUT.healthy', str(health["oracle.aq.queue.size.SVISTA_OUT"]['healthy']) )
#metric_send( 'oracle.aq.queue.size.SVISTA_OUT.message', health["oracle.aq.queue.size.SVISTA_OUT"]['message'] )
#metric_send( 'oracle.aq.queue.size.SVISTA_PC2CBS_FORPOST.healthy', str(health["oracle.aq.queue.size.SVISTA_PC2CBS_FORPOST"]['healthy']) )
#metric_send( 'oracle.aq.queue.size.SVISTA_PC2CBS_FORPOST.message', health["oracle.aq.queue.size.SVISTA_PC2CBS_FORPOST"]['message'] )
#metric_send( 'oracle.aq.queue.size.SVISTA_PC2CBS_RESP.healthy', str(health["oracle.aq.queue.size.SVISTA_PC2CBS_RESP"]['healthy']) )
#metric_send( 'oracle.aq.queue.size.SVISTA_PC2CBS_RESP.message', health["oracle.aq.queue.size.SVISTA_PC2CBS_RESP"]['message'] )
#metric_send( 'oracle.aq.queue.size.increase.AQ_SVISTA_MESSAGE_QUEUES_E.healthy', str(health["oracle.aq.queue.size.increase.AQ$_SVISTA_MESSAGE_QUEUES_E"]['healthy']) )
#metric_send( 'oracle.aq.queue.size.increase.AQ_SVISTA_MESSAGE_QUEUES_E.message', health["oracle.aq.queue.size.increase.AQ$_SVISTA_MESSAGE_QUEUES_E"]['message'] )
#metric_send( 'pcToCbs-async.performanceDeviation.healthy', str(health["pcToCbs-async.performanceDeviation"]['healthy']) )
#metric_send( 'pcToCbs-async.performanceDeviation.message', health["pcToCbs-async.performanceDeviation"]['message'] )
#metric_send( 'pcToCbs-sync.performanceDeviation.healthy', str(health["pcToCbs-sync.performanceDeviation"]['healthy']) )
#metric_send( 'pcToCbs-sync.performanceDeviation.message', health["pcToCbs-sync.performanceDeviation"]['message'] )
