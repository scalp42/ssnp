#!/usr/bin/python26

import ssnpcommon as ssnp, ujson as json, time

out = { 'services': { 'ok': { 'data': [ ], 'auxData': [ ] }, 'warning': {
	'data': [ ], 'auxData': [ ] }, 'critical': { 'data': [ ], 'auxData': [ ] },
	'unknown': { 'data': [ ], 'auxData': [ ] }, 'pending': { 'data': [ ],
	'auxData': [ ] } }, 'hosts': { 'up': { 'data': [ ], 'auxData': [ ] }, 
	'down': { 'data': [ ], 'auxData': [ ] }, 'unreachable': { 'data': [ ],
	'auxData': [ ] }, 'pending': { 'data': [ ], 'auxData': [ ] } } }

tocopy = [ 'problem_has_been_acknowledged', 'is_flapping', 'notifications_enabled',
	'checks_enabled' ]

def add_service(svc):
	global out
		
	states = [ 'ok', 'warning', 'critical', 'unknown' ]
	attempt = '{0}/{1}'.format(svc['current_attempt'], svc['max_attempts'])
	so = [ svc['host_name'], svc['service_description'], 
		ssnp.tsstr(svc['last_check']),
		ssnp.durstr(time.time(), svc['last_state_change']), attempt,
		svc['plugin_output'] ]

	sao = { }
	for k in tocopy:
		sao[k] = svc[k]

	if svc['has_been_checked']:
		out['services'][states[svc['current_state']]]['data'].append(so)
		out['services'][states[svc['current_state']]]['auxData'].append(sao)
	else:
		out['services']['pending']['data'].append(so)
		out['services']['pending']['auxData'].append(sao)

def add_host(hst):
	global out

	states = [ 'up', 'down', 'unreachable' ]
	so = [ hst['host_name'], ssnp.tsstr(hst['last_check']), 
		ssnp.durstr(time.time(), hst['last_state_change']),
		hst['plugin_output'] ]

	sao = { }
	for k in tocopy:
		sao[k] = hst[k]

	if hst['has_been_checked']:
		out['hosts'][states[hst['current_state']]]['data'].append(so)
		out['hosts'][states[hst['current_state']]]['auxData'].append(sao)
	else:
		out['hosts']['pending']['data'].append(so)
		out['hosts']['pending']['auxData'].append(sao)

keys = [ 'host_name', 'service_description', 'display_name',
	'max_attempts', 'current_attempt', 'current_state', 'plugin_output',
	'last_check', 'type', 'last_state_change', 'has_been_checked',
	'problem_has_been_acknowledged', 'notifications_enabled',
	'checks_enabled', 'is_flapping', 'has_been_checked' ]

for o in ssnp.doreq({ 'list_hosts': True, 'expand_lists': True,
	'include_services': True, 'keys': keys }):
	if o['type'] == 'service':
		add_service(o)
	elif o['type'] == 'host':
		add_host(o)

outstr = json.dumps(out)
print """Content-Type: application/json
Content-Length: {0}
Cache-Control: no-cache

""".format(len(outstr))
print outstr
