#!/usr/bin/env bash
#
# force_brute.sh - equivalent Linux (Debian/Ubuntu) de FORCE_BRUTE.bat
#
# Force brute par MASQUE. A reserver aux mots de passe courts :
# chaque caractere en plus multiplie fortement le temps.
# Lance ./demarrer.sh au moins une fois avant (pour installer hashcat).
#
# Symboles de masque :
#     ?l = minuscule   ?u = majuscule   ?d = chiffre   ?s = special
# Exemples :
#     ?d?d?d?d          = 4 chiffres
#     ?l?l?l?l?l?l       = 6 minuscules
#     ?u?l?l?l?l?d       = Majuscule + 4 minuscules + 1 chiffre
#
# Modifie la ligne MASQUE ci-dessous, puis :  ./force_brute.sh
# (ou passe le masque en argument :  ./force_brute.sh '?d?d?d?d')
#
set -u

cd "$(dirname "$0")" || exit 1

MASQUE="?d?d?d?d?d?d"
[ "$#" -ge 1 ] && MASQUE="$1"   # un masque passe en argument a la priorite

HASH="example/hash_test.txt"
MODE=9600

if ! command -v hashcat >/dev/null 2>&1; then
  echo "[X] hashcat n'est pas installe. Lance d'abord ./demarrer.sh"
  exit 1
fi
if [ ! -f "$HASH" ]; then
  echo "[X] $HASH introuvable dans ce dossier."
  exit 1
fi

echo "============================================================"
echo " FORCE BRUTE - masque : $MASQUE"
echo "============================================================"
echo " hashcat va d'abord estimer la duree. Si elle est enorme,"
echo " Ctrl+C et raccourcis le masque."
echo
read -r -p " Entree pour demarrer (Ctrl+C pour annuler)... " _

hashcat -m "$MODE" -a 3 "$HASH" "$MASQUE"

echo
echo "----- RESULTAT -----"
hashcat -m "$MODE" "$HASH" --show
