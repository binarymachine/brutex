#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brute-force PUR d'un .docx chiffré à l'ouverture : essaie TOUTES les
combinaisons possibles sur un jeu de caractères choisi, des plus courtes
aux plus longues. Ne modifie JAMAIS le document (lecture seule).

Lancement :
    python3 Docx_brute_force_pur.py            # depuis le debut
    python3 Docx_brute_force_pur.py 1500000    # REPRISE (index global affiche)

Reprise :
    L'argument optionnel est un NOMBRE : l'index GLOBAL affiche dans la
    progression ("12,345/80,000,000"). Ici les candidats d'une longueur ne
    forment pas un nombre (alphabet quelconque), donc on compte une position
    cumulee sur toutes les longueurs. En cas d'arret, relancer avec le dernier
    nombre affiche repart juste apres : les longueurs deja entierement
    parcourues sont ignorees, et la longueur en cours redemarre a sa position.

LIS D'ABORD ÇA. La force brute pure explose très vite. À ~8 essais/seconde,
pour des mots de passe de longueur L sur un alphabet de
N caractères, il faut tester N^L combinaisons :

  minuscules seules (N=26)      5 lettres  ~ 11 M   -> ~16 jours
  minusc.+chiffres (N=36)       5          ~ 60 M   -> ~3 mois
  tout activé      (N~=95)      4          ~ 81 M   -> ~4 mois
                               6          ~ 7e11  -> des milliers d'années

Autrement dit : au-delà de 4-5 caractères, ce script ne FINIRA jamais en
pratique. Il est surtout utile pour un mot de passe très court, ou pour
balayer à fond une petite longueur. 
"""

import io, sys, time, itertools, string
from multiprocessing import Pool, cpu_count

try:
    import msoffcrypto
except ImportError:
    sys.exit("Il manque la librairie. Lance d'abord :\n"
             "    python3 -m pip install --user --only-binary :all: msoffcrypto-tool")

# =====================================================================
# ==========   À MODIFIER : ne touche que cette zone   ================
# =====================================================================

# Le fichier à ouvrir (la COPIE par défaut, pour protéger l'original)
TARGET = "test-pur.docx"

# Jeux de caractères à utiliser (True = inclus)
MINUSCULES = True      # a-z
MAJUSCULES = False     # A-Z
CHIFFRES   = False      # 0-9
SPECIAUX   = False     # ! @ # $ % & * ...

# Jeu de caractères personnalisé : si tu mets quelque chose ici (ex. "abc123"),
# il REMPLACE les cases ci-dessus. Laisse "" pour utiliser les cases.
PERSO = ""

# Longueurs à essayer (inclus). Commence petit !
LONGUEUR_MIN = 1
LONGUEUR_MAX = 4

# =====================================================================
# ==========   Au-dessous, pas besoin de toucher   ====================
# =====================================================================

SPECIAUX_SET = "!@#$%&*()-_=+.?"

def alphabet():
    if PERSO:
        return "".join(dict.fromkeys(PERSO))   # dédoublonne en gardant l'ordre
    a = ""
    if MINUSCULES: a += string.ascii_lowercase
    if MAJUSCULES: a += string.ascii_uppercase
    if CHIFFRES:   a += string.digits
    if SPECIAUX:   a += SPECIAUX_SET
    return a

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
    alpha = alphabet()
    if not alpha:
        sys.exit("Aucun caractère sélectionné : active au moins un jeu.")
    nproc = max(1, cpu_count())
    N = len(alpha)

    # --- parametre de reprise optionnel : index GLOBAL affiche ---
    reprise = 0
    if len(sys.argv) > 1:
        try:
            reprise = int(sys.argv[1])
        except ValueError:
            sys.exit(f"Argument de reprise invalide : {sys.argv[1]!r} (attendu un nombre).")
        if reprise < 0:
            sys.exit("L'argument de reprise doit etre un nombre positif.")

    print(f"Fichier   : {TARGET}")
    print(f"Coeurs    : {nproc}")
    print(f"Alphabet  : {N} caractères -> {alpha}")
    total_global = sum(N ** L for L in range(LONGUEUR_MIN, LONGUEUR_MAX + 1))
    print(f"Total à essayer : {total_global:,} combinaisons")
    print(f"(estimation à 8/s : ~{total_global/8/86400:.1f} jours au pire)")
    if reprise:
        print(f"REPRISE : a partir de l'index global {reprise:,}")
    print()

    deja = 0                 # candidats dans les longueurs deja terminees (global)
    reste_skip = reprise     # combien de candidats il reste a sauter
    with Pool(nproc) as p:
        for L in range(LONGUEUR_MIN, LONGUEUR_MAX + 1):
            total = N ** L
            if reste_skip >= total:          # longueur entierement avant la reprise
                print(f"--- longueur {L} : {total:,} -> ignoré (reprise) ---")
                reste_skip -= total
                deja += total
                continue
            offset = reste_skip              # offset local dans cette longueur
            reste_skip = 0
            entete = f"--- longueur {L} : {total:,} combinaisons"
            if offset:
                entete += f" (reprise a l'index global {deja + offset:,}, offset local {offset:,})"
            print(entete + " ---")
            cands = ("".join(c) for c in itertools.product(alpha, repeat=L))
            if offset:
                cands = itertools.islice(cands, offset, None)
            t0 = time.time()
            trouve = False
            for k, res in enumerate(p.imap_unordered(test, cands, chunksize=64), 1):
                if res:
                    ecrire_resultat(res)
                    trouve = True
                    break
                position = deja + offset + k     # index GLOBAL absolu = argument de reprise
                if position % 1000 == 0:
                    dt = time.time() - t0
                    reste = (total_global - position) / (k / dt) if dt > 0 else 0
                    print(f"  {position:,}/{total_global:,}  {k/dt:.1f}/s  reste ~{reste/3600:.1f} h")
            if trouve:
                return
            deja += total
            print(f"  (rien en longueur {L})")

    print("\nRien trouvé dans la plage demandée.")

if __name__ == "__main__":
    main()
