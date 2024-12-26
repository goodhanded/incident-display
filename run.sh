#!/bin/bash

# Get the current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Run ./venv/bin/python days_since_incident.py
$DIR/venv/bin/python $DIR/days_since_incident.py