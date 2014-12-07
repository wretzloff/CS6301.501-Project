from gluon.contrib.memcache import MemcacheClient
import re


######## README ###########
#Before running application, config correct memcache ports in web2py directory
#1. cache.memcache is memcache for this request node
#2. cache.distmemcache is the distributed cache list for other nodes
###########################

##This code will detect what host and port web2py is running on
##And will map to a memcache server port based on memcache_config.txt file
"""
url = URL(r=request, host=True)
match = re.match(r'http:\/\/(.+):(\d+)\/.+', url)
distributedServerList = list()

if match:
	host = match.group(1)
	port = match.group(2)

	portTuple = None
	with open('memcache_config.txt') as f:
		for line in f.readlines():
			#print line
			tmp = line

			if port in line:
				tmp = tmp.replace('\n', '').replace(' ', '')
				portTuple = tuple(tmp.split(':'))
				#print portTuple
			else:
				tmp = tmp.replace('\n', '').replace(' ', '')
				distributedServerTuple = tuple(tmp.split(':'))
				distributedServerUrl = '%s:%s' % (host, distributedServerTuple[1])
				distributedServerList.append(distributedServerUrl)

	##Set up node's memcache server
	server = '%s:%s' % (host, portTuple[1])
	#print server

	memcache_servers = [server]
	cache.memcache = MemcacheClient(request, memcache_servers)
	cache.ram = cache.disk = cache.memcache

	##Set up access to distributed memcache servers
	cache.distmemcache = MemcacheClient(request, distributedServerList)

else:
	print "Memcache not setup: No port found in %s" % url
"""

memcache_servers = ['127.0.0.1:11211']
cache.memcache = MemcacheClient(request, memcache_servers)
cache.ram = cache.disk = cache.memcache