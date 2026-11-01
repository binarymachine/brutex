# Brutex

Boîte à outils pour **récupérer le mot de passe oublié** d'un document Office
chiffré (`.docx`, `.xlsx`, `.pptx`) et le rouvrir.

Le principe : on n'attaque jamais le document directement. On en extrait une
**empreinte** (le *hash*), un petit fichier texte qui contient uniquement les
paramètres de chiffrement - pas le contenu. C'est cette empreinte que l'outil
hashcat teste contre des millions de mots de passe candidats, sur un GPU, sans
jamais abîmer le fichier d'origine.


---

## Contenu du dossier

| Fichier | Rôle |
|---|---|
| `docx2hash.py` | **Étape 1** - extrait l'empreinte d'un `.docx`/`.xlsx` chiffré (tourne sur Mac/Linux/Windows) |
| `example/hash_test.txt` | L'empreinte déjà extraite du document d'exemple `test.docx` |
| `mots_theme.txt` | Liste de mots-pistes (un par ligne) utilisée pour deviner le mot de passe |
| `DEMARRER.bat` | **Étape 2 (Windows)** - installe hashcat et lance la recherche par liste de mots (Windows + GPU NVIDIA) |
| `FORCE_BRUTE.bat` | **Étape 3 (Windows, secours)** - recherche par force brute selon un masque |
| `demarrer.sh` | **Étape 2 (Linux)** - équivalent de `DEMARRER.bat` pour Debian/Ubuntu |
| `force_brute.sh` | **Étape 3 (Linux, secours)** - équivalent de `FORCE_BRUTE.bat` |
| `LISEZ-MOI.txt` | Version courte de ces instructions |

Hardwares:
- Une **machine avec GPU** sert aux **étapes 2 et 3** (le calcul) : soit un
  **PC Windows** (fichiers `.bat`), soit un **PC Linux Debian/Ubuntu**
  (scripts `.sh`). Tu copies tout le dossier dessus. Idéalement avec une carte
  **NVIDIA**, mais hashcat sait aussi tourner sur CPU (bien plus lentement).

---

## Tutoriel complet de A à Z (Debian / Ubuntu)

Ce tutoriel fait tout sur **une seule machine Debian/Ubuntu**, de l'installation
des outils jusqu'à l'ouverture du document. 

Ce qui s'installe **tout seul** : hashcat (le script `demarrer.sh` propose de
l'installer au lancement). Ce qui est **à installer à la main** : Python et le
module `olefile`, nécessaires uniquement à l'étape 1 (générer l'empreinte).

### 1. Ouvrir un terminal et se placer dans le dossier

Copie le dossier `brutex` sur le PC Linux (par ex. dans ton dossier
personnel), ainsi que le document `.docx` à ouvrir. Puis :

```bash
cd ~/brutex
```

### 2. Installer Python 3 et pip

Debian/Ubuntu ont presque toujours Python 3 déjà présent. On s'en assure et on
ajoute `pip` (le gestionnaire de modules Python) :

```bash
sudo apt update
sudo apt install -y python3 python3-pip
python3 --version        # doit afficher Python 3.x
```

### 3. Installer le module `olefile`

Il sert à `docx2hash.py` pour lire le document chiffré :

```bash
pip3 install --user olefile
```

> Si Debian refuse avec un message « externally-managed-environment », utilise
> plutôt le paquet système : `sudo apt install -y python3-olefile`.

### 4. Générer l'empreinte du document (étape 1)

Remplace le chemin par celui de ton document (les guillemets sont importants
s'il contient des espaces ou des accents) :

```bash
python3 docx2hash.py "example/test.docx" > example/hash_test.txt
```

Vérifie que le fichier n'est pas vide et commence par `$office$` :

```bash
cat example/hash_test.txt
```

(Pour ce projet, `example/hash_test.txt` est déjà fourni : tu peux sauter cette étape
si tu réutilises le document d'exemple `test.docx` tel quel.)

### 5. Installer hashcat et lancer la recherche (étape 2)

```bash
chmod +x demarrer.sh force_brute.sh      # une seule fois
./demarrer.sh
```

Au lancement, `demarrer.sh` :
1. vérifie que `hashcat` est présent ; sinon il **propose de l'installer**
   (`sudo apt install -y hashcat`) - réponds `o`,
2. affiche le matériel détecté (`hashcat -I`) - tu dois y voir ton GPU ; sinon
   hashcat utilisera le CPU,
3. attend que tu appuies sur **Entrée**, puis lance les deux passages par liste
   de mots.

> **GPU NVIDIA** (fortement conseillé) : installe le pilote et le backend de
> calcul une fois pour toutes :
> ```bash
> sudo apt install -y nvidia-driver nvidia-cuda-toolkit
> sudo reboot
> ```
> Après redémarrage, `nvidia-smi` doit afficher ta carte. Sans GPU, tout
> fonctionne quand même sur le processeur, mais beaucoup plus lentement.

### 6. Où trouver le résultat

- **Pendant** la recherche, hashcat affiche son avancement. Quand il trouve, il
  écrit `Status....: Cracked` et affiche la ligne du hash suivie de `:` puis du
  **mot de passe en clair** à la toute fin.
- **À la fin** (ou à tout moment en relançant), le mot de passe trouvé se
  réaffiche avec :
  ```bash
  hashcat -m 9600 example/hash_test.txt --show
  ```
  Le mot de passe est ce qui apparaît **après le dernier `:`** de la ligne.
- hashcat mémorise toute trouvaille dans le fichier **`hashcat.potfile`** (dans
  ton dossier personnel, `~/.local/share/hashcat/hashcat.potfile`, ou à côté du
  binaire). Tu peux donc fermer et relancer sans tout refaire.

Si rien n'est trouvé après les deux passages : enrichis `mots_theme.txt`
(section « Personnaliser » plus bas) et relance `./demarrer.sh`, ou tente la
force brute (`./force_brute.sh`, étape 3) pour un mot de passe court.

### 7. Ouvrir le document

Saisis le mot de passe trouvé dans LibreOffice / Word / Excel à l'ouverture du
document. Voir la section « Une fois le mot de passe trouvé » en bas pour le
retirer définitivement.

---

## Étape 1 - Générer le fichier de hash depuis le document

Sur ton Mac, dans ce dossier :

```bash
python3 docx2hash.py "example/test.docx" > example/hash_test.txt
```

- Le `>` redirige le résultat dans le fichier `example/hash_test.txt`.
- Pour un tableur, c'est pareil : `python3 docx2hash.py mon_fichier.xlsx > hash.txt`
- Option `--name` : préfixe la sortie par `nomdufichier:` (format identique à
  l'outil `office2john`) :
  ```bash
  python3 docx2hash.py --name "example/test.docx"
  ```

**Dépendance** : le module Python `olefile`. S'il manque :
```bash
pip3 install --user olefile
```

### Comment ça marche

Un document Office protégé par mot de passe n'est pas un simple zip verrouillé :
son contenu est réellement **chiffré en AES-256**, et la clé est dérivée du mot
de passe. Le document (format « OLE », il commence par les octets `D0CF11E0`)
contient un flux interne, `EncryptionInfo`, qui décrit **comment** la clé est
dérivée - mais jamais le mot de passe.

`docx2hash.py` ouvre le document **en lecture seule**, lit ce flux et en extrait :

- l'algorithme (AES-256 / SHA-512),
- le **spinCount** (nombre d'itérations, ici 100 000),
- le **salt** (sel aléatoire, propre à ce fichier),
- deux **vérificateurs** chiffrés, qui permettent à hashcat de dire
  « ce mot de passe est le bon » sans ouvrir le document.

Il assemble tout ça en une ligne au format reconnu par hashcat et John :

```
$office$*2013*100000*256*16*<salt>*<verifier>*<verifier_hash>
          │     │     │  │
          │     │     │  └ taille du sel (octets)
          │     │     └ taille de clé AES (bits)
          │     └ nombre d'itérations
          └ schéma de chiffrement Office (2013 = Office 2013+)
```

> Détail technique : le XML `EncryptionInfo` contient **deux** sels. `docx2hash.py`
> lit bien celui de l'élément `encryptedKey` (celui du mot de passe), et non
> celui de `keyData`. C'est ce qui garantit une empreinte correcte.

Le `example/hash_test.txt` fourni a été vérifié : il correspond exactement à ce que
le script régénère depuis le document.

---

## Étape 2 - Retrouver le mot de passe (liste de mots)

### Sous Linux (Debian / Ubuntu)

Sur le PC Linux, dans le dossier copié :

```bash
chmod +x demarrer.sh force_brute.sh    # une seule fois
./demarrer.sh
```

`demarrer.sh` fait l'équivalent du `.bat` :
- vérifie / propose d'installer hashcat (`sudo apt install hashcat`),
- localise les règles (`/usr/share/hashcat/rules/` avec le paquet apt),
- affiche le matériel (`hashcat -I`),
- lance les **deux passages** (règles `best64` puis `rockyou-30000`, mode `-m 9600`),
- affiche le résultat (`--show`).

Pré-requis GPU NVIDIA sous Debian : le pilote `nvidia-driver` et le backend
CUDA ou OpenCL. Sans GPU, hashcat utilise le CPU (beaucoup plus lent).
hashcat enregistre ce qu'il a déjà cassé dans `hashcat.potfile` : tu peux
relancer `./demarrer.sh` sans tout recommencer.

### Sous Windows (PC avec GPU NVIDIA)

1. Copie **tout** le dossier sur le PC (garde les fichiers ensemble).
2. Double-clique sur **`DEMARRER.bat`**. Il va, tout seul :
   - télécharger et installer hashcat (~60 Mo),
   - afficher le GPU détecté (`hashcat -I`),
   - lancer **deux passages** sur l'empreinte (mode `-m 9600` = Office 2013) :
     - **Passage 1** : les mots de `mots_theme.txt` + variantes courantes
       (règle `best64` : majuscules, chiffres, années, `!`, etc.),
     - **Passage 2** : les mêmes mots + un jeu de variantes beaucoup plus large
       (règle `rockyou-30000`).
3. Si un mot de passe est trouvé, il s'affiche à la fin et avec `--show`.
   Note-le.

Tu peux relancer `DEMARRER.bat` autant de fois que tu veux : hashcat retient ce
qui est déjà cassé (`hashcat.potfile`) et reprend où il en était.

### Personnaliser `mots_theme.txt` - c'est ici que tout se joue

Plus la liste est **pertinente**, plus tu as de chances. La liste actuelle est
bâtie autour du thème *Aristote / philosophie grecque*. Ajoute **tous** les mots
qui pourraient avoir servi de base au mot de passe, **un par ligne** :

- prénoms, noms, surnoms, lieux, dates qui te parlent,
- mots que **tu** utilisais à l'époque sur d'autres comptes,
- le sujet du document, des noms propres qui y figurent.

Inutile d'ajouter les majuscules, chiffres ou `!` toi-même : les **règles**
(`best64`, `rockyou-30000`) génèrent automatiquement `Aristote`, `aristote2019`,
`Aristote!`, `ARISTOTE`, etc. à partir de chaque mot.

---

## Étape 3 - Force brute par masque (dernier recours)

Si la liste de mots ne donne rien et que tu penses à un mot de passe **court et
sans mot reconnaissable** (ex. un code) :

**Sous Linux** - passe le masque en argument, ou édite la ligne `MASQUE=` du script :
```bash
./force_brute.sh '?d?d?d?d'      # ex. 4 chiffres
```

**Sous Windows** - édite **`FORCE_BRUTE.bat`** avec le Bloc-notes et modifie la ligne :

```bat
set "MASQUE=?d?d?d?d?d?d"
```

Symboles de masque :

| Symbole | Signifie |
|---|---|
| `?d` | un chiffre (0-9) |
| `?l` | une lettre minuscule |
| `?u` | une lettre majuscule |
| `?s` | un caractère spécial |

Exemples :
- `?d?d?d?d` → 4 chiffres
- `?u?l?l?l?l?d` → Majuscule + 4 minuscules + 1 chiffre

Enregistre, puis double-clique sur le fichier. hashcat affiche d'abord une
**estimation de durée** : si elle est énorme, ferme la fenêtre et raccourcis le
masque. Chaque caractère en plus multiplie fortement le temps.

---

## Combien de temps ça prend ?

Ce document utilise le chiffrement Office le plus coûteux à attaquer :
**AES-256 + SHA-512 + 100 000 itérations**. Chaque essai est volontairement lent.

| GPU | Essais / seconde (mode 9600) |
|---|---|
| RTX 4090 | ~100 000 à 150 000 |
| RTX 3060 | ~25 000 à 40 000 |

Conséquences concrètes :

- **Liste de mots ciblée + règles** (étape 2) : quelques milliers de mots passent
  en **minutes**. C'est de loin ta meilleure chance → soigne `mots_theme.txt`.
- **Force brute** (étape 3) : réaliste seulement pour des mots de passe
  **courts**. Au-delà de ~7-8 caractères « tout type », c'est hors de portée même
  sur un gros GPU.
- Un mot de passe **long et totalement aléatoire** jamais noté ne sera
  probablement pas retrouvé. Dans ce cas, mieux vaut chercher une copie non
  protégée ou un gestionnaire de mots de passe où il aurait pu être enregistré.

---

## Une fois le mot de passe trouvé

Ouvre simplement le document dans Word / Excel et saisis le mot de passe. Pour
le retirer définitivement : *Fichier → Informations → Protéger le document →
Chiffrer avec mot de passe*, efface le champ, puis enregistre.
