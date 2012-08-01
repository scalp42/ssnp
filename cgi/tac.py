#!/usr/bin/python26

import ssnpcommon as ssnp, ujson as json, time

out = { 'services_table': { 'data': [ ], 'auxData': [ ] },
	'hosts_table': { 'data': [ ], 'auxData': [ ] },
	'totals': { 'OK': 0, 'WARNING': 0, 'CRITICAL': 0, 'UNKNOWN': 0,
		'services-pending': 0, 'UP': 0, 'DOWN': 0, 'UNREACHABLE': 0, 
		'hosts-pending': 0 } }
svcid = 0;
hstid = 0;

tocopy = [ 'problem_has_been_acknowledged', 'is_flapping', 'notifications_enabled',
	'checks_enabled', 'accept_passive_service_checks', 'accept_passive_host_checks',
	'event_handler_enabled', 'flap_detection_enabled' ]

def add_service(svc):
	global out, svcid

	state_strs = [ 'OK', 'WARNING', 'CRITICAL', 'UNKNOWN' ]
	statestr = state_strs[svc['current_state']]
	if not svc['has_been_checked']:
		statestr = 'PENDING'
		out['totals']['services-pending'] += 1
	else:
		out['totals'][statestr] += 1
	attempt = '{0}/{1}'.format(svc['current_attempt'], svc['max_attempts'])
	so = [ svcid, svc['host_name'], svc['service_description'], statestr,
		ssnp.tsstr(svc['last_check']),
		ssnp.durstr(time.time(), svc['last_state_change']), attempt,
		svc['plugin_output'] ]

	sao = { }
	for k in tocopy:
		if k not in svc:
			continue;
		sao[k] = svc[k]
	
	out['services_table']['data'].append(so)
	out['services_table']['auxData'].append(sao)
	svcid += 1

def add_host(hst):
	global out, hstid

	state_strs = [ 'UP', 'DOWN', 'UNREACHABLE' ]
	statestr = state_strs[hst['current_state']]
	if not hst['has_been_checked']:
		statestr = 'PENDING'
		out['totals']['hosts-pending'] += 1
	else:
		out['totals'][statestr] += 1

	so = [ hstid, hst['host_name'], statestr, ssnp.tsstr(hst['last_check']),
		ssnp.durstr(time.time(), hst['last_state_change']),
		hst['plugin_output'] ]

	sao = { }
	for k in tocopy:
		if k not in hst:
			continue
		sao[k] = hst[k]

	out['hosts_table']['data'].append(so)
	out['hosts_table']['auxData'].append(sao)
	hstid += 1

keys = [ 'host_name', 'service_description', 'display_name',
	'max_attempts', 'current_attempt', 'current_state', 'plugin_output',
	'last_check', 'type', 'last_state_change', 'has_been_checked',
	'problem_has_been_acknowledged', 'notifications_enabled',
	'checks_enabled', 'is_flapping', 'has_been_checked',
	'accept_passive_service_checks', 'accept_passive_host_checks',
	'event_handler_enabled', 'flap_detection_enabled' ]

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
