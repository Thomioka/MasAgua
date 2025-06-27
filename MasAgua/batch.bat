@echo off

rem Instalar lo necesario
py -m pip install setuptools
py -m pip install pillow
pip install transbank-sdk
pip install python-http-client
pip install django
pip install sendgrid
pip install requests

rem Iniciar servidor
py manage.py runserver

start http://127.0.0.1:8000/