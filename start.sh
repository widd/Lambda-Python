#!/bin/sh
gunicorn -w 4 -b 0.0.0.0:80 --access-logfile - --error-logfile - lmda:app