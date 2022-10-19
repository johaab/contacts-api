#!/usr/bin/env bash

# create and initialize environment
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
# initialize database
flask --app contacts_app init-db
# run application
flask --app contacts_app run

# register
curl -X POST -F username='john' -F password='johndoe' http://localhost:5000/auth/register
# login
curl -X POST -F username='john' -F password='johndoe' http://localhost:5000/auth/login

# check who is logged in
curl http://localhost:5000/auth/whoisloggedin

# read whole database
curl http://localhost:5000/contacts
curl http://localhost:5000/skills

# read info of a single person
curl http://localhost:5000/contacts/1
curl http://localhost:5000/skills/1

# add new contact info
curl -X POST -F firstname='john' -F lastname='doe' -F address='doesstreet 7' -F email='john@doe.com' -F phone='1234567890' http://localhost:5000/contacts
