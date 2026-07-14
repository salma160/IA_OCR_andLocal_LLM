import cv2 as cv
import numpy as np
import easyocr as easy

path_image= r"CIN_photos\WhatsApp Image _2026-07-11 at 20.02.54.jpeg" 
img=cv.imread(path_image)
cv.namedWindow("my pipeline")
cv.createTrackbar("thres1","my pipeline", 95,255,lambda x:x)
cv.createTrackbar("thres2","my pipeline", 129,255,lambda x:x)

def resizefct(img,r=0.75):
    height,width=img.shape[:2]
    width=int(width*r)
    height=int(height*r)
    return cv.resize(img,(width,height))
img=resizefct(img,0.3)
norm_height,norm_width=img.shape[:2]

while True:
    th1=cv.getTrackbarPos("thres1","my pipeline")
    th2=cv.getTrackbarPos("thres2","my pipeline")
    img_gray=cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    img_original_gray = img_gray.copy()
    img_blur=cv.GaussianBlur(img_gray,(5,5),0)
    img_canny=cv.Canny(img_blur,th1,th2)
    img_canny=cv.dilate(img_canny,(3,3),1)
    img_canny=cv.erode(img_canny,(3,3),1)
    
    contours, _ = cv.findContours(img_canny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
   
    contours = sorted(contours, key=cv.contourArea, reverse=True)
    
    carte_contour = None
    
    for c in contours:
        
        perimetre = cv.arcLength(c, True)
        
        approx = cv.approxPolyDP(c, 0.02 * perimetre, True)
        
        
        if len(approx) == 4:
            carte_contour = approx
            break 
    # --- BLOC DE DIAGNOSTIC ---
    
    
    
    if carte_contour is not None:
        cv.drawContours(img_original_gray, [carte_contour], -1, 255, 3)
# display photos  
    cv.putText(img_original_gray, "Original", (20, 40), cv.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
    cv.putText(img_blur, "Gaussian Blur", (20, 40), cv.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
    cv.putText(img_canny, "Canny Edge", (20, 40), cv.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
    
   
    H_display = cv.hconcat([img_original_gray, img_blur, img_canny])
    cv.imshow("my pipeline",H_display)
    
    if (cv.waitKey(1)&0XFF ) == ord('a'):
        break

cv.destroyAllWindows()

if carte_contour is not None:
        # 1. On récupère les 4 points
        pts = carte_contour.reshape(4, 2).astype("float32")
        
        # --- TRI MATHEMATIQUE PAR ANGLE (INFAILLIBLE) ---
        # On calcule le centre de la carte (la moyenne des 4 points)
        centre = np.mean(pts, axis=0)
        
        # On calcule l'angle de chaque point par rapport au centre
        angles = np.arctan2(pts[:, 1] - centre[1], pts[:, 0] - centre[0])
        
        # On trie les points selon leurs angles (dans le sens des aiguilles d'une montre)
        # np.argsort nous donne l'ordre. On les réorganise.
        pts_tries = pts[np.argsort(angles)]
        
        # Avec arctan2, l'ordre obtenu est : Bas-Droite, Bas-Gauche, Haut-Gauche, Haut-Droite
        # On les remet dans l'ordre standard OpenCV : [HG, HD, BD, BG]
        rect = np.zeros((4, 2), dtype="float32")
        rect[0] = pts_tries[2]  # Haut-Gauche
        rect[1] = pts_tries[3]  # Haut-Droite
        rect[2] = pts_tries[0]  # Bas-Droite
        rect[3] = pts_tries[1]  # Bas-Gauche
        # ------------------------------------------------a
        
        # 2. Définir la cible PARFAITE (Ordre standard : HG, HD, BD, BG)
        dst = np.array([
            [0, 0],                               # Haut-Gauche
            [norm_width - 1, 0],                  # Haut-Droite
            [norm_width - 1, norm_height - 1],     # Bas-Droite
            [0, norm_height - 1]                  # Bas-Gauche
        ], dtype="float32")

        # 3. Calcul de la matrice et transformation
        M = cv.getPerspectiveTransform(rect, dst)
        carte_redressee = cv.warpPerspective(img_gray, M, (norm_width, norm_height))
        
        # 4. Affichage
        cv.namedWindow("Carte Redressee (Prete pour OCR)", cv.WINDOW_NORMAL)
        cv.resizeWindow("Carte Redressee (Prete pour OCR)", 500, 315)
        cv.imshow("Carte Redressee (Prete pour OCR)", carte_redressee)
cv.waitKey(0)
cv.destroyWindow("Carte Redressee (Prete pour OCR)")