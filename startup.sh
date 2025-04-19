#!/bin/bash
pip install -r backend/requirements.txt
gunicorn backend.wsgi:application --chdir backend --bind=0.0.0.0