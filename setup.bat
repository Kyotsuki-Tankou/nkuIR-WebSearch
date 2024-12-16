@echo off

REM Set the current directory to the directory of the batch file
cd /d %~dp0

REM Start Elasticsearch
start "" "elasticsearch.lnk"

REM Start backend
start "" cmd /k "python backend\main.py"

REM Start frontend
start "" cmd /k "cd frontend && npm start"