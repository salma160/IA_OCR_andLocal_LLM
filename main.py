# =====================================================
# IMPORTS
# =====================================================

import os
import re
import sys

import cv2 as cv
import fitz

from ollama import chat

from analyse_img import analyser_img
from ocr_paddle import ocr_paddle


# =====================================================
# INFORMATIONS PYTHON (DEBUG)
# =====================================================

print("Python :", sys.executable)
print("Version :", sys.version)

try:
    import packaging
    print("Packaging :", packaging.__file__)
except ImportError:
    print("Packaging : non trouvé")


# =====================================================
# VERIFICATION DES ARGUMENTS
# =====================================================

if len(sys.argv) != 9:
    raise Exception(
        "Nombre d'arguments incorrect.\n"
        "Utilisation : python main.py image nom prenom nom_ar prenom_ar dateNaissance cin dateExpiration"
    )


# =====================================================
# ARGUMENTS RECUS DE PHP
# =====================================================

chemin = sys.argv[1]

nom_form = sys.argv[2].strip()
prenom_form = sys.argv[3].strip()

nom_ar_form = sys.argv[4].strip()
prenom_ar_form = sys.argv[5].strip()

date_naissance_form = sys.argv[6].strip()
cin_form = sys.argv[7].strip()
date_expiration_form = sys.argv[8].strip()


# =====================================================
# FONCTIONS UTILITAIRES
# =====================================================

def normaliser_texte(texte):
    """
    Met en majuscules, supprime les espaces inutiles.
    """

    texte = texte.upper().strip()

    texte = re.sub(r"\s+", " ", texte)

    return texte


def normaliser_cin(cin):
    """
    K71415
    k71415
    K 71415

    => K71415
    """

    cin = normaliser_texte(cin)

    cin = cin.replace(" ", "")

    return cin


def normaliser_date(date):
    """
    Accepte :

    12.04.2031
    12/04/2031
    12-04-2031
    2031-04-12

    Retourne toujours :

    12.04.2031
    """

    if not date:
        return ""

    date = date.strip()

    date = date.replace("/", ".")
    date = date.replace("-", ".")

    date = re.sub(
        r"VALABLE\s*JUSQU['’]?\s*AU",
        "",
        date,
        flags=re.IGNORECASE
    )

    date = date.strip()

    # JJ.MM.AAAA

    m = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", date)

    if m:
        return f"{m.group(1)}.{m.group(2)}.{m.group(3)}"

    # AAAA.MM.JJ

    m = re.search(r"(\d{4})\.(\d{2})\.(\d{2})", date)

    if m:
        return f"{m.group(3)}.{m.group(2)}.{m.group(1)}"

    return date

# =====================================================
# LECTURE DU FICHIER (JPEG OU PDF)
# =====================================================

extension = os.path.splitext(chemin)[1].lower()

chemin_pdf = None

if extension == ".pdf":

    print("\n========== CONVERSION PDF ==========\n")

    doc = fitz.open(chemin)

    page = doc.load_page(0)

    pix = page.get_pixmap(dpi=300)

    chemin_pdf = "temp_pdf.jpg"

    pix.save(chemin_pdf)

    doc.close()

    chemin = chemin_pdf


# =====================================================
# LECTURE DE L'IMAGE
# =====================================================

img = cv.imread(chemin)

if img is None:
    raise Exception("Impossible de lire l'image.")


# =====================================================
# AGRANDISSEMENT
# =====================================================

img = cv.resize(
    img,
    None,
    fx=2,
    fy=2,
    interpolation=cv.INTER_CUBIC
)


# =====================================================
# PRETRAITEMENT
# =====================================================

img_gray = cv.cvtColor(
    img,
    cv.COLOR_BGR2GRAY
)

img_gray = analyser_img(img_gray)


# =====================================================
# RETOUR EN BGR POUR PADDLEOCR
# =====================================================

img_bgr = cv.cvtColor(
    img_gray,
    cv.COLOR_GRAY2BGR
)


# =====================================================
# IMAGE TEMPORAIRE POUR LE LLM
# =====================================================

chemin_temp = "temp_ocr.jpg"

cv.imwrite(
    chemin_temp,
    img_bgr
)

# =====================================================
# PADDLEOCR
# =====================================================

print("\n========== OCR PADDLE ==========\n")

texte_fr = ocr_paddle(img_bgr)

print(texte_fr)


# =====================================================
# EXTRACTION PYTHON
# =====================================================

print("\n========== EXTRACTION PYTHON ==========\n")

lignes = []

for ligne in texte_fr.splitlines():

    ligne = ligne.strip()

    if ligne != "":
        lignes.append(ligne)


nom_ocr = ""
prenom_ocr = ""
cin_ocr = ""
date_naissance_ocr = ""
date_validite_ocr = ""


# =====================================================
# NOM / PRENOM
# =====================================================

for i, ligne in enumerate(lignes):

    if "CARTE NATIONALE" in ligne.upper():

        # Première ligne après le titre = prénom

        if i + 1 < len(lignes):
            prenom_ocr = normaliser_texte(lignes[i + 1])

        # Deuxième ligne = nom

        if i + 2 < len(lignes):
            nom_ocr = normaliser_texte(lignes[i + 2])

        break


# =====================================================
# CIN
# =====================================================

m = re.search(
    r"\b[A-Z]{1,2}\s*\d{4,8}\b",
    texte_fr.upper()
)

if m:

    cin_ocr = normaliser_cin(
        m.group()
    )


# =====================================================
# DATES
# =====================================================

dates = re.findall(
    r"\d{2}[./-]\d{2}[./-]\d{4}|\d{4}[./-]\d{2}[./-]\d{2}",
    texte_fr
)

dates = [
    normaliser_date(d)
    for d in dates
]


if len(dates) >= 1:

    # Sur la CIN marocaine la dernière date est
    # quasiment toujours la date de validité.

    date_validite_ocr = dates[-1]


if len(dates) >= 2:

    # La première est généralement la naissance.

    date_naissance_ocr = dates[0]


# =====================================================
# AFFICHAGE
# =====================================================

print("Nom OCR            :", nom_ocr)
print("Prénom OCR         :", prenom_ocr)
print("CIN OCR            :", cin_ocr)
print("Naissance OCR      :", date_naissance_ocr)
print("Validité OCR       :", date_validite_ocr)


# =====================================================
# OCR ARABE
# =====================================================

# EasyOCR a été retiré.
# On laisse une variable vide afin que
# MiniCPM puisse compléter si nécessaire.

texte_ar = ""

# =====================================================
# MiniCPM-V
# =====================================================

print("\n========== MiniCPM-V ==========\n")

prompt = f"""
Tu es un système d'extraction d'informations.

Tu reçois :

- une image de Carte Nationale d'Identité marocaine ;
- le texte OCR suivant.

Tu dois UNIQUEMENT extraire les champs.

IMPORTANT :

- Le premier nom français est le PRÉNOM.
- Le deuxième nom français est le NOM.
- Le numéro CIN commence par une ou deux lettres suivies de chiffres.
- La date de validité est celle qui suit "Valable jusqu'au".
- Si une information est absente, écrire UNKNOWN.
- Ne jamais expliquer.
- Ne jamais ajouter de texte.

Réponds EXACTEMENT sous cette forme :

Nom (français) :
Prénom (français) :
Nom (arabe) :
Prénom (arabe) :
Numéro CIN :
Date de naissance :
Lieu de naissance :
Date de validité :

=================

OCR :

{texte_fr}
"""

reponse = chat(
    model="minicpm-v:latest",
    messages=[
        {
            "role": "user",
            "content": prompt,
            "images": [chemin_temp]
        }
    ]
)

texte_llm = reponse["message"]["content"]

print(texte_llm)


# =====================================================
# Lecture de la réponse du LLM
# =====================================================

infos = {}

for ligne in texte_llm.splitlines():

    if ":" not in ligne:
        continue

    cle, valeur = ligne.split(":", 1)

    infos[cle.strip()] = valeur.strip()

# =====================================================
# VERIFICATION
# =====================================================

print("\n========== VERIFICATION ==========\n")

erreurs = []


# -------------------------
# Nom
# -------------------------

nom_llm = normaliser_texte(
    infos.get("Nom (français)", "")
)

nom_form = normaliser_texte(nom_form)

if nom_llm != nom_form:

    erreurs.append(
        f"Nom incorrect : OCR='{nom_llm}' / Formulaire='{nom_form}'"
    )


# -------------------------
# Prénom
# -------------------------

prenom_llm = normaliser_texte(
    infos.get("Prénom (français)", "")
)

prenom_form = normaliser_texte(prenom_form)

if prenom_llm != prenom_form:

    erreurs.append(
        f"Prénom incorrect : OCR='{prenom_llm}' / Formulaire='{prenom_form}'"
    )


# -------------------------
# CIN
# -------------------------

cin_llm = normaliser_cin(
    infos.get("Numéro CIN", "")
)

if cin_llm != cin_form:

    erreurs.append(
        f"CIN incorrect : OCR='{cin_llm}' / Formulaire='{cin_form}'"
    )


# -------------------------
# Date de naissance
# -------------------------

date_naissance_llm = normaliser_date(
    infos.get("Date de naissance", "")
)

date_naissance_form = normaliser_date(
    date_naissance_form
)

if (
    date_naissance_llm != ""
    and
    date_naissance_llm != date_naissance_form
):

    erreurs.append(
        f"Date de naissance incorrecte : OCR='{date_naissance_llm}' / Formulaire='{date_naissance_form}'"
    )


# -------------------------
# Date de validité
# -------------------------

date_validite_llm = normaliser_date(
    infos.get("Date de validité", "")
)

date_expiration_form = normaliser_date(
    date_expiration_form
)

if date_validite_llm != date_expiration_form:

    erreurs.append(
        f"Date d'expiration incorrecte : OCR='{date_validite_llm}' / Formulaire='{date_expiration_form}'"
    )


# =====================================================
# RESULTAT
# =====================================================

if len(erreurs) == 0:

    print("VERIFICATION REUSSIE")

else:

    print("VERIFICATION ECHOUEE\n")

    for erreur in erreurs:

        print("-", erreur)


# =====================================================
# NETTOYAGE
# =====================================================

if os.path.exists(chemin_temp):

    os.remove(chemin_temp)

if chemin_pdf is not None:

    if os.path.exists(chemin_pdf):

        os.remove(chemin_pdf)