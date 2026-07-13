import cv2 as cv
import numpy as np
import easyocr as easy

chemin1_face=r"CIN_photos\WhatsApp Image 2026-07-11 at 21.58.54.jpeg"
img=cv.imread(chemin1_face)

"""
 verification that all is well done
if img is None:
    print(f" l'image ne peut etre lue, verifiez que le chemin {chemin1_face} est bien correcte")
else:
    print("tout va bien!")
 done with verification

"""

img_gray=cv.cvtColor(img,cv.COLOR_BGR2GRAY)

img_gray= cv.rotate(img_gray, cv.ROTATE_90_COUNTERCLOCKWISE)

#cv.imshow("face en gris", img_gray)

def resizeFonction(img, r=0.75):
   
   height,width= img.shape[:2]

   r_height=int(height*r)
   r_width= int(width *r)

   return cv.resize(img,(r_width,r_height),cv.INTER_AREA)

img_gray= resizeFonction(img_gray,0.75)

img_gray = cv.GaussianBlur(img_gray, (3, 3), 0)

_,img_gray = cv.threshold(img_gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

#cv.imshow("thres",img_gray)



reader = easy.Reader(['fr', 'en'], gpu=False)
results=reader.readtext(img_gray,detail=0)
for re in results:
   print(re)

# cv.waitKey(0)
# cv.destroyAllWindows()