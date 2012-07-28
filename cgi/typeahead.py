#!/usr/bin/python26

import ssnpcommon as ssnp, time, ujson as json

out = { }

for o in ssnp.doreq({'list_hosts': True, 'list_services': True,
	'list_hostgroups': True, 'list_servicegroups': True }):
	if o['type'] == 'service_list':
		def map_svc(s):
			out['Service ' + s['service_description']] = True
		map(map_svc, o['services'])
	if o['type'] == 'host_list':
		def map_hst(h):
			out['Host ' + h] = True
		map(map_hst, o['hosts'])
	if o['type'] == 'hostgroup_list':
		def map_hstgrp(h):
			out['Hostgroup ' + h] = True
		map(map_hstgrp, o['hostgroups'])
	if o['type'] == 'servicegroup_list':
		def map_svcgrp(h):
			out['Servicegroup ' + h] = True
		map(map_hstgrp, o['servicegroups'])


outstr = json.dumps(out.keys())
print """Content-Type: application/json
Content-Length: {0}
Cache-Control: no-cache

""".format(len(outstr))
print outstr
