#!/usr/bin/env python

import os
import sys

def replaceAppId(yamlFilename, appId):
	handle = open(yamlFilename, 'r')
	lines = handle.readlines()
	for i in range(len(lines)):
		if lines[i].startswith("application:"):
			lines[i] = "application: " + appId + "\n"
	handle.close()
	handle = open(yamlFilename, 'w')
	handle.writelines(lines)
	handle.close()

if __name__=="__main__":
	if len(sys.argv) < 3:
		print "Usage: %s <path/to/app.yaml> <app_id>" % sys.argv[0]
		sys.exit(1)
	replaceAppId(sys.argv[1], sys.argv[2])
