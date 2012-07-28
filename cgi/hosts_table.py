#!/usr/bin/python26

import ssnpcommon as ssnp, ujson as json, time

out = [ ]
outaux = [ ]
keys = [ 'host_name', 'current_state', 'plugin_output', 'last_check',
	'last_state_change', 'has_been_checked', 'problem_has_been_acknowledged',
	'is_flapping', 'checks_enabled', 'notifications_enabled', 'type' ]

reqobj = { 'keys': keys }
if 'hostgroup_name' not in ssnp.params:
	reqobj['list_hosts'] = True
	reqobj['expand_lists'] = True
else:
	reqobj['hostgroup_name'] = ssnp.params['hostgroup_name']
	reqobj['include_hosts'] = True

for o in ssnp.doreq(reqobj):
	if o['type'] != 'host':
		continue
	if 'only_problems' in ssnp.params:
		if o['current_state'] == 0:
			continue
		elif ssnp.params['only_problems'] == 'unhandled' and o['problem_has_been_acknowledged']:
			continue

	states = [ 'UP', 'DOWN', 'UNREACHABLE' ]
	state = states[o['current_state']] if o['has_been_checked'] else 'PENDING'

	so = [ o['host_name'], state, ssnp.tsstr(o['last_check']),
		ssnp.durstr(time.time(), o['last_state_change']), o['plugin_output'] ]

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

