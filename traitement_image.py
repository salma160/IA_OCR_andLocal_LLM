import cv2 as cv
import numpy as np
import easyocr as easy

chemin = r"CIN_photos\WhatsApp Image 2026-07-11 at 21.58.54.jpeg"
img = cv.imread(chemin)

if img is None:
    print(f"Erreur de chemin : {chemin}")
    exit()

# 1. Passage en gris et rotation (comme ton code initial qui fonctionnait)
img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
img_gray = cv.rotate(img_gray, cv.ROTATE_90_COUNTERCLOCKWISE)

# 2. Redimensionnement (pour garder les mêmes proportions)
height, width = img_gray.shape[:2]
r_height = int(height * 0.75)
r_width = int(width * 0.75)
img_gray = cv.resize(img_gray, (r_width, r_height), cv.INTER_AREA)

# 3. Flou très léger (3x3 ou 5x5) pour lisser le bruit sans effacer les lettres
img_blurred = cv.GaussianBlur(img_gray, (5, 5), 0)

# 4. LE SEUILLAGE ADAPTATIF (Pour éviter l'écran blanc d'Otsu !)
img_pret_pour_ocr = cv.adaptiveThreshold(
    img_blurred, 
    255, 
    cv.ADAPTIVE_THRESH_GAUSSIAN_C, 
    cv.THRESH_BINARY, 
    15, # Taille du bloc local (15x15 pixels)
    4   # Constante soustraite à la moyenne
)

# --- VÉRIFICATION VISUELLE ---
# Cette fois-ci, tu devrais voir ton texte en noir sur fond blanc !
cv.imshow("Image propre pour EasyOCR", img_pret_pour_ocr)
print("[INFO] Appuie sur n'importe quelle touche sur la fenêtre de l'image pour lancer l'OCR...")
cv.waitKey(0) 

# 5. RUN EASYOCR
print("\n[INFO] Initialisation d'EasyOCR...")
reader = easy.Reader(['fr', 'en'], gpu=False)

print("[INFO] Lecture des caractères...")
results = reader.readtext(img_pret_pour_ocr, detail=0)

print("\n--- RÉSULTATS D'EASYOCR ---")
for re in results:
    print(re)

cv.destroyAllWindows()