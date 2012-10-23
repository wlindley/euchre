#!/bin/bash
#python -m unittest euchre_test game_test
nosetests --with-gae game_test.py euchre_test.py serializer_test.py
