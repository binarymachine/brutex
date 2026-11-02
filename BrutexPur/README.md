# BrutexPur — brute-force sur alphabet

Essaie **toutes les combinaisons** possibles sur un jeu de caractères choisi
(minuscules, majuscules, chiffres, spéciaux, ou alphabet personnalisé), des plus
courtes aux plus longues. En lecture seule : le document d'origine n'est jamais
modifié.

> Fonctionne avec **Word (.docx), Excel (.xlsx) et PowerPoint (.pptx)** chiffrés
> à l'ouverture (chiffrement « agile » Office 2010/2013+). Change simplement la
> valeur `TARGET` pour pointer sur ton fichier.

## Prérequis

```bash
python3 -m pip install --user --only-binary :all: msoffcrypto-tool
```

## Utilisation

```bash
python3 Docx_brute_force_pur.py             # depuis le début
python3 Docx_brute_force_pur.py 1500000     # REPRISE (index global affiché)
```

À régler en haut du script : `TARGET`, les jeux de caractères
(`MINUSCULES`, `MAJUSCULES`, `CHIFFRES`, `SPECIAUX`, ou `PERSO`),
`LONGUEUR_MIN`, `LONGUEUR_MAX`.

## Reprise

L'argument est un **nombre** : l'**index global** affiché dans la progression
(`12,345/80,000,000`). Ici les candidats d'une longueur ne forment pas un nombre
(alphabet quelconque), donc on compte une position cumulée sur toutes les
longueurs. En cas d'arrêt, relancer avec le dernier nombre affiché repart juste
après : les longueurs déjà entièrement parcourues sont ignorées, et la longueur
en cours redémarre à sa position.

## Résultat

Mot de passe affiché, écrit dans `FOUND.txt`, et copie déchiffrée dans
`<fichier>_DECHIFFRE.docx`.

⚠️ La force brute pure explose vite : réaliste surtout jusqu'à 4-5 caractères.
