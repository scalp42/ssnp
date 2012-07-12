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

keys = [ 'host_name', 'service_description', 'display_name',
	'max_attempts', 'current_attempt', 'current_state', 'plugin_output',
	'last_check', 'type', 'last_state_change', 'has_been_checked',
	'problem_has_been_acknowledged', 'notifications_enabled',
	'checks_enabled', 'is_flapping', 'has_been_checked',
	'latency', 'execution_time' ]
req.send(json.dumps({ 'list_hosts': True, 'expand_lists': True,
	'include_services': True, 'keys': keys }))

out = { 'services': { 'ok': [ ], 'warning': [ ], 'critical': [ ],
	'unknown': [ ], 'pending': [ ], 'latency': { 'min': float('Inf'),
	'max': 0, 'avg': 0}, 'exectime': { 'min': float('Inf'), 'max': 0,
	'avg': 0 } }, 'hosts': { 'up': [ ], 'down': [ ], 'unreachable': [ ],
	'pending': [ ], 'latency': { 'min': float('Inf'), 'max': 0,
	'avg': 0 }, 'exectime': { 'min': float('Inf'), 'max': 0, 'avg': 0 } } }
total_svcs = 0
total_hosts = 0

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

def compute_stats(otype, latency, exectime):
	global out
	out[otype]['latency']['min'] = min(out[otype]['latency']['min'], latency)
	out[otype]['latency']['max'] = max(out[otype]['latency']['max'], latency)
	out[otype]['latency']['avg'] += latency
	out[otype]['exectime']['min'] = min(out[otype]['exectime']['min'], exectime)
	out[otype]['exectime']['max'] = max(out[otype]['exectime']['max'], exectime)
	out[otype]['exectime']['avg'] += exectime

def add_service(svc):
	global out, total_svcs

	compute_stats('services', svc['latency'], svc['execution_time'])
	total_svcs += 1
		
	states = [ 'ok', 'warning', 'critical', 'unknown' ]
	attempt = '{0}/{1}'.format(svc['current_attempt'], svc['max_attempts'])
	so = [ svc['host_name'], svc['service_description'], tsstr(svc['last_check']),
		durstr(time.time(), svc['last_state_change']), attempt,
		svc['plugin_output'] ]

	if svc['has_been_checked']:
		out['services'][states[svc['current_state']]].append(so)
	else:
		out['services']['pending'].append(so)

def add_host(hst):
	global out, total_hosts

	compute_stats('hosts', hst['latency'], hst['execution_time'])
	total_hosts += 1

	states = [ 'up', 'down', 'unreachable' ]
	so = [ hst['host_name'], tsstr(hst['last_check']), durstr(time.time(),
		hst['last_state_change']), hst['plugin_output'] ]

	if hst['has_been_checked']:
		out['hosts'][states[hst['current_state']]].append(so)
	else:
		out['hosts']['pending'].append(so)

for o in json.loads(req.recv()):
	if o['type'] == 'service':
		add_service(o)
	elif o['type'] == 'host':
		add_host(o)

if total_hosts > 0:
	out['hosts']['latency']['avg'] /= total_hosts
	out['hosts']['exectime']['avg'] /= total_hosts
if total_svcs > 0:
	out['services']['latency']['avg'] /= total_svcs
	out['services']['exectime']['avg'] /= total_svcs
if out['hosts']['latency']['min'] == float('Inf'):
	out['hosts']['latency']['min'] = 0
if out['hosts']['exectime']['min'] == float('Inf'):
	out['hosts']['exectime']['min'] = 0
if out['services']['latency']['min'] == float('Inf'):
	out['services']['latency']['min'] = 0
if out['services']['exectime']['min'] == float('Inf'):
	out['services']['exectime']['min'] = 0

outstr = json.dumps(out)
print """Content-Type: application/json
Content-Length: {0}
Cache-Control: no-cache

""".format(len(outstr))
print outstr
