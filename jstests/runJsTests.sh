#!/bin/bash
DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
java -jar $DIR/../bin/JsTestDriver.jar --tests all --config $DIR/../jsTestDriver.conf
