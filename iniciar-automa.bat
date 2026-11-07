@echo off
setlocal EnableExtensions
cd /d "%~dp0"

rem ============================================================
rem  AUTOMA - inicializacao unificada (coloque este arquivo na raiz do repo)
rem
rem  iniciar-automa.bat            prepara tudo e abre o app
rem                                (o Electron sobe o backend sozinho)
rem  iniciar-automa.bat check      prepara tudo e testa backend + FFmpeg,
rem                                sem abrir o app
rem  iniciar-automa.bat backend    roda so o backend neste console
rem                                (mostra os erros na tela)
rem ============================================================

set "MODE=%~1"
if "%MODE%"=="" set "MODE=app"
set "VENV_PY=%~dp0backend\.venv\Scripts\python.exe"

echo ==========================================
echo  AUTOMA - modo: %MODE%
echo ==========================================

rem ---------- Python ----------
where python >nul 2>&1
if errorlevel 1 (
  echo [ERRO] Python nao encontrado no PATH.
  echo        Instale o Python 3.11 ou superior e marque "Add python.exe to PATH".
  exit /b 1
)

rem ---------- venv do backend ----------
rem O Electron em modo dev executa backend\.venv\Scripts\python.exe main.py
if exist "%VENV_PY%" goto venv_ok
echo [1/4] Criando ambiente virtual em backend\.venv ...
python -m venv "backend\.venv"
if errorlevel 1 (
  echo [ERRO] Nao consegui criar o ambiente virtual.
  exit /b 1
)
goto venv_done
:venv_ok
echo [1/4] Ambiente virtual ja existe.
:venv_done

rem ---------- dependencias do backend ----------
echo [2/4] Instalando dependencias do backend (pode demorar na primeira vez)...
"%VENV_PY%" -m pip install --disable-pip-version-check -q -r "backend\requirements.txt"
if errorlevel 1 (
  echo [ERRO] Falha no pip install. Veja a mensagem acima.
  exit /b 1
)

rem ---------- FFmpeg ----------
rem O backend NAO usa o FFmpeg do PATH: usa o binario do pacote imageio-ffmpeg.
echo [3/4] Verificando o FFmpeg embutido (imageio-ffmpeg)...
"%VENV_PY%" -c "import imageio_ffmpeg,os,sys; p=imageio_ffmpeg.get_ffmpeg_exe(); print('      ' + p); sys.exit(0 if os.path.exists(p) else 1)"
if errorlevel 1 (
  echo [ERRO] Binario do FFmpeg nao encontrado. Rode: backend\.venv\Scripts\python.exe -m pip install --force-reinstall imageio-ffmpeg
  exit /b 1
)

if /i "%MODE%"=="check" goto run_check
if /i "%MODE%"=="backend" goto run_backend
goto run_app

:run_check
echo [4/4] Testando se o backend importa sem erros...
pushd backend
"%VENV_PY%" -c "import main; print('      backend importado com sucesso')"
set "RC=%ERRORLEVEL%"
popd
if not "%RC%"=="0" (
  echo [ERRO] O backend nao importou. Leia o erro acima.
  exit /b 1
)
echo.
echo Tudo certo. Rode "iniciar-automa.bat" para abrir o app.
exit /b 0

:run_backend
echo [4/4] Subindo o backend em http://127.0.0.1:8420  (Ctrl+C para parar)
echo       Teste no navegador: http://127.0.0.1:8420/health
pushd backend
"%VENV_PY%" main.py
set "RC=%ERRORLEVEL%"
popd
exit /b %RC%

:run_app
rem Se ja existe um backend na porta 8420, o Electron abriria um segundo e ele falharia.
netstat -ano | findstr /R /C:":8420 .*LISTENING" >nul 2>&1
if not errorlevel 1 (
  echo.
  echo [AVISO] A porta 8420 ja esta em uso. Provavelmente ha outro backend do AUTOMA rodando.
  echo         Feche-o antes de continuar, senao o app vai conversar com o backend antigo.
  pause
)

where npm >nul 2>&1
if errorlevel 1 (
  echo [ERRO] npm nao encontrado. Instale o Node.js 20 ou superior.
  exit /b 1
)

if exist "frontend\node_modules" goto fe_ok
echo [4/4] Instalando dependencias do frontend (primeira vez)...
pushd frontend
call npm install
set "RC=%ERRORLEVEL%"
popd
if not "%RC%"=="0" (
  echo [ERRO] npm install falhou.
  exit /b 1
)
goto fe_done
:fe_ok
echo [4/4] Dependencias do frontend ja instaladas.
:fe_done

echo.
echo Abrindo o AUTOMA. O Electron sobe o backend sozinho.
pushd frontend
call npm run dev
popd
exit /b 0
