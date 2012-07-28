#!/usr/bin/python26

import ssnpcommon as ssnp, ujson as json, time, zmq

push = ssnp.zctx.socket(zmq.PUSH)
push.connect("tcp://localhost:5556")
push.send(json.dumps(ssnp.params))

outstr = json.dumps(ssnp.params)
print """Content-Type: application/json
Content-Length: {0}
Cache-Control: no-cache

{1}""".format(len(outstr),outstr)
