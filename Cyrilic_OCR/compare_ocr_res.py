# -*- coding: utf-8 -*-
import codecs
import os
from difflib import SequenceMatcher
pjoin = os.path.join
import shutil


def get_tag(line_line, tag):
    res = ''
    tag_beg = '<'+tag+'>'
    tag_end = '</'+tag+'>'
    p1 = line_line.find(tag_beg) 
    p2 = line_line.find(tag_end)
    if (p1>1) or (p2>p1):
        res = line_line[(p1+len(tag_beg)):p2]
    return (res)


def set_tag(tag, value):
    res = ''
    tag_beg = '<'+tag+'>'
    tag_end = '</'+tag+'>'
    res = tag_beg + value + tag_end
    return (res)


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

with codecs.open('ignore_chars.txt', encoding='utf-8') as f:
    for line in f:
        ignore_chars = line.strip('\n')

with codecs.open('diacritics_list.txt', encoding='utf-8') as f:
    for line in f:
        diacritics_list = line.strip('\n')
        
latin_cyr = []
with codecs.open('latin_cyr.txt', encoding='utf-8') as f:
    for line in f:
        latin_cyr.append(line)
cyr_latin = []
with codecs.open('cyr_latin.txt', encoding='utf-8') as f:
    for line in f:
        cyr_latin.append(line)

def tras_latin_cyr(text):
    tr = {ord(a):ord(b) for a, b in zip(*latin_cyr)}

    tr = dict( [ (ord(a), ord(b)) for (a, b) in zip(*latin_cyr) ] )
    return text.translate(tr)

def tras_cyr_latin(text):
    tr = {ord(a):ord(b) for a, b in zip(*latin_cyr)}

    tr = dict( [ (ord(a), ord(b)) for (a, b) in zip(*cyr_latin) ] )
    return text.translate(tr)


def remove_diacritics(word):
    for d in range(len(diacritics_list)):
        word = word.replace(diacritics_list[d],'')
        
        
    diacritics_in_word = 0
    for d in range(len(diacritics_list)):
        diacritics_in_word = diacritics_in_word + word.count(diacritics_list[d])
    if (diacritics_in_word) >0:
        print ('error')
        exit()

    return(word)



def compare(filename, rotated_ocr):
    p1 = filename.find('\\')
    p2 = filename.find('.')
    result_folder='results\\'+filename[(p1+1):p2]+'\\'
    #rotated_file='results\\'+filename[(p1+1):p2]+rotated_ocr+'\\plain_modified.txt'
    rotated_file='results\\' + filename[(p1+1):p2] + '\\'+ filename[(p1+1):p2] + rotated_ocr + '.txt'
    print(rotated_file)
    filename_txt = filename[(p1+1):p2]+'.txt'

    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    currentDirectory = os.getcwd()
    rotated_file = pjoin(currentDirectory, rotated_file)
    print (rotated_file)
    if os.path.exists(rotated_file):
        print ('compare rotated text with OCR result for:' + filename)
        rotated = []
        predicted = []
        with codecs.open(rotated_file, encoding='utf-8') as f:
            for line in f:
                rotated.append(line.strip('\n'))
        print (pjoin(currentDirectory,result_folder,filename_txt))
        with codecs.open(pjoin(currentDirectory,result_folder,filename_txt), encoding='utf-8') as f:
            for line in f:
                str_line = line.replace('\n', '')
                str_line = str_line.replace(chr(13), '')
                predicted.append(str_line)

        diacritics_on_page = 0
        for d in range(len(diacritics_list)):
            for line in rotated:
                diacritics_on_page = diacritics_on_page + line.count(diacritics_list[d])



        word_cnt = 0
        dif_cnt = 0
        rotated_chars = 0
        diacritics_error = 0

        list_max_lines = len(rotated)
        if len(predicted)<len(rotated):
            list_max_lines = len(predicted)

        with codecs.open(result_folder+'report'+rotated_ocr+'.txt', "w", encoding="utf-8") as f:
            cnt_pred_lines = 0
            cnt_rot_lines = 0

            for cnt in range(list_max_lines):
                rotated_chars = rotated_chars + len(rotated[cnt])

                #sync lines
                if  (cnt_pred_lines)> (len(predicted)-1):
                    cnt_pred_lines = len(predicted)-1
                if  (cnt_rot_lines)> (len(rotated)-1):
                    cnt_rot_lines = len(rotated)-1

                check_next = 0
                if ((cnt_rot_lines+1)< len(rotated)) and ((cnt_pred_lines+1)< len(predicted)):
                    check_next = similar(rotated[cnt_rot_lines + 1].lower(), predicted[cnt_pred_lines + 1].lower())

                sim_current_line = similar(rotated[cnt_rot_lines].lower(), predicted[cnt_pred_lines].lower())
                pred_next_line = 0
                if  ((cnt_pred_lines+1)< len(predicted)):
                    pred_next_line = similar(rotated[cnt_rot_lines].lower(), predicted[cnt_pred_lines+1].lower())
                rot_next_line = 0
                if ((cnt_rot_lines+1)< len(rotated)):
                    rot_next_line = similar(rotated[cnt_rot_lines+1].lower(), predicted[cnt_pred_lines].lower())

                found_line = False
                # check if next two lines are different 
                if  (sim_current_line < rot_next_line) and (rot_next_line>0.7) and (check_next <0.7)and(len(predicted[cnt_pred_lines])>0) and (found_line == False):
                    cnt_rot_lines = cnt_rot_lines + 1

                if  (sim_current_line < pred_next_line) and (rot_next_line>0.7) and (check_next <0.7)and(len(rotated[cnt_rot_lines])>0) and (found_line == False):
                    cnt_pred_lines = cnt_pred_lines + 1
                    
                #print (cnt, cnt_pred_lines, cnt_rot_lines)
                if (sim_current_line <0.1) and (check_next <0.7):

                    correct_rot = 0
                    correct_pred = 0
                    most_similar_rot = 0
                    most_similar_pred = 0
                    for lin_x in range(2,6):

                        if  len(predicted[cnt_pred_lines])>0:
                            if ((cnt_rot_lines+lin_x)< len(rotated)):
                                rot_next_line = similar(rotated[cnt_rot_lines+lin_x].lower(), predicted[cnt_pred_lines].lower())
                                if most_similar_rot < rot_next_line:
                                    most_similar_rot = rot_next_line
                                    correct_rot = lin_x

                        if  len(rotated[cnt_rot_lines])>0:
                            if  ((cnt_pred_lines+lin_x)< len(predicted)):
                                pred_next_line = similar(rotated[cnt_rot_lines].lower(), predicted[cnt_pred_lines+lin_x].lower())
                                if most_similar_pred < pred_next_line:
                                    most_similar_pred = pred_next_line
                                    correct_pred = lin_x

                    cnt_pred_lines=cnt_pred_lines+correct_pred
                    cnt_rot_lines=cnt_rot_lines+correct_rot
                #sync lines

                rotated_words = str.split(rotated[cnt_rot_lines])
                predicted_words = str.split(predicted[cnt_pred_lines])

                rl = len(rotated_words)
                if rl > len(predicted_words):
                    rl = len(predicted_words)

                c1_r = 0
                c1_p = 0
                if (cnt_pred_lines< list_max_lines) and (cnt_rot_lines< list_max_lines):
                    for c1 in range(rl):

                        if (c1_r<len(rotated_words)) and (c1_r<len(predicted_words)) and (c1_p<len(rotated_words)) and (c1_p<len(predicted_words)):
                            #rotated_words[c1_r] = rotated_words[c1_r].translate({ord(i): ' ' for i in ignore_chars})
                            #predicted_words[c1_p] = predicted_words[c1_p].translate({ord(i): ' ' for i in ignore_chars})

                            #rotated_words[c1_r] = tras_latin_cyr(rotated_words[c1_r])
                            #predicted_words[c1_p] = tras_latin_cyr(predicted_words[c1_p])

                            rline = ''

                            if rotated_words[c1_r] != predicted_words[c1_p]:
                                rotated_words_without_d = remove_diacritics(rotated_words[c1_r])
                                predicted_words_without_d = remove_diacritics(predicted_words[c1_r])


                                if rotated_words_without_d == predicted_words_without_d:
                                    diacritics_error = diacritics_error + 1
                                    #print("ERROR IN diacritics!!!!!!!!!\n")
                                    #f.write("ERROR IN diacritics!!!!!!!!!\n")
                                #print ('!!!!!')

                                not_missing = True

                                p_word_beg = 0
                                if c1_p>0:
                                    for w_idx in range(0,c1_p):
                                        p_word_beg = p_word_beg + len(predicted_words[w_idx]) + 1

                                p_word_end = len(predicted_words[0])
                                if c1_p>0:
                                    p_word_end = 0
                                    for w_idx in range(0,c1_p+1):
                                        p_word_end = p_word_end + len(predicted_words[w_idx]) + 1

                                r_word_beg = 0
                                if c1_r>0:
                                    for w_idx in range(0,c1_r):
                                        r_word_beg = r_word_beg + len(rotated_words[w_idx]) + 1

                                r_word_end = len(rotated_words[0])
                                if c1_r>0:
                                    r_word_end = 0
                                    for w_idx in range(0,c1_r+1):
                                        r_word_end = r_word_end + len(rotated_words[w_idx]) + 1

                                #rline = rline + set_tag('line_num', str(cnt))+set_tag('word_pos', str(c1_r))
                                #rline = rline + set_tag('predicted', predicted[cnt])+set_tag('rotated', rotated[cnt])
                                rline = rline + set_tag('line_num', str(cnt_pred_lines))+set_tag('word_pos', str(c1_r))
                                rline = rline + set_tag('predicted', predicted[cnt_pred_lines])+set_tag('rotated', rotated[cnt_rot_lines])

                                if (c1_r + 1) < len(range(rl)):
                                    sim_current= similar(rotated_words[c1_r].lower(), predicted_words[c1_p].lower())
                                    sim_next_exp = similar(rotated_words[c1_r + 1].lower(), predicted_words[c1_p].lower())

                                    check_next = 0
                                    if (c1_p+1)< len(range(rl)):
                                        check_next = similar(rotated_words[c1_r + 1].lower(), predicted_words[c1_p + 1].lower())
                                    if  (sim_current < sim_next_exp) and (sim_next_exp>0.7) and (check_next <0.7):
                                        rline = rline + set_tag('missing_rotated', rotated_words[c1])
                                        rline = rline + set_tag('r_word_beg', str(r_word_beg))+set_tag('r_word_end', str(r_word_end))
                                        c1_r = c1_r + 1
                                        not_missing = False
                                if (not_missing) and ((c1_p + 1) < len(range(rl))):
                                    sim_current= similar(rotated_words[c1_r].lower(), predicted_words[c1_p].lower())
                                    sim_next = similar(rotated_words[c1_r].lower(), predicted_words[c1_p + 1].lower())

                                    check_next = 0
                                    if ((c1_r + 1) < len(range(rl))):
                                        check_next = similar(rotated_words[c1_r + 1].lower(), predicted_words[c1_p + 1].lower())

                                    if (sim_current < sim_next) and (sim_next>0.7) and (check_next <0.7):
                                        rline = rline + set_tag('missing_pred', predicted_words[c1])
                                        rline = rline + set_tag('p_word_beg', str(p_word_beg))+set_tag('p_word_end', str(p_word_end))
                                        c1_p = c1_p + 1
                                        not_missing = False

                                if not_missing:

                                    rline = rline + set_tag('pred_word', predicted_words[c1_p])+set_tag('rotated_word', rotated_words[c1_r])
                                    rline = rline + set_tag('p_word_beg', str(p_word_beg))+set_tag('p_word_end', str(p_word_end))
                                    rline = rline + set_tag('r_word_beg', str(r_word_beg))+set_tag('r_word_end', str(r_word_end))

                                    dif_cnt = dif_cnt + 1
                                f.write(rline+'\n')
                            c1_r = c1_r + 1
                            c1_p = c1_p + 1
                            word_cnt = word_cnt + 1

                cnt_pred_lines = cnt_pred_lines + 1
                cnt_rot_lines = cnt_rot_lines + 1

            #f.write("%s" % ('karaktera: ' + str(rotated_chars)) + '   razlika: ' +  str(dif_cnt) + '  dijakritika: '+str(diacritics_on_page)+ '  diacritics_error:  '+str(diacritics_error)+'\n')
            print('done ' + filename)


#compare('\Dubrovnik0018_crop.tif','_rn01')
#compare('\Dubrovnik0018_crop.tif','_left')
#compare('\Dubrovnik0019_crop.tif','_right')
