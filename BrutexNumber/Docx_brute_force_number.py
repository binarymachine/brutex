#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brute-force NUMÉRIQUE d'un .docx chiffré à l'ouverture.
Essaie tous les mots de passe composés uniquement de chiffres, des plus
courts aux plus longs. Ne modifie JAMAIS le document (lecture seule).

Lancement :
    python3 Docx_brute_force_number.py            # depuis le debut
    python3 Docx_brute_force_number.py 124000     # REPRISE

Reprise :
    L'argument optionnel est un NOMBRE. Son nombre de chiffres indique la
    longueur de code ou l'on reprend (ex. 124000 -> 6 chiffres, 4000 -> 4
    chiffres), et les longueurs plus courtes sont considerees comme deja
    testees (sans succes). La longueur de reprise redemarre a ce numero.
    Exemple : l'affichage "124000/1000000" (6 chiffres) ; en cas d'arret,
    relancer avec l'argument 124000 repart au debut de cette iteration.

ATTENTION au temps : chaque chiffre en plus multiplie le travail par 10.
À ~12 essais/seconde :
    4 chiffres  (10 000)        ~ 15 min
    5 chiffres  (100 000)       ~ 2 h 30
    6 chiffres  (1 000 000)     ~ 1 jour
    7 chiffres  (10 000 000)    ~ 10 jours
    8 chiffres et plus          -> irréaliste
"""

import io, sys, time, itertools
from multiprocessing import Pool, cpu_count

try:
    import msoffcrypto
except ImportError:
    sys.exit("Il manque la librairie. Lance d'abord :\n"
             "    python3 -m pip install --user --only-binary :all: msoffcrypto-tool")

# =====================================================================
# ==========   À MODIFIER : ne touche que cette zone   ================
# =====================================================================

# Le fichier à ouvrir
TARGET = "test-number.docx"

# Longueurs de code à essayer (inclus). Commence petit !
LONGUEUR_MIN = 1
LONGUEUR_MAX = 7

# =====================================================================
# ==========   Au-dessous, pas besoin de toucher   ====================
# =====================================================================

def test(pw):
    try:
        with open(TARGET, "rb") as f:
            o = msoffcrypto.OfficeFile(f)
            o.load_key(password=pw)
            io_out = io.BytesIO()
            o.decrypt(io_out)
        return pw
    except Exception:
        return None

def ecrire_resultat(found):
    print(f"\n*** TROUVE : {found!r} ***")
    with open("FOUND.txt", "w") as f:
        f.write(found)
    sortie = TARGET.rsplit(".", 1)[0] + "_DECHIFFRE.docx"
    with open(TARGET, "rb") as fin, open(sortie, "wb") as fout:
        o = msoffcrypto.OfficeFile(fin)
        o.load_key(password=found)
        o.decrypt(fout)
    print(f"Document déchiffré écrit dans :\n    {sortie}")
    print("Mot de passe aussi noté dans FOUND.txt (dossier courant).")

def main():
    nproc = max(1, cpu_count())

    # --- parametre de reprise optionnel (un nombre) ---
    reprise = 0
    debut_len = LONGUEUR_MIN
    if len(sys.argv) > 1:
        try:
            reprise = int(sys.argv[1])
        except ValueError:
            sys.exit(f"Argument de reprise invalide : {sys.argv[1]!r} (attendu un nombre).")
        if reprise < 0:
            sys.exit("L'argument de reprise doit etre un nombre positif.")
        debut_len = max(len(str(reprise)), LONGUEUR_MIN)   # 4000 -> 4, 124000 -> 6
        if debut_len > LONGUEUR_MAX:
            sys.exit(f"Reprise a {reprise} ({debut_len} chiffres) hors plage "
                     f"(LONGUEUR_MAX = {LONGUEUR_MAX}). Augmente LONGUEUR_MAX.")

    print(f"Fichier : {TARGET}")
    print(f"Coeurs  : {nproc}")
    print(f"Essai des codes de {LONGUEUR_MIN} a {LONGUEUR_MAX} chiffres")
    if reprise:
        print(f"REPRISE : longueur {debut_len}, a partir du numero {reprise} "
              f"(longueurs < {debut_len} considerees comme deja testees)")
    print()

    with Pool(nproc) as p:
        for L in range(LONGUEUR_MIN, LONGUEUR_MAX + 1):
            total = 10 ** L
            if L < debut_len:
                print(f"--- {L} chiffres : ignore (reprise) ---")
                continue
            depart = reprise if (reprise and L == debut_len) else 0
            print(f"--- {L} chiffres : {total} combinaisons"
                  + (f" (reprise a {depart})" if depart else "") + " ---")
            cands = (str(n).zfill(L) for n in range(depart, total))
            t0 = time.time()
            trouve = False
            for k, res in enumerate(p.imap_unordered(test, cands, chunksize=64), 1):
                if res:
                    ecrire_resultat(res)
                    trouve = True
                    break
                position = depart + k            # index absolu = argument de reprise
                if position % 1000 == 0:
                    dt = time.time() - t0
                    reste = (total - position) / (k / dt) if dt > 0 else 0
                    print(f"  {position}/{total}  {k/dt:.1f}/s  reste ~{reste/60:.0f} min")
            if trouve:
                return
            print(f"  (rien en {L} chiffres)")

    print("\nRien trouve dans la plage demandee.")
    print("Augmente LONGUEUR_MAX si tu penses que le code est plus long.")

if __name__ == "__main__":
    main()
