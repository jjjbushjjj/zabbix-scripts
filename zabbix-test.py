#!/usr/bin/python

username='zabtech'
password='zabtechpwd'
hostgroup='Linux servers'
#test_server = 'ESB-T2'
#item_name='system.cpu.load[,avg1]'
#item1_name='vfs.fs.size[/,free]'
zabbix_url='http://srvmon.main.roseurobank.ru'

from zabbix_api.zabbix_api import ZabbixAPI
import sys
import re
import collections

def convert_bytes(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2fT' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2fG' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2fM' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2fK' % kilobytes
    else:
        size = '%.2fb' % bytes
    return size


def makehash():
    return collections.defaultdict( makehash )

def check_status( freep ):
    #print WARNING if free % less than 10
    if freep <= 10 and freep >=5: 
        return "WARNING"
    elif freep <= 5:
    # print CRITICAL if % less than 5
        return "CRITICAL"
    return "OK"
    

# Connect to Zabbix server
z=ZabbixAPI(server=zabbix_url)
z.login(user=username, password=password)

# Get hosts in the hostgroup
get_hostgroup = z.hostgroup.get(
    {
    'filter' : { 'name': hostgroup },
    'sortfield': 'name',
    'select_hosts':'extend'
    })

get_hosts = z.host.get(
        {
            'groupids': get_hostgroup[0]['groupid'],
            'output': "extend"
        })


# init dictionary for storing records
rezult = makehash()


print "All servers in Linux group"


for host in get_hosts:
    hostname = str( host['name'] )
    hostid = host['hostid']

    item = z.item.get(
            {
                'output': 'extend',
                'hostids': hostid,
#                'filter': { 'key_': item1_name }
                'search': { "key_": "vfs.fs.size" }
            })
    if item:
        for fs in item:
            ss = [ s.strip() for s in re.split(",|\[|\]", fs[ 'key_' ]) ] 
            ( mount_point, data_type ) = ss[1:3]
            if data_type == 'pfree':
                rezult[ hostname ][ mount_point ][ 'FreeP' ] = fs[ 'lastvalue' ]
            elif data_type == 'total':
                rezult[ hostname ][ mount_point ][ 'Total' ] = convert_bytes( fs[ 'lastvalue' ] )
            elif data_type == 'used':
                rezult[ hostname ][ mount_point ][ 'Used' ] = convert_bytes( fs[ 'lastvalue' ] )
            elif data_type == 'free':
                rezult[ hostname ][ mount_point ][ 'Free' ] = convert_bytes( fs[ 'lastvalue' ] )

    else:
       print "Host: %s No data" % hostname


# Output here
print "Server name              Size        Used        Free space      Free(%)    Status     Mount point"
print "--------------------     --------    --------    ------------    -------    ---------- --------------------------------"

for server, server_hash in rezult.items():
    for mount, mount_hash in server_hash.items():
        freep_float = float( rezult[server][mount ]['FreeP'] )
        freep_int = int( freep_float )
        freep_str = str( freep_int )
        print '{0:25s}{1:12s}{2:12s}{3:16s}{4:11s}{5:11s}{6:22s}'.format(
            server,
            rezult[server][mount ]['Total'], 
            rezult[server][mount ]['Used'], 
            rezult[server][mount ]['Free'],
            freep_str,
            check_status(freep_int),
            mount )
    print "............................................................................................................" 
