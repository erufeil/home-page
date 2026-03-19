@echo off
call venv\Scripts\activate.bat

for /f "usebackq tokens=1,* delims== eol=#" %%A in (".env") do (
    set "%%A=%%B"
)
python -m backend.app