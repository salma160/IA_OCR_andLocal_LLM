import cv2 as cv
import numpy as np

"""
1. la photo est-elle sombre?
2. la photo est-elle floue?
3. la photo est-elle bruitée?
4. la carte est -elle détectable?
5. la carte est-elle inclinée?
"""
#.1
#phase de récolte de données:
"""
list_images=[r"cinPhotosTests\WhatsApp Image 2026-07-14 at 18.06.13.jpeg",
r"cinPhotosTests\WhatsApp Image 2026-07-14 at 18.07.35.jpeg",r"cinPhotosTests\WhatsApp Image 2026-07-14 at 18.07.52.jpeg",r"cinPhotosTests\WhatsApp Image 2026-07-14 at 18.08.10.jpeg",r"cinPhotosTests\WhatsApp Image 2026-07-16 at 01.34.15.jpeg",r"cinPhotosTests\WhatsApp Image 2026-07-16 at 01.34.17.jpeg",r"cinPhotosTests\WhatsApp Image 2026-07-16 at 01.34.21.jpeg",r"cinPhotosTests\WhatsApp Image 2026-07-16 at 01.34.22.jpeg",r"cinPhotosTests\WhatsApp Image 2026-07-16 at 01.34.23.jpeg",r"cinPhotosTests\WhatsApp Image 2026-07-16 at 01.34.24.jpeg",r"cinPhotosTests\WhatsApp Image 2026-07-16 at 01.34.25.jpeg",r"cinPhotosTests\WhatsApp Image 2026-07-16 at 01.34.26.jpeg",r"cinPhotosTests\WhatsApp Image 2026-07-16 at 01.34.27.jpeg",r"cinPhotosTests\WhatsApp Image 2026-07-16 at 01.34.28.jpeg",r"cinPhotosTests\WhatsApp Image 2026-07-16 at 01.34.29.jpeg",r"cinPhotosTests\WhatsApp Image 2026-07-16 at 01.34.30.jpeg",r"cinPhotosTests\WhatsApp Image 2026-07-16 at 01.34.31.jpeg",r"cinPhotosTests\WhatsApp Image 2026-07-16 at 01.34.32.jpeg"]

for i, path in enumerate(list_images, start=1):
    img=cv.imread(path)
    img_gray=cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    mean,stddev=cv.meanStdDev(img_gray)
    print(f" voici la moyenne de l'image {i}: {mean}; et voici son std: {stddev}; et la variation de ses contours après laplacian:{np.var(cv.Laplacian(img_gray,cv.CV_64F))}")
while(True):
    True
"""



def analyser_img(img_gray):

    CLAHE = False

    BRIGHTNESS_THRES = 130
    CONTRAST_THRES = 28
    BLUR_THRES = 20

    # ---------- Luminosité ----------
    mean = np.mean(img_gray)

    if mean < BRIGHTNESS_THRES:
        clahe = cv.createCLAHE()
        img_gray = clahe.apply(img_gray)
        CLAHE = True

    # ---------- Contraste ----------
    stddev = np.std(img_gray)

    if stddev < CONTRAST_THRES:
        if not CLAHE:
            clahe = cv.createCLAHE()
            img_gray = clahe.apply(img_gray)
            CLAHE = True

    # ---------- Flou ----------
    img_laplacian = cv.Laplacian(img_gray, cv.CV_64F)
    var_contours = np.var(img_laplacian)

    if var_contours < BLUR_THRES:
        #BLUR = True
        print("Veuillez reprendre une photo plus nette de votre carte.")
        exit()

    return img_gray






