from paddleocr import PaddleOCR
import cv2 as cv

# On crée l'OCR UNE SEULE FOIS
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv5_server_det",
    text_recognition_model_name="PP-OCRv5_server_rec",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)


def ocr_paddle(img):
    if len(img.shape) == 2:
        img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    

# Agrandissement x2
    img = cv.resize(
    img,
    None,
    fx=2,
    fy=2,
    interpolation=cv.INTER_CUBIC
)
    result = ocr.predict(img)

    textes = result[0]["rec_texts"]
    scores = result[0]["rec_scores"]

    texte_final = ""

    for texte, score in zip(textes, scores):

        if score > 0.6 and texte.strip() != "":
            texte_final += texte + "\n"

    return texte_final