import clean as cl
import words as wp
import extract_letters as el
import replace_letter as rl
import compare as cmp


import sys
import datetime
script_start = datetime.datetime.now()


#filename = 'scan\\Jablanica0096_crop.tif'

#filename = 'scan\\paragraph_635.tif'
#filename = 'scan\\problem_italic.tif'
#filename = 'scan\\paragraph_265.tif'
#filename = 'scan\\test1.tif'

#filename = 'scan\\Dubrovnik0018_crop.tif'
#filename = 'scan\\Jablanica0096_crop.tif'
#filename = 'scan\\JuznaSrbija0052_crop.tif'
#filename = 'scan\\Piva0015_crop.tif'
#filename = 'scan\\Proscenje0064_crop.tif'

#filename = 'scan\\Uskoci0080_crop.tif'
#filename = 'scan\\Vasojevici0033_crop.tif'

#filename = 'scan\\line_165.tif'
#filename = 'scan\\line_177.tif'
filename = 'scan\\Vasojevici0033_crop.tif'



cl.clean_all()
wp.get_words(filename)
el.extract_letters(filename)

rl.replace_diacritics(filename)
cmp.compare(filename, 'initial')

script_end = datetime.datetime.now()
print (script_end-script_start)
