@echo off
REM Primera vez: desactiva cualquier env activo, activa el venv, instala dependencias y carga .env

call deactivate 2>nul

call venv\Scripts\activate.bat

pip install -r backend\requirements.txt

for /f "usebackq tokens=1,* delims== eol=#" %%A in (".env") do (
    set "%%A=%%B"
)

python -m backend.app
