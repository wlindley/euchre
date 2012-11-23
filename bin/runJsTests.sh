#!/bin/bash
DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
java -jar $DIR/JsTestDriver.jar --tests all
