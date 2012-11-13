#!/bin/bash
#python -m unittest euchre_test game_test serializer_test
nosetests --with-gae game_test.py euchre_test.py serializer_test.py util_test.py executable_test.py
