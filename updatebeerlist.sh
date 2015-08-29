#!/bin/bash
cd /home/JohnEdenfield

workon porterenv

python updatebeerlist.py

deactivate

