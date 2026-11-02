#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Brute-force "par thème" d'un .docx chiffré à l'ouverture.
Teste une liste de mots + variantes (casse, chiffres, années, caractères
spéciaux, leet) contre le fichier. Ne modifie JAMAIS le document : il est
seulement lu. Si un mot de passe marche, il est écrit dans FOUND.txt et une
copie déchiffrée est enregistrée à côté.

Lancement :
    python3 Docx_brute_force_word.py        # depuis le debut
    python3 Docx_brute_force_word.py 1200   # REPRISE (index affiche dans la progression)

Reprise :
    L'argument optionnel est un NOMBRE : l'index affiche dans la progression
    ("1,200/5,000"). En cas d'arret, relancer avec le dernier nombre affiche
    saute les candidats deja testes et repart juste apres. L'ordre des
    candidats est deterministe, donc l'index reste valable d'une execution a
    l'autre (a condition de ne pas modifier MOTS ni les options de variantes).

(voir les instructions en bas si Python dit qu'il manque "msoffcrypto")



- MOTS = [...] : ta liste de mots pour le thème. Un par ligne, entre guillemets, séparés par des virgules. Pas besoin de mettre les majuscules, le script génère aristote, Aristote, ARISTOTE tout seul. Ajoute un prénom, une année, un chiffre fétiche, etc.
- AJOUTER_CHIFFRES : ajoute 0 à 99 au bout (aristote7…).
- AJOUTER_ANNEES : ajoute 1950 à 2026 au bout.
- AJOUTER_SPECIAUX : ajoute !, ?, 123, etc.
- LEET : remplace a→4 e→3 o→0… Laisse sur False au début (ça multiplie énormément le nombre d'essais) ; passe-le à True seulement si le reste n'a rien donné.


- Il affiche la progression et une estimation du temps restant.
- Si ça marche : il écrit le mot de passe dans FOUND.txt et crée test-word_DECHIFFRE.docx à côté, sans toucher aux fichiers d'origine.
"""

import io, sys, time
from multiprocessing import Pool, cpu_count

try:
    import msoffcrypto
except ImportError:
    sys.exit("Il manque la librairie. Lance d'abord :\n"
             "    python3 -m pip install --user --only-binary :all: msoffcrypto-tool")

# =====================================================================
# ==========   À MODIFIER : ne touche que cette zone   ================
# =====================================================================

# 1) Le fichier à ouvrir (la COPIE par défaut, pour protéger l'original)
TARGET = "test-word.docx"

# 2) TON THÈME : mets ici tous les mots qui te viennent (un par ligne,
#    entre guillemets, séparés par des virgules). Minuscules suffisent,
#    le script génère tout seul les majuscules.
MOTS = [
    "bo", "steve", "bka0",
    # ajoute les tiens ici, par ex. :
    # "prenom", "unmot", "annee",
]

# 3) Options de variantes (True = activé, False = désactivé)
AJOUTER_CHIFFRES   = True    # ajoute 0..99 à la fin (aristote7, aristote42...)
AJOUTER_ANNEES     = True    # ajoute 1950..2026 à la fin
AJOUTER_SPECIAUX   = False    # ajoute ! ? . @ # 123 1234 etc. à la fin
LEET               = False   # remplace a->4 e->3 i->1 o->0 s->5 t->7
                             #   (démultiplie le nombre d'essais : à activer
                             #    seulement si le reste n'a rien donné)

# =====================================================================
# ==========   Au-dessous, pas besoin de toucher   ====================
# =====================================================================

def case_variants(w):
    # ordre fixe + dedoublonnage deterministe (indispensable pour la reprise)
    return list(dict.fromkeys([w, w.lower(), w.upper(), w.capitalize()]))

def leet_variants(w):
    repl = [("a", "4"), ("e", "3"), ("i", "1"), ("o", "0"),
            ("s", "5"), ("t", "7"), ("a", "@")]
    out = [w]
    for ch, d in repl:                          # une substitution à la fois
        if ch in w.lower():
            out.append(w.lower().replace(ch, d))
    full = w.lower()                            # + leet complet
    for ch, d in repl:
        full = full.replace(ch, d)
    out.append(full)
    return list(dict.fromkeys(out))             # dedoublonne en gardant l'ordre

def build_suffixes():
    s = [""]
    if AJOUTER_CHIFFRES:
        s += [str(n) for n in range(0, 100)]
    if AJOUTER_ANNEES:
        s += [str(y) for y in range(1950, 2027)]
    if AJOUTER_SPECIAUX:
        s += ["!", "?", ".", "@", "#", "*", "_", "-",
              "1!", "!!", "123", "1234", "12", "12345", "123456",
              "01", "00", "!1", "321"]
    return s

def generate():
    suffixes = build_suffixes()
    seen = set()
    for mot in MOTS:
        cores = []
        for c in case_variants(mot):
            cores += (leet_variants(c) if LEET else [c])
        cores = list(dict.fromkeys(cores))     # dedoublonne en gardant l'ordre
        for core in cores:
            for suf in suffixes:
                cand = core + suf
                if cand and cand not in seen:
                    seen.add(cand)
                    yield cand

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

def main():
    # --- parametre de reprise optionnel : index affiche dans la progression ---
    reprise = 0
    if len(sys.argv) > 1:
        try:
            reprise = int(sys.argv[1])
        except ValueError:
            sys.exit(f"Argument de reprise invalide : {sys.argv[1]!r} (attendu un nombre).")
        if reprise < 0:
            sys.exit("L'argument de reprise doit etre un nombre positif.")

    cands = list(generate())
    total = len(cands)
    nproc = max(1, cpu_count())
    print(f"Fichier   : {TARGET}")
    print(f"Candidats : {total}")
    print(f"Coeurs    : {nproc}")
    if reprise:
        print(f"REPRISE   : a partir de l'index {reprise} (candidats 1..{reprise} ignores)")
    print()

    if reprise >= total:
        print(f"Index de reprise {reprise} >= nombre de candidats ({total}) : rien a tester.")
        return

    a_tester = cands[reprise:]          # saute les candidats deja essayes

    t0 = time.time()
    found = None
    with Pool(nproc) as p:
        for k, res in enumerate(p.imap_unordered(test, a_tester, chunksize=8), 1):
            if res:
                found = res
                p.terminate()
                break
            position = reprise + k       # index absolu = argument de reprise
            if position % 200 == 0:
                dt = time.time() - t0
                reste = (total - position) / (k / dt) if dt > 0 else 0
                print(f"{position}/{total}  {k/dt:.1f}/s  reste ~{reste/60:.0f} min")

    if found:
        print(f"\n*** TROUVE : {found!r} ***")
        with open("FOUND.txt", "w") as f:
            f.write(found)
        # écrit une copie déchiffrée à côté, sans toucher l'original
        sortie = TARGET.rsplit(".", 1)[0] + "_DECHIFFRE.docx"
        with open(TARGET, "rb") as fin, open(sortie, "wb") as fout:
            o = msoffcrypto.OfficeFile(fin)
            o.load_key(password=found)
            o.decrypt(fout)
        print(f"Document déchiffré écrit dans :\n    {sortie}")
        print("Mot de passe aussi noté dans FOUND.txt (dossier courant).")
    else:
        print(f"\nRien trouvé sur {total} candidats "
              f"({(time.time()-t0)/60:.0f} min).")
        print("Idées : ajoute des mots dans MOTS, ou mets LEET = True.")

if __name__ == "__main__":
    main()
