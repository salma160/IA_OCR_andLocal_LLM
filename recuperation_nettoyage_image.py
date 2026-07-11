import cv2 as cv
import numpy as np

chemin1_face=r"CIN_photos\WhatsApp Image _2026-07-11 at 20.02.54.jpeg"
img=cv.imread(chemin1_face)

"""
 verification that all is well done
if img is None:
    print(f" l'image ne peut etre lue, verifiez que le chemin {chemin1_face} est bien correcte")
else:
    print("tout va bien!")
 done with verification

"""
# cv.imshow("face cin en origin",img)

img=cv.cvtColor(img,cv.COLOR_BGR2GRAY)
cv.imshow("face en gris", img)

def resizeFonction(img, r=0.75):
   
   height,width= img.shape[:2]

   r_height=int(height*r)
   r_width= int(width *r)

   return cv.resize(img,(r_width,r_height),cv.INTER_AREA)

img_smaller= resizeFonction(img,0.5)
cv.imshow("face_reduite",img_smaller)



cv.waitKey(0)
cv.destroyAllWindows()