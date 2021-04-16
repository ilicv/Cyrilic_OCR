import glob, os, os.path

def clean_dir(mydir):
    filelist = glob.glob(os.path.join(mydir, "*.*"))
    for f in filelist:
        os.remove(f)

def remove_file(filename):
    if os.path.isfile(filename):
        os.remove(filename)

def clean_all():
    clean_dir('letters')
    clean_dir('lines')
    clean_dir('paragraph')
    clean_dir('training')
    clean_dir('words')

    remove_file('letters1.txt')
    remove_file('letters_select.jpg')
    remove_file('letters2.txt')
    remove_file('select.jpg')
    remove_file('word_output.txt')
    remove_file('plain.txt')
    remove_file('letters.txt')
    remove_file('compare.txt')

#clean_all()



