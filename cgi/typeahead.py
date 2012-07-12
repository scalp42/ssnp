#!/usr/bin/python26
import time, zmq, os, cgi, ujson as json, cgitb
from datetime import timedelta, datetime

cgitb.enable()

zctx = zmq.Context()
req = zctx.socket(zmq.REQ)
req.connect("tcp://localhost:5557")

configfile = open('/etc/nagios/nagmq.conf', 'r')
config = json.load(configfile)
configfile.close()
config = config['cgi'] if 'cgi' in config else None

user = os.environ['REMOTE_USER']
params = cgi.parse()
def dedup(k):
	global params
	params[k] = params[k][0]
map(dedup, params.keys())

def resolve_user(username, contactgroup):
	req.send_json( { 'contactgroup_name': contactgroup,
		'keys': [ 'type', 'members' ] } )
	res = req.recv_json()
	if len(res) == 0:
		return False
	res = res[0]
	if res['type'] != 'contactgroup':
		return False
	if user not in set(res['members']):
		return False
	return True

if config and 'administrators' in config:
	if resolve_user(user, config['administrators']):
		user = None
	if 'for_user' in params:
		user = params['for_user']
elif config and 'readonly' in config:
	if resolve_user(user, config['readonly']):
		user = None

out = { }
req.send(json.dumps({'list_hosts': True, 'list_services': True}));

for o in json.loads(req.recv()):
	if o['type'] == 'service_list':
		def map_svc(s):
			out[s['service_description']] = True
		map(map_svc, o['services'])
	if o['type'] == 'host_list':
		def map_hst(h):
			out[h] = True
		map(map_hst, o['hosts'])		

outstr = json.dumps(out.keys())
print """Content-Type: application/json
Content-Length: {0}
Cache-Control: no-cache

""".format(len(outstr))
print outstr
