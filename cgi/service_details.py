#!/usr/bin/python26

import ssnpcommon as ssnp, time, ujson as json

if 'host_name' not in ssnp.params:
	json.dumps({'type': 'error', 'msg': 'Host name not in request!' })
	exit(0)
if 'service_description' not in ssnp.params:
	json.dumps({'type': 'error', 'msg': 'Service description not in request!' })
	exit(0)

svc, err = None, None
keys = [ 'plugin_output', 'perf_data', 'latency', 'execution_time', 'is_flapping',
	'in_scheduled_downtime', 'last_check', 'next_check', 'last_notification',
	'current_notification_number', 'last_state_change', 'checks_enabled',
	'accept_passive_service_checks', 'flap_detection_enabled', 'notifications_enabled',
	'event_handler_enabled', 'obsess_over_service', 'type' ]
booleans = [ 'checks_enabled', 'accept_passive_service_checks', 'notifications_enabled',
	'flap_detection_enabled', 'event_handler_enabled', 'obsess_over_service' ]
datetimes = [ 'last_state_change', 'next_check', 'last_check', 'last_notification' ]
out = { 'textual': { }, 'booleans': { } }

for o in ssnp.doreq({'host_name': ssnp.params['host_name'],
	'service_description': ssnp.params['service_description'], 'keys': keys}):
	if o['type'] == 'error':
		err = o
		break
	elif o['type'] == 'service':
		svc = o
		break

if err:
	outstr = json.dumps(err)
	print """Content-Type: application/json
	Content-Length: {0}
	Cache-Control: no-cache

	{1}""".format(len(outstr), outstr)
	exit(0)

for k in datetimes:
	out['textual'][k] = ssnp.tsstr(svc[k])
for k in booleans:
	out['booleans'][k] = "ENABLED" if svc[k] else "DISABLED"
for k in [ 'plugin_output', 'perf_data' ]:
	out['textual'][k] = svc[k]

out['textual']['last_notification'] += ' (notification {0})'.format(
	svc['current_notification_number'])
out['textual']['is_flapping'] = "YES" if svc['is_flapping'] else "NO"
out['textual']['in_scheduled_downtime'] = "NO"
out['textual']['latency_duration'] = '{0}/{1} secs'.format(
	svc['latency'], svc['execution_time'])

outstr = json.dumps(out)
print """Content-Type: application/json
Content-Length: {0}
Cache-Control: no-cache

{1}""".format(len(outstr), outstr)
exit(0)

