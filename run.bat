@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动 Streamlit 应用...
call streamlit run streamlit_app.py
pause
