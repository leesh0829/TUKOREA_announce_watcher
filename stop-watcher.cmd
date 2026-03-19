@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0stop-watcher.ps1" %*
