#!/usr/bin/env bash
#
# demarrer.sh - equivalent Linux (Debian/Ubuntu) de DEMARRER.bat
#
# Retrouve le mot de passe du document chiffre a partir de son empreinte
# (example/hash_test.txt), avec hashcat, en deux passages par liste de mots.
#
# Usage :
#     chmod +x demarrer.sh      # une seule fois
#     ./demarrer.sh
#
set -u

# --- se placer dans le dossier du script ---
cd "$(dirname "$0")" || exit 1

HASH="example/hash_test.txt"
WORDS="mots_theme.txt"
MODE=9600          # Office 2013 (AES-256 / SHA-512 / 100000 iterations)

echo "============================================================"
echo "  Brutex (Linux / hashcat)"
echo "============================================================"
echo

# --- 1. verifier les fichiers ---
if [ ! -f "$HASH" ]; then
  echo "[X] $HASH introuvable dans ce dossier. Garde tous les fichiers ensemble."
  exit 1
fi
if [ ! -f "$WORDS" ]; then
  echo "[X] $WORDS introuvable dans ce dossier."
  exit 1
fi

# --- 2. verifier / installer hashcat ---
if ! command -v hashcat >/dev/null 2>&1; then
  echo "[*] hashcat n'est pas installe."
  echo "    Sur Debian/Ubuntu, installe-le avec :"
  echo
  echo "        sudo apt update && sudo apt install -y hashcat"
  echo
  read -r -p "    Tenter l'installation automatique maintenant ? [o/N] " rep
  case "$rep" in
    o|O|y|Y)
      sudo apt update && sudo apt install -y hashcat || {
        echo "[X] L'installation a echoue. Installe hashcat a la main puis relance."
        exit 1
      }
      ;;
    *)
      echo "    Installe hashcat puis relance ./demarrer.sh"
      exit 1
      ;;
  esac
fi

# --- 3. localiser le dossier des regles ---
RULES=""
for d in /usr/share/hashcat/rules ./rules ./hashcat-*/rules; do
  if [ -f "$d/best64.rule" ]; then RULES="$d"; break; fi
done
if [ -z "$RULES" ]; then
  echo "[X] Dossier de regles hashcat introuvable (best64.rule)."
  echo "    Avec le paquet apt, il est normalement dans /usr/share/hashcat/rules."
  exit 1
fi
echo "[*] Regles trouvees dans : $RULES"
echo

# --- 4. materiel detecte ---
echo "[*] Peripheriques detectes par hashcat :"
hashcat -I 2>/dev/null || true
echo
echo "    (Pour utiliser un GPU NVIDIA : pilote 'nvidia-driver' + backend CUDA"
echo "     ou OpenCL installes. Sans GPU, hashcat tourne sur le CPU, nettement"
echo "     plus lentement.)"
echo
read -r -p "    Entree pour demarrer la recherche (Ctrl+C pour annuler)... " _

# --- 5. passage 1 : variantes courantes ---
echo
echo "============================================================"
echo " PASSAGE 1 : mots du theme + variantes courantes (best64)"
echo "============================================================"
hashcat -m "$MODE" "$HASH" "$WORDS" -r "$RULES/best64.rule"

# --- 6. passage 2 : grosses variantes (si pas encore trouve) ---
echo
echo "============================================================"
echo " PASSAGE 2 : mots du theme + grosses variantes (rockyou-30000)"
echo "============================================================"
if [ -f "$RULES/rockyou-30000.rule" ]; then
  hashcat -m "$MODE" "$HASH" "$WORDS" -r "$RULES/rockyou-30000.rule"
else
  echo "[i] rockyou-30000.rule absent dans $RULES, passage 2 ignore."
fi

# --- 7. resultat ---
echo
echo "============================================================"
echo " RESULTAT"
echo "============================================================"
hashcat -m "$MODE" "$HASH" --show
echo
echo "------------------------------------------------------------"
echo " Un mot de passe trouve s'affiche apres le dernier ':' de la"
echo " ligne ci-dessus. Note-le pour dechiffrer le document."
echo " Tu peux relancer ./demarrer.sh : hashcat reprend ou il en"
echo " etait (fichier hashcat.potfile)."
echo "------------------------------------------------------------"
