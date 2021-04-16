import os
import sys

import os.path
from os import path

import cv2
from scipy import ndimage


pjoin = os.path.join

root_dir = os.path.dirname(os.path.realpath(__file__))

sys.path.append(pjoin(root_dir,'process_scan','templates'))
sys.path.append(pjoin(root_dir, 'python_code'))
sys.path.append(pjoin(root_dir, 'Cyrilic_OCR'))

import zipfile
import filecmp

import subprocess
import shutil

# internal function for OCR
def ifun_ocr(file, rotate):

    pos1 = file.find('.')
    filename = file[:pos1]
    filename_txt = filename+'.txt'

    if rotate == "True":
        file_left = filename + '_left.tif'
        file_right = filename + '_right.tif'
        #path_left = pjoin('Cyrilic_OCR', 'scan', file_left)
        #path_right = pjoin('Cyrilic_OCR', 'scan', file_right)
        path_left = pjoin('scan', file_left)
        path_right = pjoin('scan', file_right)
        print (path_left + '\n')
        print (path_right + '\n')
        
        #original_scan = pjoin('Cyrilic_OCR', 'scan', file)
        original_scan = pjoin('scan', file)
        print (original_scan)

        sc_image = cv2.imread(original_scan)
        print (file + ' loaded\n')
        #rotation angle in degree
        rotated_p1 = ndimage.rotate(sc_image, 0.1, cval=255)
        rotated_n1 = ndimage.rotate(sc_image, -0.1, cval=255)
        print (file + ' rotated\n')

        cv2.imwrite(path_left, rotated_p1)
        cv2.imwrite(path_right, rotated_n1)
        print ('new img saved\n')

    os.system('python main.py '+file)

    original = pjoin('results', filename, filename_txt)
    target = pjoin('results', filename, filename+'_backup.txt')

    shutil.copyfile(original, target)
    
    if rotate == "True":
        os.system('python main.py '+file_left)
        os.system('python main.py '+file_right)
        
        pos1 = file_left.find('.')
        filename_left = file_left[:pos1]

        original = pjoin('results', filename_left, filename_left + '.txt')
        target = pjoin('results', filename, filename + '_left.txt')
        
        
        shutil.copyfile(original, target)
        pos1 = file_right.find('.')
        filename_right = file_right[:pos1]

        original = pjoin('results', filename_right, filename_right + '.txt')
        target = pjoin('results', filename, filename + '_right.txt')
        shutil.copyfile(original, target)
        shutil.rmtree(pjoin('results', filename_left))
        shutil.rmtree(pjoin('results', filename_right))

        os.system('python start_compare.py '+file)

   
    if rotate == "True":
        os.remove(path_left) 
        os.remove(path_right) 


# read commandline arguments, first
fullCmdArguments = sys.argv

# - further arguments
filename = fullCmdArguments[1]
if len(fullCmdArguments) == 3:
    rotate = fullCmdArguments[2]
else:
    rotate = "False"


ifun_ocr(filename, rotate)