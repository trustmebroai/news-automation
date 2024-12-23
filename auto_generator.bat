@echo off
:start
python auto_generator.py
timeout /t 300
goto start 