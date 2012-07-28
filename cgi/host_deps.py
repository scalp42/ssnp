#!/usr/bin/python26

import ssnpcommon as ssnp, ujson as json, time

out = [ ]
keys = [ 'host_name', 'current_state', 'parent_hosts', 'child_hosts', 'type',
	'has_been_checked' ]
reqobj = { 'keys': keys }
if 'hostgroup_name' in ssnp.params:
	reqobj['hostgroup_name'] = ssnp.params['hostgroup_name']
	reqobj['include_hosts'] = True
else:
	reqobj['list_hosts'] = True
	reqobj['expand_lists'] = True

for o in ssnp.doreq(reqobj):
	if o['type'] != 'host':
		continue
	states = [ 'UP', 'DOWN', 'UNREACHABLE' ]
	if not o['has_been_checked']:
		o['current_state'] = 'PENDING'
	else:
		o['current_state'] = states[o['current_state']]
	del o['has_been_checked']
	out.append(o)

outstr = json.dumps(out)
print """Content-Type: application/json
Content-Length: {0}
Cache-Control: no-cache

{1}""".format(len(outstr), outstr)
