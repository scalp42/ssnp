#!/usr/bin/python26

import ssnpcommon as ssnp, time, ujson as json

out = [ ]
outaux = [ ]
keys = [ 'host_name', 'service_description', 'max_attempts', 'current_attempt',
	'current_state', 'plugin_output', 'last_check', 'last_state_change',
	'has_been_checked', 'problem_has_been_acknowledged', 'type', 'is_flapping',
	'checks_enabled', 'notifications_enabled' ]


reqobj = { 'keys': keys }
if 'host_name' in ssnp.params:
	reqobj['host_name'] = ssnp.params['host_name']
	reqobj['include_services'] = True
elif 'servicegroup_name' in ssnp.params:
	reqobj['servicegroup_name'] = ssnp.params['servicegroup_name']
	reqobj['include_services'] = True
elif 'service_description' in ssnp.params:
	reqobj['list_services'] = ssnp.params['service_description']
else:
	reqobj['list_services'] = True
reqobj['expand_lists'] = True

for o in ssnp.doreq(reqobj):
	if o['type'] != 'service':
		continue
	if 'only_problems' in ssnp.params:
		if o['current_state'] == 0:
			continue
		elif ssnp.params['only_problems'] == 'unhandled' and o['problem_has_been_acknowledged']:
			continue

	states = [ 'OK', 'WARNING', 'CRITICAL', 'UNKNOWN' ]
	state = states[o['current_state']] if o['has_been_checked'] else 'PENDING'
	attempt = '{0}/{1}'.format(o['current_attempt'], o['max_attempts'])	

	so = [ o['host_name'], o['service_description'], state, ssnp.tsstr(o['last_check']),
		ssnp.durstr(time.time(), o['last_state_change']), attempt, o['plugin_output'] ]

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
