@echo off
set PYTHONPATH=%PYTHONPATH%;%~dp0..
python run_timing_tests.py
pause
