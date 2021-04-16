import sys
import compare as cmp

# read commandline arguments, first
fullCmdArguments = sys.argv

# - further arguments
filename = 'scan\\' + fullCmdArguments[1]

cmp.compare(filename,'mod')

