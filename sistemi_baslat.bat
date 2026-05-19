@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
title Niko AI - Kontrol Merkezi

:: --- YAPILANDIRMA ---
set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"
set "MAIN_SCRIPT=%~dp0main.py"
set "TUNNEL_SCRIPT=%~dp0start_tunnel.py"
set "ADMIN_SCRIPT=%~dp0manage_users.py"
set "REQ_FILE=%~dp0requirements.txt"

:: Python Calistirici Secimi (Once .venv, sonra global Python)
if exist "!VENV_PYTHON!" (
    set "PYTHON_EXE=!VENV_PYTHON!"
) else (
    where python >nul 2>nul
    if "!ERRORLEVEL!"=="0" (
        set "PYTHON_EXE=python"
    ) else (
        color 4F
        cls
        echo.
        echo  =============================================================
        echo   [!] HATA: Python bulunamadi!
        echo  =============================================================
        echo   Lutfen sisteminize Python yukleyin veya .venv olusturun:
        echo   1. python -m venv .venv
        echo   2. .venv\Scripts\pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

:MENU
cls
color 0B
echo.
echo  ===================================================================
echo    N I K O   A I   -   S I S T E M   K O N T R O L   M E R K E Z I
echo  ===================================================================
echo.
echo    [1] [+] TAM BASLAT (Backend + Cloudflare Tuneli)
echo    [2] [*] SUPABASE VERITABANI ISLEMLERI (Yonetim Menusu)
echo    [3] [+] KULLANICI YONETICISI (manage_users.py)
echo    [4] [+] BAGIMLILIKLARI GUNCELLE (pip install)
echo    [5] [*] TEK TEK CALISTIRMA SECENEKLERI (Alt Menu)
echo    [6] [-] CIKIS
echo.
echo  ===================================================================
echo   [Python]: !PYTHON_EXE!
echo  ===================================================================
set /p "choice= Seciminiz (1-6): "

if "%choice%"=="1" goto START_SOFT
if "%choice%"=="2" goto SUPABASE_MENU
if "%choice%"=="3" goto START_ADMIN
if "%choice%"=="4" goto UPDATE_DEPS
if "%choice%"=="5" goto INDIVIDUAL_MENU
if "%choice%"=="6" exit
goto MENU


:SUPABASE_MENU
cls
color 0A
echo.
echo  ===================================================================
echo    N I K O   A I   -   SUPABASE VERITABANI YONETIMI
echo  ===================================================================
echo.
echo    [1] [+] Supabase Baglantisini Test Et
echo    [2] [*] Yerel JSON Verilerini Supabase'e Goc Ettir (Migration)
echo    [3] [?] Veritabani Istatistiklerini Goruntule
echo    [4] [-] ANA MENUYE DON
echo.
echo  ===================================================================
set /p "dbchoice= Seciminiz (1-4): "

if "%dbchoice%"=="1" goto TEST_SUPABASE
if "%dbchoice%"=="2" goto RUN_MIGRATION
if "%dbchoice%"=="3" goto DB_STATS
if "%dbchoice%"=="4" goto MENU
goto SUPABASE_MENU


:TEST_SUPABASE
cls
echo.
echo  [*] Supabase baglantisi test ediliyor...
echo.
"!PYTHON_EXE!" -c "from database import get_supabase; db = get_supabase(); print('  [+] Supabase baglantisi basarili!') if db else print('  [-] Supabase baglantisi kurulamadi!')" 2>nul
if !ERRORLEVEL! NEQ 0 (
    echo  [-] HATA: Supabase modulu yuklu degil veya .env dosyasinda eksik var.
)
echo.
pause
goto SUPABASE_MENU


:RUN_MIGRATION
cls
echo.
echo  [*] Yerel JSON dosyalari Supabase'e aktariliyor...
echo  [!] Bu islem mevcut users.json ve history verilerini veritabanina gonderir.
echo.
"!PYTHON_EXE!" -c "from database import migrate_json_to_supabase; migrate_json_to_supabase()"
echo.
pause
goto SUPABASE_MENU


:DB_STATS
cls
echo.
echo  [*] Veritabani istatistikleri yukleniyor...
echo.
"!PYTHON_EXE!" -c "from database import get_supabase; db = get_supabase(); u = len(db.table('users').select('username').execute().data); s = len(db.table('chat_sessions').select('id').execute().data); m = len(db.table('chat_messages').select('id').execute().data); v = len(db.table('email_verifications').select('email').execute().data); print(f'  - Kayitli Kullanici Sayisi: {u}'); print(f'  - Toplam Sohbet Oturumu   : {s}'); print(f'  - Toplam Sohbet Mesaji    : {m}'); print(f'  - Bekleyen E-posta Dogr.  : {v}')" 2>nul
if !ERRORLEVEL! NEQ 0 (
    echo  [-] HATA: Istatistikler alinamadi. Baglanti detaylarini veya tablo semasini kontrol edin.
)
echo.
pause
goto SUPABASE_MENU


:INDIVIDUAL_MENU
cls
color 0E
echo.
echo  ===================================================================
echo    N I K O   A I   -   TEK TEK CALISTIRMA SECENEKLERI
echo  ===================================================================
echo.
echo    [1] [+] Sadece Backend Servisini Baslat (Port: 8001)
echo    [2] [*] Sadece Cloudflare Tunelini Baslat
echo    [3] [-] ANA MENUYE DON
echo.
echo  ===================================================================
set /p "subchoice= Seciminiz (1-3): "

if "%subchoice%"=="1" goto START_BACKEND_ONLY
if "%subchoice%"=="2" goto START_TUNNEL_ONLY
if "%subchoice%"=="3" goto MENU
goto INDIVIDUAL_MENU


:START_SOFT
cls
echo.
echo  ===================================================================
echo        NIKO AI SISTEMI AYAGA KALDIRILIYOR
echo  ===================================================================
echo.

:: 1. Backend Baslat (Yeni Pencerede)
echo  [+] Backend Servisi baslatiliyor (Port: 8001)...
start "Niko - Backend Server" cmd /k ""!PYTHON_EXE!" "!MAIN_SCRIPT!""

echo.
echo  [+] Tunel Servisi baslatiliyor...
echo  [i] Backend ve Tunel aktif. Bu pencere tuneli ayakta tutar.
echo  [!] Kapatmak veya ana menuye donmek icin CTRL+C yapabilirsiniz.
echo.

:: 2. Tünel Baslat (Bu Pencerede - Blocking)
"!PYTHON_EXE!" "!TUNNEL_SCRIPT!"

echo.
echo  [!] Tunel scripti durdu.
pause
goto MENU


:START_BACKEND_ONLY
cls
echo.
echo  [+] Backend Servisi baslatiliyor (Port: 8001)...
start "Niko - Backend Server" cmd /k ""!PYTHON_EXE!" "!MAIN_SCRIPT!""
echo  [i] Backend servisi yeni pencerede acildi.
echo.
pause
goto INDIVIDUAL_MENU


:START_TUNNEL_ONLY
cls
echo.
echo  [+] Tunel Servisi baslatiliyor...
echo  [i] Tunel bu pencerede calisacak.
"!PYTHON_EXE!" "!TUNNEL_SCRIPT!"
echo.
echo  [!] Tunel scripti durdu.
pause
goto INDIVIDUAL_MENU


:START_ADMIN
cls
echo.
echo  [+] Admin Paneli aciliyor...
start "Niko - User Manager" cmd /k ""!PYTHON_EXE!" "!ADMIN_SCRIPT!""
goto MENU


:UPDATE_DEPS
cls
echo.
echo  [+] Bagimliliklar requirements.txt dosyasindan yukleniyor...
"!PYTHON_EXE!" -m pip install -r "!REQ_FILE!"
echo.
echo  [+] Yukleme tamamlandi.
echo.
pause
goto MENU
