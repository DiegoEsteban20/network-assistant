@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Creando entorno de Python...
  py -3 -m venv .venv || python -m venv .venv
)
".venv\Scripts\python.exe" -c "import psutil" 2>nul || (
  echo Instalando dependencias, solo la primera vez...
  ".venv\Scripts\python.exe" -m pip install -q -r requirements.txt
)
".venv\Scripts\python.exe" main.py %*
