import clean as cl
import words as wp
import extract_letters as el
import replace_letter as rl
import compare as cmp


import sys
import datetime
script_start = datetime.datetime.now()
print (script_start)


# read commandline arguments, first
fullCmdArguments = sys.argv

# - further arguments
filename = 'scan\\' + fullCmdArguments[1]



cl.clean_all()
wp.get_words(filename)
el.extract_letters(filename)

rl.replace_diacritics(filename)
cmp.compare(filename, 'initial')

script_end = datetime.datetime.now()
print (script_end-script_start)
