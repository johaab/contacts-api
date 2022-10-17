#!/usr/bin/env bash

# create and initialize environment
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
# initialize database
flask --app contacts_app init-db
# run application
flask --app contacts_app run


#