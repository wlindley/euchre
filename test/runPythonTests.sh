#!/bin/bash
filePattern="*.py"
if [ -n "$1" ]; then
	filePattern=$1
fi
DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
nosetests --with-gae --gae-application=$DIR/.. $DIR/$filePattern
