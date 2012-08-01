#!/usr/bin/python26

import ssnpcommon as ssnp, ujson as json, time, zmq, os

req = json.loads(os.environ['QUERY_STRING'])
push = ssnp.zctx.socket(zmq.PUSH)
push.connect('tcp://localhost:5556')

def onoff_macro(val):
	return 1 if val == 'on' else 0

print """Content-Type: application/json
Cache-Control: no-cache
"""

if(len(req['targets']) == 0):
	print '{ "type": "error", "msg": "No targets for command!!!" }'
	exit(0)

if req['type'] == 'command':
	cmdname = None
	cmdmap = {
		'enable_notifications': [ 'enable_host_notifications', 'enable_service_notifications' ],
		'disable_notifications': [ 'disable_host_notifications', 'disable_service_notifications' ],
		'enable_checks': [ 'enable_host_checks', 'enable_service_checks'  ],
		'disable_checks': [ 'disable_host_checks', 'enable_service_checks' ],
		'enable_passive_checks': [ 'enable_passive_host_checks', 'enable_passive_service_checks' ],
		'disable_passive_checks': [ 'disable_passive_host_checks',
		'disable_passive_service_checks' ],
		'enable_event_handler': [ 'enable_host_event_handler', 'enable_service_event_handler' ],
		'disable_event_handler': [ 'enable_host_event_handler', 'disable_service_event_handler' ],
		'start_obsessing': [ 'start_obsessing_over_host', 'start_obsessing_over_service' ],
		'stop_obessing': [ 'stop_obsessing_over_host', 'stop_obsessing_over_service' ],
		'remove_acknowledgement': [ 'remove_host_acknowledgement', 'remove_service_acknowledgement' ]
	}

	if 'service_description' in req['targets'][0]:
		cmdname = cmdmap[req['command_name']][1]
	else:
		cmdname = cmdmap[req['command_name']][0]

	for t in req['targets']:
		t['type'] = 'command'
		t['command_name'] = cmdname
		push.send(json.dumps(t))

elif req['type'] == 'acknowledgement':
	ackobj = {
		'type': 'acknowledgement',
		'acknowledgement_type': onoff_macro(req['sticky_acknowledgement']),
		'comment_data': req['comment_data'],
		'author_name': os.environ['REMOTE_USER'],
		'notify_contacts': onoff_macro(req['notify_contacts']) == 1,
		'persistent_comment': onoff_macro(req['persistent_comment']) == 1,
		'time_stamp': { 'tv_sec': int(time.time()) }
	}
	for t in req['targets']:
		tonagios = ackobj.copy()
		for k in t:
			tonagios[k] = t[k]
		push.send(json.dumps(tonagios))

print json.dumps(req)
