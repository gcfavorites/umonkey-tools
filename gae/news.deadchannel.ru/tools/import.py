#!/usr/bin/env python

import os
import simplejson
import sys
import urllib
import urllib2

def post(url, data):
	for k in data.keys():
		if type(data[k]) == list:
			data[k] = u', '.join(data[k])
		if type(data[k]) == unicode:
			data[k] = data[k].encode('utf-8')
		if not data[k]:
			del data[k]

	u = urllib2.urlopen(urllib2.Request(url, urllib.urlencode(data)))
	if u is not None:
		return u.read()

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print >>sys.stderr, 'Usage: %s filename.json url' % os.path.basename(sys.argv[0])
		sys.exit(1)

	if not os.path.exists(sys.argv[1]):
		print >>sys.stderr, 'File %s not found.' % sys.argv[1]
	data = simplejson.loads(open(sys.argv[1]).read())

	for news in data[-10:]:
		print 'Updating node/%s' % news['id']
		try:
			post(sys.argv[2], news)
		except Exception, e:
			print >>sys.stderr, 'Error adding node/%s, see server logs.' % news['id']
