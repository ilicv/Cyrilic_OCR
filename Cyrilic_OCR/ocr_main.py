import clean as cl
import words as wp
import extract_letters as el
import replace_letter as rl
import compare as cmp


import sys
import datetime
script_start = datetime.datetime.now()


def recognize(filename):
    fullCmdArguments = sys.argv

    #filename = 'scan\\' + fullCmdArguments[1]

    cl.clean_all()
    #####
    function_start = datetime.datetime.now()
    print ('started extract coordinates for: ' + filename, function_start)
    wp.get_words(filename)
    function_end = datetime.datetime.now()
    print ('completed extract coordinates for: ' + filename, function_start-function_end)

    #####
    function_start = datetime.datetime.now()
    print ('started extract_letters for: ' + filename, function_start)
    el.extract_letters(filename)
    function_end = datetime.datetime.now()
    print ('completed extract_letters for: ' + filename, function_start-function_end)

    #####
    function_start = datetime.datetime.now()
    print ('started replace_diacritics for: ' + filename, function_start)
    rl.replace_diacritics(filename)
    function_end = datetime.datetime.now()
    print ('completed replace_diacritics for: ' + filename, function_start-function_end)

    #####
    function_start = datetime.datetime.now()
    print ('started compare for: ' + filename, function_start)
    cmp.compare(filename, 'initial')
    function_end = datetime.datetime.now()
    print ('completed compare for: ' + filename, function_start-function_end)

    script_end = datetime.datetime.now()
    print ('completed OCR processing for: ' + filename, script_end-script_start)
