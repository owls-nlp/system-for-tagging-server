#!/bin/bash

python3 /home/flask_app/worker.py &
python3 /home/flask_app/flask_app.py

