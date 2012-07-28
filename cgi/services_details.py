#!/usr/bin/python26

import ssnpcommon as ssnp, time, ujson as json

if 'host_name' not in ssnp.params:
	json.dumps({'type': 'error', 'msg': 'Host name not in request!' })
	exit(0)

svc, hst, err = None, None, None
reqobj = { 'host_name': ssnp.params['host_name'] }
if 'service_description' in ssnp.params:
	reqobj['service_description'] = ssnp.params['service_description']

for o in ssnp.doreq(reqobj):
	if o['type'] == 'error':
		err = o
		break
	elif o['type'] == 'service':
		states = [ 'OK', 'WARNING', 'CRITICAL', 'UNKNOWN' ]
		o['current_state'] = states[o['current_state']]
		o['last_state'] = states[o['last_state']]
		o['last_hard_state'] = states[o['last_hard_state']]
		if not o['has_been_checked']:
			o['current_state'] = 'PENDING'
		svc = o
	elif o['type'] == 'host':
		states = [ 'UP', 'DOWN', 'UNREACHABLE' ]
		o['current_state'] = states[o['current_state']]
		o['last_state'] = states[o['last_state']]
		o['last_hard_state'] = states[o['last_hard_state']]
		if not o['has_been_checked']:
			o['current_state'] = 'PENDING'
		hst = o

outstr = json.dumps({ 'service': svc, 'host': hst, 'error': err })
print """Content-Type: application/json
Content-Length: {0}
Cache-Control: no-cache

{1}""".format(len(outstr), outstr)
