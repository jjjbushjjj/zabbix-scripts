#!/usr/bin/python

from zabbix_api.zabbix_api import ZabbixAPI
import sys
import datetime
import time
import shutil
import requests
from requests.auth import HTTPDigestAuth


def output_rezults ( mesg, items, time_from_str, time_now, hist_stat='', good_status='1' ):

    print "--- %s --- [ %s ] - [ %s ] ---" % ( mesg, time_from_str, time_now )
    for item,value in items.items():
        print "%s status: %s" % ( value[0], "OK" if value[1] == good_status else "ALERT" )
    if hist_stat:
        print "Has bad status at: "
        for key,val in hist_stat.items():
            print "%s changes time: %s" % ( items[key][0], val )
    print



def get_map_as_img ( zabbuser, zabbpassword, url ):
    # First we need to create session and login in zabbix server
    url1 = 'http://srvmon.main.roseurobank.ru/index.php'
    payload = {
        'name': zabbuser,
        'password': zabbpassword,
        'autologin': '1',
        'enter': 'Sign in'
    }
 
    session = requests.session()
    response = session.post(url1, data=payload, verify=False )
    # Second get our image url should contain image
    get_png = session.get( url, stream=True )
    # Save it to /tmp as img.png 
    with open('/tmp/img.png', 'wb') as out_file:
        shutil.copyfileobj(get_png.raw, out_file)
    del response
    del get_png


def get_hostid ( srv, zabb ):
    get_hostid = zabb.host.get ({
        'filter': { 'host': srv }
        })
#    print get_hostid
    return get_hostid[0]['hostid']

def get_items ( host_id, zabb, f_key='key_', f_item='' ):
    items = {}
    get_items = zabb.item.get ({
        'output': 'extend',
        'hostids': host_id,
        'search': { f_key: f_item }
        })
    for i in get_items:
#        print i['itemid']
#        print i['name']
#        print i['lastvalue']
        items[ i['itemid'] ] = ( i['name'], i['lastvalue'] )

    return items

def get_trigger ( zabb, hostids , trigger_desc):
    items = {}
    get_trigger = zabb.trigger.get ({
        'output': 'extend',
        'hostids': hostids,
        'search':{ 'description': trigger_desc }
        })
    for i in get_trigger:
        items[ i['triggerid'] ] = ( i['description'], i['value'], 
                datetime.datetime.fromtimestamp( float(i['lastchange']) ).strftime('%Y-%m-%d %H:%M:%S') )
#    print get_trigger
    return items

def get_history ( items, zabb, good_status, time_from=''):
    item_changes = {}
    get_history = zabb.history.get({
        'itemids': items,
        'time_from': time_from,
        'output': 'extend',
        })
    times = []
    for i in get_history:
        if i['value'] not in good_status:
            time_str = datetime.datetime.fromtimestamp( float(i['clock']) ).strftime('%Y-%m-%d %H:%M:%S')
    #        print "Item: %s Value %s changed from good status in %s" % ( i['itemid'], i['value'], i['clock'] )
            times.append(time_str)
            item_changes[ i['itemid'] ] = times
    #print item_changes
    return item_changes

if __name__ == "__main__":
    username='username'
    password='password'
    hostgroup='Linux servers'
    #test_server = 'ESB-T2'
    #item_name='system.cpu.load[,avg1]'
    #item1_name='vfs.fs.size[/,free]'
    zabbix_url='zabbix server url'
    # Get date in unix timestamp format we looking for items history -1 day till now
    time_from = int(time.time()) - (24 * 60 * 60)
    time_now = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    time_from_str = datetime.datetime.fromtimestamp( float(time_from) ).strftime('%Y-%m-%d %H:%M:%S')
    # Connect to Zabbix server
    z=ZabbixAPI(server=zabbix_url, timeout = 100 )
    z.login(user=username, password=password)

    #Global goodval value
    good_val = '1'

    # Check NTP service ntp1,2.roseurobank.ru
    hostid = get_hostid ( 'SCARAB2', z )
    items = get_items ( hostid, z, 'key_', 'NTP')
    hist_stat = get_history (items.keys(), z, good_val, time_from ) 
    # Compile output for NTP
    output_rezults( 'NTP(1,2).ROSEUROBANK.RU service', items, time_from_str, time_now, hist_stat )

    # Check DHCP service
    hostid = get_hostid ( 'SCARAB', z )
    items = get_items ( hostid, z, 'key_', 'DHCP')
    hist_stat = get_history (items.keys(), z, good_val, time_from ) 
    # Compile output for DHCP
    output_rezults( 'SCARAB.MAIN.ROSEUROBANK.RU  DHCP service', items, time_from_str, time_now, hist_stat )

    # Check DHCP service
    hostid = get_hostid ( 'SCARAB2', z )
    items = get_items ( hostid, z, 'key_', 'DHCP')
    hist_stat = get_history (items.keys(), z, good_val, time_from ) 
    # Compile output for DHCP
    output_rezults( 'SCARAB2.MAIN.ROSEUROBANK.RU  DHCP service', items, time_from_str, time_now, hist_stat )

    # Check NTP service ntp1,2.main.roseurobank.ru
    hostid = get_hostid ( 'Zabbix server', z )
    items = get_items ( hostid, z, 'key_', 'NTP')
    hist_stat = get_history (items.keys(), z, good_val, time_from ) 
    # Compile output for NTP
    output_rezults( 'NTP(1,2).MAIN.ROSEUROBANK.RU service', items, time_from_str, time_now, hist_stat )

    # Check DNS service
    # We use same host for items quering so we don't need to call get_hostid() again
    items = get_items ( hostid, z, 'key_', 'DNS')
    hist_stat = get_history (items.keys(), z, good_val, time_from ) 
    # Compile output for DNS
    output_rezults( 'DNS service', items, time_from_str, time_now, hist_stat )

    # Check PROXY.ROSEUROBANK.RU 
    hostid = get_hostid ( 'Zabbix server', z )
    items = get_items ( hostid, z, 'key_', 'proxy.roseurobank.ru')
    hist_stat = get_history (items.keys(), z, good_val, time_from ) 
    # Compile output for PROXY
    output_rezults( 'PROXY.ROSEUROBANK.RU', items, time_from_str, time_now, hist_stat )

    # Check PROXY2.ROSEUROBANK.RU
    hostid = get_hostid ( 'Zabbix server', z )
    items = get_items ( hostid, z, 'key_', 'proxy2.roseurobank.ru')
    hist_stat = get_history (items.keys(), z, good_val, time_from ) 
    # Compile output for PROXY2
    output_rezults( 'PROXY2.ROSEUROBANK.RU', items, time_from_str, time_now, hist_stat )

    hist_stat= ''
    good_status = '0'
    # Availability Webchecks on zabbix server
    print "--- Webchecks aggregated report [ %s ] - [ %s ] ----------------------------" % ( time_from_str, time_now )
    print
    hostids = get_hostid ( 'Zabbix server', z )
    items = get_trigger ( z, hostids, 'ibanking.rosevrobank.ru availability' ) 
    output_rezults( 'IBANKING.ROSEUROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'vb.rosevrobank.ru availability' )
    output_rezults( 'VB.ROSEUROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'www.rosevrobank.ru availability' )
    output_rezults( 'WWW.ROSEUROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )

    items = get_trigger ( z, hostids, 'WEBCheck_chlb.rosevrobank.ru' )
    output_rezults( 'CHLB.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_chlb1.rosevrobank.ru' )
    output_rezults( 'CHLB1.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_msk.rosevrobank.ru' )
    output_rezults( 'MSK.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_msk1.rosevrobank.ru' )
    output_rezults( 'MSK1.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_msk2.rosevrobank.ru' )
    output_rezults( 'MSK2.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_ekt.rosevrobank.ru' )
    output_rezults( 'EKT.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_ekt1.rosevrobank.ru' )
    output_rezults( 'EKT1.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_mbext.rosevrobank.ru' )
    output_rezults( 'MBEXT.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_nvsb.rosevrobank.ru' )
    output_rezults( 'NVSB.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_nvsb1.rosevrobank.ru' )
    output_rezults( 'NVSB1.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_rst.rosevrobank.ru' )
    output_rezults( 'RST.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_rst1.rosevrobank.ru' )
    output_rezults( 'RST1.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_smr.rosevrobank.ru' )
    output_rezults( 'SMR.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_smr1.rosevrobank.ru' )
    output_rezults( 'SMR1.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_spb.rosevrobank.ru' )
    output_rezults( 'SPB.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_spb1.rosevrobank.ru' )
    output_rezults( 'SPB1.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_webquik.rosevrobank.ru' )
    output_rezults( 'WEBQUIK.ROSEVROBANK.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_ecommrussia.ru' )
    output_rezults( 'ECOMMRUSSIA.RU', items, time_from_str, time_now, hist_stat, good_status )
    items = get_trigger ( z, hostids, 'WEBCheck_ipoteka2015.ru' )
    output_rezults( 'IPOTEKA2015.RU', items, time_from_str, time_now, hist_stat, good_status )







    #Get image from maps BPC
    get_map_as_img ( username, password, 'http://srvmon.main.roseurobank.ru/map.php?sysmapid=6&severity_min=0' )


 
