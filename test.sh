#!/bin/sh
export PYTHONPATH="./finviz-data:$PYTHONPATH"
python tests/test_finviz_data.py
