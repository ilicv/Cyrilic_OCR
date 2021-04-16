from os import path
import os 
pjoin = os.path.join

root_dir = os.path.dirname(os.path.realpath(__file__))
import Cyrilic_OCR.ocr_main as om


om.recognize(pjoin('scan', 'Dubrovnik0001_crop.tif'))