import os
import re
import time
import cv2 as cv
import fitz
import mysql.connector

from ollama import chat
from analyse_img import analyser_img
from ocr_paddle import ocr_paddle


# =========================================================
# CONNEXION MYSQL
# =========================================================

def connecter_mysql():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gestion_concours"
    )


# =========================================================
# NORMALISATION TEXTE
# =========================================================

def normaliser_texte(texte):

    if texte is None:
        return ""

    texte = str(texte).strip()

    texte = texte.replace("**", "")
    texte = texte.replace("*", "")
    texte = texte.strip()

    if texte.upper() in [
        "UNKNOWN",
        "INCONNU",
        "N/A",
        "NA",
        ""
    ]:
        return ""

    texte = texte.upper()

    texte = re.sub(
        r"\s+",
        " ",
        texte
    )

    return texte


# =========================================================
# NORMALISATION CIN
# =========================================================

def normaliser_cin(cin):

    cin = normaliser_texte(cin)

    cin = cin.replace(" ", "")

    return cin


# =========================================================
# NORMALISATION DATE
# Format interne : JJ.MM.AAAA
# =========================================================

def normaliser_date(date):

    if date is None:
        return ""

    date = str(date).strip()

    if date.upper() in [
        "UNKNOWN",
        "INCONNU",
        "N/A",
        "NA"
    ]:
        return ""

    date = date.replace("/", ".")
    date = date.replace("-", ".")

    # JJ.MM.AAAA
    match = re.search(
        r"(\d{2})\.(\d{2})\.(\d{4})",
        date
    )

    if match:

        return (
            f"{match.group(1)}."
            f"{match.group(2)}."
            f"{match.group(3)}"
        )

    # AAAA.MM.JJ
    match = re.search(
        r"(\d{4})\.(\d{2})\.(\d{2})",
        date
    )

    if match:

        return (
            f"{match.group(3)}."
            f"{match.group(2)}."
            f"{match.group(1)}"
        )

    return ""


# =========================================================
# DATE → FORMAT MYSQL
# JJ.MM.AAAA → AAAA-MM-JJ
# =========================================================

def date_vers_mysql(date):

    date = normaliser_date(date)

    if not date:
        return None

    match = re.match(
        r"(\d{2})\.(\d{2})\.(\d{4})",
        date
    )

    if not match:
        return None

    jour = match.group(1)
    mois = match.group(2)
    annee = match.group(3)

    return f"{annee}-{mois}-{jour}"


# =========================================================
# RÉCUPÉRER UN CANDIDAT NON ENCORE VÉRIFIÉ
# =========================================================

def recuperer_candidat():

    connexion = connecter_mysql()

    curseur = connexion.cursor(
        dictionary=True
    )

    requete = """
        SELECT
            c.id_candidat,
            c.nom,
            c.prenom,
            c.date_naissance,
            c.numero_cin,
            c.date_expiration,
            c.chemin_cin

        FROM candidats c

        LEFT JOIN verifications v
            ON c.id_candidat = v.id_candidat

        WHERE v.id_candidat IS NULL

        ORDER BY c.id_candidat ASC

        LIMIT 1
    """

    curseur.execute(requete)

    candidat = curseur.fetchone()

    curseur.close()
    connexion.close()

    return candidat


# =========================================================
# ENREGISTRER LA VÉRIFICATION
# =========================================================

def enregistrer_verification(
    id_candidat,
    nom_ocr,
    prenom_ocr,
    numero_cin_ocr,
    date_naissance_ocr,
    date_expiration_ocr,
    statut
):

    connexion = connecter_mysql()

    curseur = connexion.cursor()

    # Conversion des dates pour MySQL
    date_naissance_mysql = date_vers_mysql(
        date_naissance_ocr
    )

    date_expiration_mysql = date_vers_mysql(
        date_expiration_ocr
    )

    requete = """
        INSERT INTO verifications (

            id_candidat,
            nom_ocr,
            prenom_ocr,
            numero_cin_ocr,
            date_naissance_ocr,
            date_expiration_ocr,
            statut,
            date_verification

        )

        VALUES (

            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            NOW()

        )
    """

    curseur.execute(
        requete,
        (
            id_candidat,
            nom_ocr if nom_ocr else None,
            prenom_ocr if prenom_ocr else None,
            numero_cin_ocr if numero_cin_ocr else None,
            date_naissance_mysql,
            date_expiration_mysql,
            statut
        )
    )

    connexion.commit()

    curseur.close()
    connexion.close()


# =========================================================
# EXTRAIRE UNE INFORMATION DE LA RÉPONSE MINICPM
# =========================================================

def extraire_valeur(infos, cles_possibles):

    for cle in cles_possibles:

        for cle_reponse, valeur in infos.items():

            cle_reponse_normalisee = (
                cle_reponse
                .strip()
                .replace("*", "")
                .replace("#", "")
                .strip()
                .upper()
            )

            cle_recherchee = (
                cle
                .strip()
                .replace("*", "")
                .replace("#", "")
                .strip()
                .upper()
            )

            if cle_reponse_normalisee == cle_recherchee:

                valeur = valeur.strip()

                if valeur.upper() not in [
                    "UNKNOWN",
                    "INCONNU",
                    "N/A",
                    "NA",
                    ""
                ]:

                    valeur = valeur.replace("**", "")
                    valeur = valeur.replace("*", "")
                    valeur = valeur.strip()

                    return valeur

    return ""


# =========================================================
# TRAITEMENT D'UN CANDIDAT
# =========================================================

def traiter_candidat(candidat):

    id_candidat = candidat["id_candidat"]

    nom_form = candidat["nom"]
    prenom_form = candidat["prenom"]

    date_naissance_form = candidat["date_naissance"]
    cin_form = candidat["numero_cin"]
    date_expiration_form = candidat["date_expiration"]

    chemin_relatif = candidat["chemin_cin"]


    print()
    print("============================================")
    print("NOUVEAU CANDIDAT")
    print("============================================")

    print("ID candidat :", id_candidat)
    print("Nom :", nom_form)
    print("Prénom :", prenom_form)
    print("CIN :", cin_form)
    print("Chemin :", chemin_relatif)


    # =====================================================
    # CHEMIN RELATIF → CHEMIN ABSOLU
    # =====================================================

    chemin_absolu = os.path.join(
        os.path.dirname(__file__),
        chemin_relatif
    )

    chemin_absolu = os.path.normpath(
        chemin_absolu
    )


    if not os.path.exists(chemin_absolu):

        print()
        print("ERREUR : fichier CIN introuvable.")
        print(chemin_absolu)

        enregistrer_verification(
            id_candidat,
            None,
            None,
            None,
            None,
            None,
            "DOCUMENT_INVALIDE"
        )

        return


    # =====================================================
    # GESTION PDF
    # =====================================================

    extension = os.path.splitext(
        chemin_absolu
    )[1].lower()

    chemin_image = chemin_absolu
    fichier_temp_pdf = None

    if extension == ".pdf":

        print()
        print("========== CONVERSION PDF ==========")

        document = fitz.open(
            chemin_absolu
        )

        page = document.load_page(0)

        pix = page.get_pixmap(
            dpi=300
        )

        fichier_temp_pdf = os.path.join(
            os.path.dirname(__file__),
            "temp_pdf.jpg"
        )

        pix.save(
            fichier_temp_pdf
        )

        document.close()

        chemin_image = fichier_temp_pdf


    # =====================================================
    # LECTURE IMAGE
    # =====================================================

    img = cv.imread(
        chemin_image
    )

    if img is None:

        print(
            "ERREUR : impossible de lire l'image."
        )

        enregistrer_verification(
            id_candidat,
            None,
            None,
            None,
            None,
            None,
            "DOCUMENT_INVALIDE"
        )

        return


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
    # PRÉTRAITEMENT
    # =====================================================

    img_gray = cv.cvtColor(
        img,
        cv.COLOR_BGR2GRAY
    )

    img_gray = analyser_img(
        img_gray
    )


    # =====================================================
    # DOCUMENT INVALIDE
    # =====================================================

    if img_gray is None:

        print()
        print("============================================")
        print("VERIFICATION : DOCUMENT_INVALIDE")
        print("============================================")

        enregistrer_verification(
            id_candidat,
            None,
            None,
            None,
            None,
            None,
            "DOCUMENT_INVALIDE"
        )

        return


    # =====================================================
    # RETOUR EN BGR
    # =====================================================

    img_bgr = cv.cvtColor(
        img_gray,
        cv.COLOR_GRAY2BGR
    )


    # =====================================================
    # IMAGE TEMPORAIRE POUR MINICPM
    # =====================================================

    chemin_temp = os.path.join(
        os.path.dirname(__file__),
        "temp_ocr.jpg"
    )

    cv.imwrite(
        chemin_temp,
        img_bgr
    )


    # =====================================================
    # PADDLEOCR
    # =====================================================

    print()
    print("========== OCR PADDLE ==========")

    texte_fr = ocr_paddle(
        img_bgr
    )

    print(texte_fr)


    # =====================================================
    # EXTRACTION PYTHON
    # =====================================================

    lignes = []

    for ligne in texte_fr.splitlines():

        ligne = ligne.strip()

        if ligne:
            lignes.append(ligne)


    nom_ocr = ""
    prenom_ocr = ""
    numero_cin_ocr = ""
    date_naissance_ocr = ""
    date_expiration_ocr = ""


    # =====================================================
    # NOM / PRÉNOM
    # =====================================================

    for i, ligne in enumerate(lignes):

        if "CARTE NATIONALE" in ligne.upper():

            if i + 1 < len(lignes):

                prenom_ocr = normaliser_texte(
                    lignes[i + 1]
                )

            if i + 2 < len(lignes):

                nom_ocr = normaliser_texte(
                    lignes[i + 2]
                )

            break


    # =====================================================
    # NUMÉRO CIN
    # =====================================================

    match_cin = re.search(
        r"\b[A-Z]{1,2}\s*\d{4,8}\b",
        texte_fr.upper()
    )

    if match_cin:

        numero_cin_ocr = normaliser_cin(
            match_cin.group()
        )


    # =====================================================
    # DATES OCR
    # =====================================================

    dates = re.findall(
        r"\d{2}[./-]\d{2}[./-]\d{4}"
        r"|"
        r"\d{4}[./-]\d{2}[./-]\d{2}",
        texte_fr
    )

    dates = [
        normaliser_date(date)
        for date in dates
    ]

    dates = [
        date for date in dates
        if date
    ]


    if len(dates) >= 1:

        date_naissance_ocr = dates[0]


    if len(dates) >= 2:

        date_expiration_ocr = dates[-1]


    # =====================================================
    # AFFICHAGE OCR
    # =====================================================

    print()
    print("========== INFORMATIONS OCR PADDLE ==========")

    print(
        "Nom OCR :",
        nom_ocr
    )

    print(
        "Prénom OCR :",
        prenom_ocr
    )

    print(
        "CIN OCR :",
        numero_cin_ocr
    )

    print(
        "Date naissance OCR :",
        date_naissance_ocr
    )

    print(
        "Date expiration OCR :",
        date_expiration_ocr
    )


    # =====================================================
    # MINICPM-V
    # =====================================================

    print()
    print("========== MINICPM-V ==========")

    prompt = f"""
Tu es un système d'extraction d'informations
pour une Carte Nationale d'Identité marocaine.

Tu dois extraire uniquement les informations
présentes sur la CIN.

Le texte OCR est :

{texte_fr}

Réponds exactement sous cette forme :

Nom (français) :
Prénom (français) :
Numéro CIN :
Date de naissance :
Date de validité :

Si une information est absente :
UNKNOWN
"""


    reponse = chat(

        model="minicpm-v:latest",

        messages=[
            {
                "role": "user",

                "content": prompt,

                "images": [
                    chemin_temp
                ]
            }
        ]
    )


    texte_llm = reponse[
        "message"
    ][
        "content"
    ]


    print(texte_llm)


    # =====================================================
    # EXTRACTION RÉPONSE LLM
    # =====================================================

    infos = {}

    for ligne in texte_llm.splitlines():

        if ":" not in ligne:
            continue

        cle, valeur = ligne.split(
            ":",
            1
        )

        cle = cle.strip()
        valeur = valeur.strip()

        infos[cle] = valeur


    # =====================================================
    # VALEURS LLM
    # =====================================================

    nom_llm = normaliser_texte(
        extraire_valeur(
            infos,
            [
                "Nom (français)",
                "Nom français",
                "Nom",
                "Nom (francais)",
                "Nom francais"
            ]
        )
    )


    prenom_llm = normaliser_texte(
        extraire_valeur(
            infos,
            [
                "Prénom (français)",
                "Prénom français",
                "Prenom (français)",
                "Prenom français",
                "Prénom",
                "Prenom"
            ]
        )
    )


    cin_llm = normaliser_cin(
        extraire_valeur(
            infos,
            [
                "Numéro CIN",
                "Numero CIN",
                "Numéro",
                "Numero",
                "CIN"
            ]
        )
    )


    date_naissance_llm = normaliser_date(
        extraire_valeur(
            infos,
            [
                "Date de naissance",
                "Date naissance",
                "Date de naissance (JJ.MM.AAAA)"
            ]
        )
    )


    date_expiration_llm = normaliser_date(
        extraire_valeur(
            infos,
            [
                "Date de validité",
                "Date validite",
                "Date d'expiration",
                "Date expiration"
            ]
        )
    )


    # =====================================================
    # FALLBACK OCR
    # =====================================================

    if not nom_llm and nom_ocr:

        nom_llm = nom_ocr


    if not prenom_llm and prenom_ocr:

        prenom_llm = prenom_ocr


    if not cin_llm and numero_cin_ocr:

        cin_llm = numero_cin_ocr


    if not date_naissance_llm and date_naissance_ocr:

        date_naissance_llm = date_naissance_ocr


    if not date_expiration_llm and date_expiration_ocr:

        date_expiration_llm = date_expiration_ocr


    # =====================================================
    # AFFICHAGE DES INFORMATIONS FINALES
    # =====================================================

    print()
    print("========== INFORMATIONS FINALES ==========")

    print(
        "Nom :",
        nom_llm
    )

    print(
        "Prénom :",
        prenom_llm
    )

    print(
        "Numéro CIN :",
        cin_llm
    )

    print(
        "Date de naissance :",
        date_naissance_llm
    )

    print(
        "Date de validité :",
        date_expiration_llm
    )


    # =====================================================
    # NORMALISATION FORMULAIRE
    # =====================================================

    nom_form = normaliser_texte(
        nom_form
    )

    prenom_form = normaliser_texte(
        prenom_form
    )

    cin_form = normaliser_cin(
        cin_form
    )

    date_naissance_form = normaliser_date(
        date_naissance_form
    )

    date_expiration_form = normaliser_date(
        date_expiration_form
    )


    # =====================================================
    # VÉRIFICATION
    # =====================================================

    erreurs = []


    if not nom_llm:

        erreurs.append(
            "Nom non extrait"
        )

    elif nom_llm != nom_form:

        erreurs.append(
            "Nom différent"
        )


    if not prenom_llm:

        erreurs.append(
            "Prénom non extrait"
        )

    elif prenom_llm != prenom_form:

        erreurs.append(
            "Prénom différent"
        )


    if not cin_llm:

        erreurs.append(
            "Numéro CIN non extrait"
        )

    elif cin_llm != cin_form:

        erreurs.append(
            "Numéro CIN différent"
        )


    if not date_naissance_llm:

        erreurs.append(
            "Date de naissance non extraite"
        )

    elif date_naissance_llm != date_naissance_form:

        erreurs.append(
            "Date de naissance différente"
        )


    if not date_expiration_llm:

        erreurs.append(
            "Date d'expiration non extraite"
        )

    elif date_expiration_llm != date_expiration_form:

        erreurs.append(
            "Date d'expiration différente"
        )


    # =====================================================
    # STATUT
    # =====================================================

    if len(erreurs) == 0:

        statut = "VALIDE"

        print()
        print("============================================")
        print("VERIFICATION : VALIDE")
        print("============================================")

    else:

        statut = "NON_VALIDE"

        print()
        print("============================================")
        print("VERIFICATION : NON_VALIDE")
        print("============================================")

        for erreur in erreurs:

            print(
                "-",
                erreur
            )


    # =====================================================
    # ENREGISTREMENT MYSQL
    # =====================================================

    print()
    print("========== ENREGISTREMENT MYSQL ==========")

    enregistrer_verification(

        id_candidat,

        nom_llm,

        prenom_llm,

        cin_llm,

        date_naissance_llm,

        date_expiration_llm,

        statut
    )

    print(
        "Vérification enregistrée."
    )


    # =====================================================
    # NETTOYAGE
    # =====================================================

    if os.path.exists(
        chemin_temp
    ):

        os.remove(
            chemin_temp
        )


    if (
        fichier_temp_pdf
        and
        os.path.exists(
            fichier_temp_pdf
        )
    ):

        os.remove(
            fichier_temp_pdf
        )


# =========================================================
# PROGRAMME PRINCIPAL
# =========================================================

print()
print("============================================")
print("SYSTÈME DE VÉRIFICATION DES CIN")
print("============================================")
print("Connexion à MySQL...")
print("En attente de nouveaux candidats...")
print()


while True:

    try:

        candidat = recuperer_candidat()

        if candidat is None:

            time.sleep(3)

            continue


        traiter_candidat(
            candidat
        )


    except Exception as e:

        print()
        print("============================================")
        print("ERREUR")
        print("============================================")

        print(e)

        print()
        print("Nouvelle tentative dans 5 secondes...")

        time.sleep(5)