#!/usr/bin/env python

import os
import sys

def translateShortName(shortname):
	if "local" == shortname:
		return "familyeuchre-local"
	elif "stage" == shortname:
		return "familyeuchre-staging"
	return "familyeuchre"

def replaceAppId(yamlFilename, environment):
	handle = open(yamlFilename, 'r')
	lines = handle.readlines()
	for i in range(len(lines)):
		if lines[i].startswith("application:"):
			lines[i] = "application: " + translateShortName(environment) + "\n"
	handle.close()
	handle = open(yamlFilename, 'w')
	handle.writelines(lines)
	handle.close()

if __name__=="__main__":
	if len(sys.argv) < 3:
		print "Usage: %s <path/to/app.yaml> <environment>" % sys.argv[0]
		sys.exit(1)
	replaceAppId(sys.argv[1], sys.argv[2])
