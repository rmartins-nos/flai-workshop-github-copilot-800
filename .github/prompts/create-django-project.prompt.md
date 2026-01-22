---
description: 'Create a Django project, start it, and run it'
model: Claude Sonnet 4.5 (copilot)
---

Your task is to create the Django project 'octofit_tracker' in octofit-tracker/backend directory using the Python
virtual environment we already created in directory octofit-tracker/backend/venv which contains all the prerequisites.


To create the Django project follow these steps.
1. Make sure we are in the root directory and don't change directories
2. source octofit-tracker/backend/venv/bin/activate
3. django-admin startproject octofit_tracker in the "octofit-tracker/backend" directory
4. python manage.py migrate
5. Instruct the user to run the django app from the .vscode/launch.json configuration that is in the repository
