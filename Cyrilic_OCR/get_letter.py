import codecs

lines=[]
with codecs.open("insert_letters.txt", encoding="utf-8") as f:
    for line in f:
        text = line.strip('\n')
        lines.append(text)

def get_letter(letter,y):
    letter_with_d = ''
    letter_fnd = 'nf'
    for line in lines:
        s = line.split(',')
        if s[0] == letter:
            letter_with_d = s
    if letter_with_d != '':
        letter_fnd = letter_with_d[y]
    return letter_fnd
#get_letter('a',5)