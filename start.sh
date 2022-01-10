#!/bin/bash

python Main/manage.py makemigrations
python Main/manage.py migrate
python Main/manage.py runserver 0.0.0.0:8000