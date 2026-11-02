# BrutexNumber — brute-force numérique

Essaie tous les mots de passe composés **uniquement de chiffres**, des plus
courts aux plus longs, jusqu'à ouvrir le document chiffré. En lecture seule :
le fichier d'origine n'est jamais modifié.

> Fonctionne avec **Word (.docx), Excel (.xlsx) et PowerPoint (.pptx)** chiffrés
> à l'ouverture (chiffrement « agile » Office 2010/2013+). Change simplement la
> valeur `TARGET` pour pointer sur ton fichier.

## Prérequis

```bash
python3 -m pip install --user --only-binary :all: msoffcrypto-tool
```

## Utilisation

```bash
python3 Docx_brute_force_number.py            # depuis le début
python3 Docx_brute_force_number.py 124000     # REPRISE
```

À régler en haut du script : `TARGET`, `LONGUEUR_MIN`, `LONGUEUR_MAX`.

## Reprise

L'argument optionnel est un **nombre**. Son **nombre de chiffres** indique la
longueur où l'on reprend (`4000` → 4 chiffres, `124000` → 6 chiffres) ; les
longueurs plus courtes sont considérées comme déjà testées, et la longueur de
reprise redémarre à ce numéro. Le nombre affiché pendant la progression
(`124000/1000000`) est exactement celui à retaper pour reprendre après un arrêt.

## Résultat

Mot de passe affiché à l'écran, écrit dans `FOUND.txt`, et copie déchiffrée dans
`<fichier>_DECHIFFRE.docx` (à côté).

⚠️ Chaque chiffre en plus multiplie le temps par 10 : réaliste surtout pour des
codes courts.
