#!/usr/bin/env python3
"""
docx2hash.py - Extrait l'empreinte (hash) d'un document Office chiffre.

Prend un .docx/.xlsx/.pptx protege par mot de passe (chiffrement "agile"
Office 2010/2013+) et ecrit sur la sortie standard la ligne au format
$office$ reconnue par John the Ripper et hashcat (mode -m 9600).

Usage :
    python3 docx2hash.py "example/test.docx" > example/hash_test.txt
    python3 docx2hash.py --name document.docx          # prefixe "nom:hash"

Ne modifie jamais le document d'origine : il est ouvert en lecture seule.
Necessite le module olefile :  pip3 install --user olefile
"""
import sys
import base64
import re
import argparse

try:
    import olefile
except ImportError:
    sys.exit("Erreur : module 'olefile' manquant.  Installe-le avec :\n"
             "    pip3 install --user olefile")


def attr(name, scope):
    m = re.search(r'%s="([^"]+)"' % name, scope)
    return m.group(1) if m else None


def docx_to_hash(path):
    if not olefile.isOleFile(path):
        raise ValueError(
            "Ce fichier n'est pas un conteneur OLE chiffre.\n"
            "  - un .docx NON protege est un .zip (commence par 'PK') : rien a extraire.\n"
            "  - un .docx protege par mot de passe commence par D0CF11E0.")

    ole = olefile.OleFileIO(path)
    try:
        if not ole.exists('EncryptionInfo'):
            raise ValueError("Flux 'EncryptionInfo' absent : format de chiffrement non gere.")
        data = ole.openstream('EncryptionInfo').read()
    finally:
        ole.close()

    major, minor = data[0], data[2]
    if (major, minor) not in ((4, 4), (3, 3), (4, 3)):
        raise ValueError(
            "Chiffrement non 'agile' (version %d.%d). Ce script gere Office 2010/2013+ "
            "(version 4.4). Les anciens .doc/.xls binaires ne sont pas pris en charge." % (major, minor))

    xml = data[8:].decode('utf-8', 'ignore')

    # L'element <...encryptedKey ...> porte les verificateurs du MOT DE PASSE
    # et SON propre saltValue (a ne pas confondre avec celui de <keyData>).
    m = re.search(r'<[^>]*encryptedKey[^>]*encryptedVerifierHashInput[^>]*/>', xml)
    if not m:
        raise ValueError("Element encryptedKey introuvable dans EncryptionInfo.")
    enc = m.group(0)

    spin = attr('spinCount', enc)
    keybits = attr('keyBits', enc)
    salt = base64.b64decode(attr('saltValue', enc))
    vin = base64.b64decode(attr('encryptedVerifierHashInput', enc))
    vval = base64.b64decode(attr('encryptedVerifierHashValue', enc))

    return "$office$*2013*%s*%s*%d*%s*%s*%s" % (
        spin, keybits, len(salt), salt.hex(), vin.hex(), vval.hex())


def main():
    p = argparse.ArgumentParser(description="Extrait le hash $office$ d'un document Office chiffre.")
    p.add_argument("fichier", help="chemin du .docx/.xlsx/.pptx protege par mot de passe")
    p.add_argument("--name", action="store_true",
                   help="prefixer la sortie par 'nomdufichier:' (comme office2john)")
    args = p.parse_args()

    try:
        h = docx_to_hash(args.fichier)
    except Exception as e:
        sys.exit("Erreur : %s" % e)

    if args.name:
        import os
        print("%s:%s" % (os.path.basename(args.fichier), h))
    else:
        print(h)


if __name__ == "__main__":
    main()
