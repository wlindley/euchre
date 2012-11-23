#!/bin/bash
DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
nosetests --with-gae --gae-application=$DIR/.. $DIR/*.py
