import pytesseract
import cv2
from pytesseract import Output
from PIL import Image
import PIL as PIL

import recognize as rc
print ('start')
def test(scan, filename):
    p1 = scan.find('\\')
    p2 = scan.find('.')
    result_folder='results\\'+filename[(p1+1):p2]+'\\'
    expected_file='expected\\'+filename[(p1+1):p2]+'.txt'


    imgs_dir = 'results\\'+scan+'\\letters\\'
    img_path = imgs_dir + filename
    print (img_path)
    img = Image.open(img_path)
    ocr_letter = pytesseract.image_to_string(img,lang='srp', config='--psm 10')
    print (ocr_letter)

    res = rc.recognize(img_path)



    print (res)
    print ('end')

test('Vasojevici0034_crop', 'letter00006.bmp')

