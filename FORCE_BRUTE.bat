@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
chcp 65001 >nul

rem ==========================================================
rem  Force brute par MASQUE (lance DEMARRER.bat au moins une
rem  fois avant, pour installer hashcat).
rem
rem  MODIFIE la ligne MASQUE ci-dessous :
rem    ?l = minuscule   ?u = majuscule   ?d = chiffre   ?s = special
rem  Exemples :
rem    ?d?d?d?d            = 4 chiffres
rem    ?l?l?l?l?l?l        = 6 minuscules
rem    ?u?l?l?l?l?d        = Majuscule + 4 minuscules + 1 chiffre
rem  Chaque symbole en plus multiplie fortement le temps.
rem ==========================================================

set "MASQUE=?d?d?d?d?d?d"

set "HC=hashcat-6.2.6"

if not exist "%HC%\hashcat.exe" (
  echo [X] hashcat n'est pas installe. Lance d'abord DEMARRER.bat.
  pause
  goto :eof
)

echo ============================================================
echo  FORCE BRUTE - masque : %MASQUE%
echo ============================================================
echo  hashcat va d'abord estimer la duree. Si elle est enorme,
echo  ferme la fenetre et raccourcis le masque.
echo.
pause

pushd "%HC%"
hashcat.exe -m 9600 -a 3 "..\example\hash_test.txt" %MASQUE%
echo.
echo ----- RESULTAT -----
hashcat.exe -m 9600 "..\example\hash_test.txt" --show
popd

echo.
pause
