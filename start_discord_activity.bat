@echo off
title Discord Activity
python -m pip install pypresence --quiet
python "%~dp0discord_activity.py"
pause