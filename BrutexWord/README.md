# BrutexWord — brute-force par liste de mots

Teste une **liste de mots** (ton thème) et leurs variantes automatiques —
casse (`mot`, `Mot`, `MOT`), suffixes chiffres, années, caractères spéciaux, et
leet optionnel — contre le document chiffré. En lecture seule : le fichier
d'origine n'est jamais modifié.

> Fonctionne avec **Word (.docx), Excel (.xlsx) et PowerPoint (.pptx)** chiffrés
> à l'ouverture (chiffrement « agile » Office 2010/2013+). Change simplement la
> valeur `TARGET` pour pointer sur ton fichier.

## Prérequis

```bash
python3 -m pip install --user --only-binary :all: msoffcrypto-tool
```

## Utilisation

```bash
python3 Docx_brute_force_word.py            # depuis le début
python3 Docx_brute_force_word.py 1200       # REPRISE (index affiché)
```

À régler en haut du script : `TARGET`, la liste `MOTS`, et les options de
variantes (`AJOUTER_CHIFFRES`, `AJOUTER_ANNEES`, `AJOUTER_SPECIAUX`, `LEET`).
Inutile d'ajouter majuscules/chiffres à la main : le script génère les variantes.

## Reprise

L'argument est un **nombre** : l'index affiché dans la progression
(`1,200/5,000`). En cas d'arrêt, relancer avec le dernier nombre affiché saute
les candidats déjà testés et repart juste après. L'ordre des candidats est
**déterministe**, donc l'index reste valable d'une exécution à l'autre — à
condition de **ne pas modifier** `MOTS` ni les options (sinon la liste, et donc
la numérotation, change).

## Résultat

Mot de passe affiché, écrit dans `FOUND.txt`, et copie déchiffrée dans
`<fichier>_DECHIFFRE.docx`.

C'est la méthode la plus efficace quand tu as une idée du mot de passe (prénom,
mot fétiche, date…) : quelques centaines de candidats testés en minutes.
