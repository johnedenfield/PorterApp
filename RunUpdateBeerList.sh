#!/bin/bash
cd /var/www/Flask/Apps/PorterApp
source flask_env/bin/activate
python updatebeerlist.py

deactivate
#python /var/www/Flask/Apps/PorterApp/updatebeerlist.py
