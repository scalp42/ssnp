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
keys = [ 'host_name', 'service_description', 'max_attempts', 'current_attempt',
	'current_state', 'plugin_output', 'last_check', 'last_state_change',
	'has_been_checked', 'problem_has_been_acknowledged', 'type', 'is_flapping',
	'checks_enabled', 'notifications_enabled' ]
req.send_json({ 'list_services': True, 'expand_lists': True, 'keys': keys })
for o in json.loads(req.recv()):
	if o['type'] != 'service':
		continue
	if 'only_problems' in params:
		if o['current_state'] == 0:
			continue
		elif params['only_problems'] == 'unhandled' and o['problem_has_been_acknowledged']:
			continue

	states = [ 'OK', 'WARNING', 'CRITICAL', 'UNKNOWN' ]
	state = states[o['current_state']] if o['has_been_checked'] else 'PENDING'
	attempt = '{0}/{1}'.format(o['current_attempt'], o['max_attempts'])	

	so = [ o['host_name'], o['service_description'], state, tsstr(o['last_check']),
		durstr(time.time(), o['last_state_change']), attempt, o['plugin_output'] ]

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
