import sys
import compare_ocr_res as cmp

# read commandline arguments, first
fullCmdArguments = sys.argv

# - further arguments
filename = 'scan\\' + fullCmdArguments[1]

cmp.compare(filename,'_left')
cmp.compare(filename,'_right')

