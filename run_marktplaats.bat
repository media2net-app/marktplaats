@echo off
cd /d %~dp0
if not exist logs mkdir logs
powershell -NoProfile -ExecutionPolicy Bypass -Command "python scripts\post_ads.py --csv products.csv --keep-open 2>&1 | Tee-Object -FilePath 'logs\\last_run.log'"
echo.
echo Log opgeslagen in logs\last_run.log
pause
{
  "cells": [],
  "metadata": {
    "language_info": {
      "name": "python"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 2
}