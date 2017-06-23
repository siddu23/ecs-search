#!/bin/bash 
set -e 
echo "=============== starting nginx ==============="
exec service nginx start &
echo "=============== starting gunicorn ==============="
exec gunicorn --workers 2 --bind unix:search.sock -u root -g www-data wsgi --log-level=debug
echo "=============== search startup done ==============="
