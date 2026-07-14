# import cv2 as cv
# import numpy as np
# import easyocr as easy

# chemin = r"CIN_photos\WhatsApp Image 2026-07-11 at 21.58.54.jpeg"
# img = cv.imread(chemin)

# if img is None:
#     print(f"Erreur de chemin : {chemin}")
#     exit()

# # 1. Passage en gris et rotation (comme ton code initial qui fonctionnait)
# img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
# img_gray = cv.rotate(img_gray, cv.ROTATE_90_COUNTERCLOCKWISE)

# # 2. Redimensionnement (pour garder les mêmes proportions)
# height, width = img_gray.shape[:2]
# r_height = int(height * 0.75)
# r_width = int(width * 0.75)
# img_gray = cv.resize(img_gray, (r_width, r_height), cv.INTER_AREA)

# # 3. Flou très léger (3x3 ou 5x5) pour lisser le bruit sans effacer les lettres
# img_blurred = cv.GaussianBlur(img_gray, (5, 5), 0)

# # 4. LE SEUILLAGE ADAPTATIF (Pour éviter l'écran blanc d'Otsu !)
# img_pret_pour_ocr = cv.adaptiveThreshold(
#     img_blurred, 
#     255, 
#     cv.ADAPTIVE_THRESH_GAUSSIAN_C, 
#     cv.THRESH_BINARY, 
#     15, # Taille du bloc local (15x15 pixels)
#     4   # Constante soustraite à la moyenne
# )

# # --- VÉRIFICATION VISUELLE ---
# # Cette fois-ci, tu devrais voir ton texte en noir sur fond blanc !
# cv.imshow("Image propre pour EasyOCR", img_pret_pour_ocr)
# print("[INFO] Appuie sur n'importe quelle touche sur la fenêtre de l'image pour lancer l'OCR...")
# cv.waitKey(0) 

# # 5. RUN EASYOCR
# print("\n[INFO] Initialisation d'EasyOCR...")
# reader = easy.Reader(['fr', 'en'], gpu=False)

# print("[INFO] Lecture des caractères...")
# results = reader.readtext(img_pret_pour_ocr, detail=0)

# print("\n--- RÉSULTATS D'EASYOCR ---")
# for re in results:
#     print(re)

# cv.destroyAllWindows()

import cv2 as cv
import numpy as np
import easyocr as easy

# 1. Chargement de l'image
path_image = r"CIN_photos\WhatsApp Image 2026-07-11 at 20.02.54.jpeg" 
img = cv.imread(path_image)

if img is None:
    print("Erreur de chemin")
    exit()

# --- SÉCURITÉ ANTI-ROTATION SMARTPHONE ---
# Si l'image est plus haute que large, ou si elle arrive couchée, 
# on s'assure qu'on travaille dans le sens où tu la vois normalement.
height, width = img.shape[:2]
if width > height:
    # Si la photo WhatsApp arrive de côté, on la pivote pour l'avoir face à soi
    img = cv.rotate(img, cv.ROTATE_90_COUNTERCLOCKWISE)
    height, width = img.shape[:2]

norm_width = 800
norm_height = 500
pts_cliques = []

def obtenir_coins(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        pts_cliques.append([x, y])
        cv.circle(img_PROPRE, (x, y), 25, (0, 0, 255), -1)
        cv.imshow("CLIQUE DANS L'ORDRE : HG -> HD -> BD -> BG", img_PROPRE)
        
        if len(pts_cliques) == 4:
            print("[INFO] 4 coins reçus. Appuie sur une touche...")

img_PROPRE = img.copy()

cv.namedWindow("CLIQUE DANS L'ORDRE : HG -> HD -> BD -> BG", cv.WINDOW_NORMAL)
cv.resizeWindow("CLIQUE DANS L'ORDRE : HG -> HD -> BD -> BG", 600, 800)
cv.setMouseCallback("CLIQUE DANS L'ORDRE : HG -> HD -> BD -> BG", obtenir_coins)

print("\n--- CLIQUE DANS CET ORDRE PRÉCIS ---")
print("1. Coin Haut-Gauche de la carte d'identité")
print("2. Coin Haut-Droite")
print("3. Coin Bas-Droite")
print("4. Coin Bas-Gauche")

cv.imshow("CLIQUE DANS L'ORDRE : HG -> HD -> BD -> BG", img_PROPRE)
cv.waitKey(0)
cv.destroyAllWindows()

if len(pts_cliques) == 4:
    rect = np.array(pts_cliques, dtype="float32")
    
    # Cible standard OpenCV
    dst = np.array([
        [0, 0],
        [norm_width - 1, 0],
        [norm_width - 1, norm_height - 1],
        [0, norm_height - 1]
    ], dtype="float32")
    
    # Prétraitement adaptatif
    orig_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    orig_blurred = cv.GaussianBlur(orig_gray, (5, 5), 0)
    img_binarisee = cv.adaptiveThreshold(
        orig_blurred, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 15, 4
    )
    
    # Transformation de perspective
    M = cv.getPerspectiveTransform(rect, dst)
    carte_final_ocr = cv.warpPerspective(img_binarisee, M, (norm_width, norm_height))
    
    # Affichage pour vérifier
    cv.namedWindow("Carte Redressee Finale", cv.WINDOW_NORMAL)
    cv.resizeWindow("Carte Redressee Finale", 600, 380)
    cv.imshow("Carte Redressee Finale", carte_final_ocr)
    print("[INFO] Appuie sur une touche pour lancer l'OCR...")
    cv.waitKey(0)
    
    # Lancement EasyOCR
    print("\n[INFO] Initialisation d'EasyOCR...")
    reader = easy.Reader(['fr', 'en'], gpu=False)
    results = reader.readtext(carte_final_ocr, detail=0)
    
    print("\n--- RÉSULTATS DE L'OCR ---")
    if len(results) == 0:
        print("[ALERTE] EasyOCR n'a toujours rien trouvé. L'image est encore illisible.")
    else:
        for texte in results:
            print(texte)
else:
    print("Erreur : Recommence et clique sur les 4 coins.")
cv.destroyAllWindows()