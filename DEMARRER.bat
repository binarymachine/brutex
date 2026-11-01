@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
chcp 65001 >nul

echo ============================================================
echo   Brutex
echo   (hashcat sur GPU NVIDIA - installation automatique)
echo ============================================================
echo.

set "HC=hashcat-6.2.6"
set "HCZIP=hashcat-6.2.6.7z"

rem --- 1. Verifier le hash ---
if not exist "example\hash_test.txt" (
  echo [X] Fichier example\hash_test.txt introuvable dans ce dossier.
  echo     Garde tous les fichiers du dossier ensemble.
  goto :fin
)

rem --- 2. Telecharger 7zr.exe (sert a extraire hashcat) si absent ---
if not exist "7zr.exe" (
  echo [*] Telechargement de l'outil d'extraction 7zr.exe ...
  powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.7-zip.org/a/7zr.exe' -OutFile '7zr.exe'"
  if not exist "7zr.exe" goto :erreur_net
)

rem --- 3. Telecharger + extraire hashcat si absent ---
if not exist "%HC%\hashcat.exe" (
  if not exist "%HCZIP%" (
    echo [*] Telechargement de hashcat ... patiente, environ 60 Mo.
    powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://hashcat.net/files/hashcat-6.2.6.7z' -OutFile '%HCZIP%'"
    if not exist "%HCZIP%" goto :erreur_net
  )
  echo [*] Extraction de hashcat ...
  "7zr.exe" x -y "%HCZIP%" >nul
  if not exist "%HC%\hashcat.exe" goto :erreur_extract
)

echo.
echo [*] Verification du materiel GPU detecte par hashcat :
pushd "%HC%"
hashcat.exe -I
popd
echo.
echo     ^(Si aucun peripherique CUDA/NVIDIA n'apparait ci-dessus,
echo      mets a jour le pilote NVIDIA GeForce puis relance.^)
echo.
pause

pushd "%HC%"

echo.
echo ============================================================
echo  PASSAGE 1 : mots du theme + variantes courantes ^(best64^)
echo ============================================================
hashcat.exe -m 9600 "..\example\hash_test.txt" "..\mots_theme.txt" -r rules\best64.rule

echo.
echo ============================================================
echo  PASSAGE 2 : mots du theme + grosses variantes
echo ============================================================
hashcat.exe -m 9600 "..\example\hash_test.txt" "..\mots_theme.txt" -r rules\rockyou-30000.rule

echo.
echo ============================================================
echo  RESULTAT
echo ============================================================
hashcat.exe -m 9600 "..\example\hash_test.txt" --show
popd
goto :fin

:erreur_net
echo.
echo [X] Un telechargement a echoue. Verifie la connexion Internet
echo     puis relance DEMARRER.bat.
goto :fin

:erreur_extract
echo.
echo [X] L'extraction de hashcat a echoue. Supprime le fichier
echo     %HCZIP% et relance DEMARRER.bat.
goto :fin

:fin
echo.
echo ------------------------------------------------------------
echo  Termine. Un mot de passe trouve s'affiche a la fin de la
echo  ligne du hash ^(apres le dernier ":"^) et via --show.
echo  Note-le et renvoie-le pour dechiffrer le document.
echo ------------------------------------------------------------
pause
