#!/usr/bin/python26

import time, zmq, os, cgi, simplejson as json, cgitb
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

def tsstr(timestamp):
	if timestamp == 0:
		return 'N/A'
	return str(datetime.fromtimestamp(timestamp))

def durstr(a, b):
	if b == 0:
		return 'forever'
	td = datetime.fromtimestamp(a) - datetime.fromtimestamp(b)
	td -= timedelta(microseconds=td.microseconds)
	return str(td)

out = [ ]
outaux = [ ]
keys = [ 'host_name', 'current_state', 'plugin_output', 'last_check',
	'last_state_change', 'has_been_checked', 'problem_has_been_acknowledged',
	'is_flapping', 'checks_enabled', 'notifications_enabled', 'type' ]
req.send_json({ 'list_hosts': True, 'expand_lists': True, 'keys': keys })
for o in json.loads(req.recv()):
	if o['type'] != 'host':
		continue
	if 'only_problems' in params:
		if o['current_state'] == 0:
			continue
		elif params['only_problems'] == 'unhandled' and o['problem_has_been_acknowledged']:
			continue

	states = [ 'UP', 'DOWN', 'UNREACHABLE' ]
	state = states[o['current_state']] if o['has_been_checked'] else 'PENDING'

	so = [ o['host_name'], state, tsstr(o['last_check']),
		durstr(time.time(), o['last_state_change']), o['plugin_output'] ]

	soa = { 'problem_has_been_acknowledged': o['problem_has_been_acknowledged'],
		'is_flapping': o['is_flapping'], 'checks_enabled': o['checks_enabled'],
		'notifications_enabled': o['notifications_enabled'] }

	out.append(so)
	outaux.append(soa)

outstr = json.dumps({ 'aaData': out, 'auxdata': outaux })
print """Content-Type: application/json
Content-Length: {0}
Cache-Control: no-cache

""".format(len(outstr))
print outstr

