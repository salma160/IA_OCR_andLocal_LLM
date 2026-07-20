import cv2 as cv
import easyocr
from ollama import chat
import sys

from analyse_img import analyser_img
from ocr_paddle import ocr_paddle

# =====================================================
# Chargement EasyOCR (une seule fois)
# =====================================================

reader_ar = easyocr.Reader(
    ['ar'],
    gpu=False
)





# =====================================================
# Récupération des données envoyées par PHP
# =====================================================

chemin = sys.argv[1]

nom_form = sys.argv[2]
prenom_form = sys.argv[3]
nom_ar_form = sys.argv[4]
prenom_ar_form = sys.argv[5]
date_naissance_form = sys.argv[6]
cin_form = sys.argv[7]
date_expiration_form = sys.argv[8]

# =====================================================
# Plus tard : conversion PDF -> JPEG
# =====================================================

"""
import fitz

doc = fitz.open(chemin)

page = doc.load_page(0)

pix = page.get_pixmap(dpi=300)

pix.save("temp_pdf.jpg")

chemin = "temp_pdf.jpg"
"""



img = cv.imread(chemin)

if img is None:
    raise ValueError("Impossible de lire l'image.")

# =====================================================
# Agrandissement
# =====================================================

img = cv.resize(
    img,
    None,
    fx=2,
    fy=2,
    interpolation=cv.INTER_CUBIC
)

# =====================================================
# Prétraitement
# =====================================================

img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

img_gray = analyser_img(img_gray)

# Paddle veut une image BGR
img_bgr = cv.cvtColor(img_gray, cv.COLOR_GRAY2BGR)

# Sauvegarde temporaire
chemin_temp = "temp_ocr.jpg"

cv.imwrite(chemin_temp, img_bgr)

# =====================================================
# PaddleOCR (Français)
# =====================================================

texte_fr = ocr_paddle(img_bgr)

print("\n========== OCR Paddle ==========\n")
print(texte_fr)

# =====================================================
# EasyOCR (Arabe)
# =====================================================

print("\n========== OCR EasyOCR (Arabe) ==========\n")

resultats_ar = reader_ar.readtext(
    img_bgr,
    detail=0,
    paragraph=False
)

texte_ar = "\n".join(resultats_ar)

print(texte_ar)

# =====================================================
# MiniCPM-V
# =====================================================

print("\n========== MiniCPM-V ==========\n")

reponse = chat(
    model="minicpm-v:latest",
    messages=[
        {
            "role": "user",
            
"content": f"""
Tu es un moteur OCR.

Tu dois uniquement recopier les informations visibles sur la carte.

Ne traduis jamais.

N'invente jamais.

N'interprète jamais.

Sur une Carte Nationale d'Identité marocaine :

- la première ligne contenant un nom en français correspond toujours au PRÉNOM ;
- la deuxième ligne correspond toujours au NOM.

Exemple :

Première ligne :
ABDELHAFID

Deuxième ligne :
LECHKAR

Tu dois répondre :

Nom (français) : LECHKAR
Prénom (français) : ABDELHAFID

La date de validité est la date située juste après la mention :

Valable jusqu'au

Si cette date est visible, recopie-la exactement.

Ne laisse jamais ce champ vide.

Si une information est réellement illisible, écris UNKNOWN.

Réponds UNIQUEMENT sous cette forme :

Nom (français) :
Prénom (français) :
Numéro CIN :
Date de naissance :
Lieu de naissance :
Date de validité :

=====================
OCR français :

{texte_fr}

=====================
OCR arabe :

{texte_ar}
""",
            "images": [chemin_temp]
        }
    ]
)

print(reponse["message"]["content"])
# =====================================================
# Récupération des informations du LLM
# =====================================================

texte_llm = reponse["message"]["content"]

infos = {}

for ligne in texte_llm.splitlines():

    if ":" in ligne:

        cle, valeur = ligne.split(":", 1)

        infos[cle.strip()] = valeur.strip()
# =====================================================
# Comparaison avec les données du formulaire
# =====================================================

erreurs = []

# =====================================================
# Nom + prénom
# =====================================================

nom_llm = infos.get("Nom (français)", "").upper()
prenom_llm = infos.get("Prénom (français)", "").upper()

if nom_llm.strip().upper() != nom_form.strip().upper():
    erreurs.append("Nom français incorrect")

if prenom_llm.strip().upper() != prenom_form.strip().upper():
    erreurs.append("Prénom français incorrect")

# =====================================================
# Numéro CIN
# =====================================================

cin_llm = infos.get("Numéro CIN", "").upper().strip()

if cin_llm != cin_form.upper():
    erreurs.append("Numéro CIN incorrect")

# =====================================================
# Date d'expiration
# =====================================================

date_llm = infos.get("Date de validité", "")

date_llm = (
    date_llm
    .replace("Valable jusqu'au", "")
    .replace("Valable jusqu’à", "")
    .replace("Valable jusquau", "")
    .replace("/", ".").replace("-", ".")
    .strip()
)

# Le formulaire donne : 2031-04-12
# On le transforme en : 12.04.2031

annee, mois, jour = date_expiration_form.split("-")

date_form = f"{jour}.{mois}.{annee}"

if date_llm != date_form:
    erreurs.append("Date d'expiration incorrecte")
# =====================================================
# Résultat final
# =====================================================

print("\n========== VERIFICATION ==========\n")

if len(erreurs) == 0:

    print("VERIFICATION REUSSIE")

else:

    print("VERIFICATION ECHOUEE")

    for e in erreurs:
        print("-", e)