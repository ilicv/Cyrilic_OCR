import codecs
import ltr_coordinate as ltc
import numpy as np
import os


ins_letters=[]
plain_txt =[]
crd_list = []
lines_inserted_letters = np.zeros(5000, dtype=int)

with codecs.open("insert_letters.txt", encoding="utf-8") as f:
    for line in f:
        text = line.strip('\n')
        ins_letters.append(text)


def get_letter(crd):
    letter_fnd = 'nf'

    if (crd.diacritic != 16) and (crd.diacritic != 316)and (crd.diacritic != 22)and (crd.diacritic != 23)and (crd.diacritic != 24)and (crd.diacritic != 25):
        letter_with_d = ''
        bottom = ''

        if (crd.diacritic == 1302) or (crd.diacritic == 1303) or (crd.diacritic == 1304) or (crd.diacritic == 1305) or (crd.diacritic == 1306):
            bottom = ins_letters[0].split(',')
            bottom = bottom[13][1]
            if (crd.diacritic == 1302):
                crd.diacritic = 2
            if (crd.diacritic == 1303):
                crd.diacritic = 3
            if (crd.diacritic == 1304):
                crd.diacritic = 4
            if (crd.diacritic == 1305):
                crd.diacritic = 5
            if (crd.diacritic == 1306):
                crd.diacritic = 6
            if (crd.diacritic == 1307):
                crd.diacritic = 7

        # small cases
        for line in ins_letters:
            s = line.split(',')
            if s[0] == crd.letter:
                letter_with_d = s
        if letter_with_d != '':
            #print(letter_with_d)
            #print(crd.diacritic)
            #print(letter_with_d[crd.diacritic])
            letter_fnd = letter_with_d[crd.diacritic] + bottom

        #check upper cases
        if letter_fnd=='nf':
            #check upper case
            for line in ins_letters:
                s = line.split(',')
                if s[0].upper() == crd.letter:
                    letter_with_d = s
            if letter_with_d != '':
                letter_fnd = letter_with_d[crd.diacritic].upper() + bottom

    else:
        # letter u
        if crd.diacritic == 16:
            line = ins_letters[5]
            s = line.split(',')
            letter_fnd = s[0]

        # letter u"
        if crd.diacritic == 316:
            line = ins_letters[5]
            s = line.split(',')
            letter_fnd = s[3]

        # letter sh
        if crd.diacritic == 22:
            line = ins_letters[10]
            s = line.split(',')
            letter_fnd = s[0]

        # letter p
        if crd.diacritic == 23:
            line = ins_letters[11]
            s = line.split(',')
            letter_fnd = s[0]

        # letter g
        if crd.diacritic == 24:
            line = ins_letters[16]
            s = line.split(',')
            letter_fnd = s[0]
            
        # letter v
        if crd.diacritic == 25:
            line = ins_letters[17]
            s = line.split(',')
            letter_fnd = s[0]

        #print (ins_letters[17])
    return letter_fnd


def replace_letter(line, position, new_letter):
    beg = line[:position]
    end = line[(position+1):]
    new_line = beg + new_letter + end
    return new_line


def replace_diacritics(filename):
    p1 = filename.find('\\')
    p2 = filename.find('.')
    result_folder='results\\'+filename[(p1+1):p2]+'\\'
    filename_txt = filename[(p1+1):p2]+'.txt'

    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    with codecs.open(result_folder+'letters_coordinates.txt', encoding='utf-8') as f:
        for line in f:
            crd = ltc.coordinate()
            crd_str = line.strip('\n')
            crd.load_from_str(crd_str)
            crd_list.append(crd)

    with codecs.open(result_folder+'plain.txt', encoding='utf-8') as f:
        for line in f:
            plain_txt.append(line.strip('\n'))

    prev_word = ""
    letter_pos = 0
    for crd in crd_list:
        if prev_word != crd.found_in:
            letter_pos = 0
            prev_word = crd.found_in

        # replace superscript J
        if (crd.superscript == 1) and (ord(crd.letter)==1112):

            new_letter = chr(690)

            new = replace_letter(crd.found_in, letter_pos, new_letter)
            #print (crd.letter + " - " + str(letter_pos) + " - " + str(crd.diacritic) + ' >> insert_pos:' + str(crd.insert_position) + ' ,,' + crd.found_in + ',,' + new + ',,' + str(len(new_letter)) )

            line_pos = crd.ip_line_pos
            word_pos = crd.ip_word_pos

            if (line_pos>-1) and (new_letter !='nf'):
                lpos = word_pos + letter_pos + lines_inserted_letters[line_pos]
                new_line = replace_letter(plain_txt[line_pos], lpos, new_letter)
                lines_inserted_letters[line_pos] = lines_inserted_letters[line_pos] + (len(new_letter) - 1)
                plain_txt[line_pos] = new_line

        # replace letters with diacritics
        if crd.diacritic > 0:
            new_letter = get_letter(crd)

            new = replace_letter(crd.found_in, letter_pos, new_letter)
            #print (crd.letter + " - " + str(letter_pos) + " - " + str(crd.diacritic) + ' >> insert_pos:' + str(crd.insert_position) + ' ,,' + crd.found_in + ',,' + new + ',,' + str(len(new_letter)) )

            line_pos = crd.ip_line_pos
            word_pos = crd.ip_word_pos


            if (line_pos>-1) and (new_letter !='nf'):
                lpos = word_pos + letter_pos + lines_inserted_letters[line_pos]
                new_line = replace_letter(plain_txt[line_pos], lpos, new_letter)
                lines_inserted_letters[line_pos] = lines_inserted_letters[line_pos] + (len(new_letter) - 1)
                plain_txt[line_pos] = new_line

        letter_pos = letter_pos + 1

    with codecs.open(result_folder+filename_txt, "w", encoding="utf-8") as f:
        for line in plain_txt:
            f.write("%s" % line+'\n')

#replace_diacritics('scan\\'+'Dubrovnik0019_small2.tif')
