# -*- coding: utf-8 -*-
import codecs
import os
from difflib import SequenceMatcher

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



def compare(filename, report_type):
    p1 = filename.find('\\')
    p2 = filename.find('.')
    result_folder='results\\'+filename[(p1+1):p2]+'\\'
    expected_file='expected\\'+filename[(p1+1):p2]+'.txt'
    filename_txt = filename[(p1+1):p2]+'.txt'

    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    print (expected_file)
    if os.path.exists(expected_file):
        print ('compare expected text with OCR result for: '+ filename)
        expected = []
        predicted = []
        with codecs.open(expected_file, encoding='utf-8') as f:
            for line in f:
                expected.append(line.strip('\n'))

        with codecs.open(result_folder+filename_txt, encoding='utf-8') as f:
            for line in f:
                predicted.append(line.strip('\n'))

        diacritics_on_page = 0
        for d in range(len(diacritics_list)):
            for line in expected:
                diacritics_on_page = diacritics_on_page + line.count(diacritics_list[d])



        word_cnt = 0
        dif_cnt = 0
        expected_chars = 0
        diacritics_error = 0

        if report_type == 'initial':
            report_file = result_folder+'report.txt'
        if report_type == 'mod':
            report_file = result_folder+'report_mod.txt'

        with codecs.open(report_file, "w", encoding="utf-8") as f:
            cnt_pred_lines = 0
            cnt_exp_lines = 0

            for cnt in range(len(expected)):
                expected_chars = expected_chars + len(expected[cnt])

                #sync lines
                if  (cnt_pred_lines)> (len(predicted)-1):
                    cnt_pred_lines = len(predicted)-1
                if  (cnt_exp_lines)> (len(expected)-1):
                    cnt_exp_lines = len(expected)-1
                    
                check_next = 0
                if ((cnt_exp_lines+1)< len(expected)) and ((cnt_pred_lines+1)< len(predicted)):
                    check_next = similar(expected[cnt_exp_lines + 1].lower(), predicted[cnt_pred_lines + 1].lower())

                sim_current_line = similar(expected[cnt_exp_lines].lower(), predicted[cnt_pred_lines].lower())
                pred_next_line = 0
                if  ((cnt_pred_lines+1)< len(predicted)):
                    pred_next_line = similar(expected[cnt_exp_lines].lower(), predicted[cnt_pred_lines+1].lower())
                rot_next_line = 0
                if ((cnt_exp_lines+1)< len(expected)):
                    rot_next_line = similar(expected[cnt_exp_lines+1].lower(), predicted[cnt_pred_lines].lower())

                # check if next two lines are different 
                if  (sim_current_line < rot_next_line) and (rot_next_line>0.7) and (check_next <0.7):
                    cnt_exp_lines = cnt_exp_lines + 1

                if  (sim_current_line < pred_next_line) and (rot_next_line>0.7) and (check_next <0.7):
                    cnt_pred_lines = cnt_pred_lines + 1
                #sync lines

                expected_words = str.split(expected[cnt_exp_lines])
                predicted_words = str.split(predicted[cnt_pred_lines])

                rl = len(expected_words)
                if rl > len(predicted_words):
                    rl = len(predicted_words)

                c1_e = 0
                c1_p = 0
                for c1 in range(rl):

                    if (c1_e<len(expected_words)) and (c1_e<len(predicted_words)) and (c1_p<len(expected_words)) and (c1_p<len(predicted_words)):
                        expected_words[c1_e] = expected_words[c1_e].translate({ord(i): ' ' for i in ignore_chars})
                        predicted_words[c1_p] = predicted_words[c1_p].translate({ord(i): ' ' for i in ignore_chars})

                        expected_words[c1_e] = tras_latin_cyr(expected_words[c1_e])
                        predicted_words[c1_p] = tras_latin_cyr(predicted_words[c1_p])

                        if expected_words[c1_e] != predicted_words[c1_p]:
                            expected_words_without_d = remove_diacritics(expected_words[c1_e])
                            predicted_words_without_d = remove_diacritics(predicted_words[c1_e])

                            #print ('!!!!!')
                            #print (expected_words[c1_e])
                            #print (expected_words_without_d)
                            #print (predicted_words[c1_e])
                            #print (predicted_words_without_d)
                            if expected_words_without_d == predicted_words_without_d:
                                diacritics_error = diacritics_error + 1
                                #print("ERROR IN diacritics!!!!!!!!!\n")
                                f.write("ERROR IN diacritics!!!!!!!!!\n")
                            #print ('!!!!!')
                            
                            not_missing = True
                            f.write("%s" % 'line: ' + str(cnt+1) + '  word:'+ str(c1_e) +'\n')
                            
                            if (c1_e + 1) < len(range(rl)):
                                sim_current= similar(expected_words[c1_e].lower(), predicted_words[c1_p].lower())
                                sim_next_exp = similar(expected_words[c1_e + 1].lower(), predicted_words[c1_p].lower())

                                check_next = 0
                                if (c1_p+1)< len(range(rl)):
                                    check_next = similar(expected_words[c1_e + 1].lower(), predicted_words[c1_p + 1].lower())
                                if  (sim_current < sim_next_exp) and (sim_next_exp>0.7) and (check_next <0.7):
                                    f.write("%s" % expected_words +'\n')
                                    f.write("%s" % predicted_words +'\n')
                                    f.write("missing expected word: %s" % expected_words[c1] +'\n')
                                    c1_e = c1_e + 1
                                    not_missing = False
                            if (not_missing) and ((c1_p + 1) < len(range(rl))):
                                sim_current= similar(expected_words[c1_e].lower(), predicted_words[c1_p].lower())
                                sim_next = similar(expected_words[c1_e].lower(), predicted_words[c1_p + 1].lower())

                                check_next = 0
                                if ((c1_e + 1) < len(range(rl))):
                                    check_next = similar(expected_words[c1_e + 1].lower(), predicted_words[c1_p + 1].lower())
                                
                                if (sim_current < sim_next) and (sim_next>0.7) and (check_next <0.7):
                                    f.write("%s" % expected_words +'\n')
                                    f.write("%s" % predicted_words +'\n')
                                    f.write("not needed predicted word: %s" % predicted_words[c1_p] +'\n')
                                    c1_p = c1_p + 1
                                    not_missing = False
                                
                            if not_missing:
                                f.write("%s" % expected_words[c1_e] +'\n')
                                f.write("%s" % predicted_words[c1_p] +'\n')
                                dif_cnt = dif_cnt + 1
                            f.write("%s" % '-----------------------------' +'\n')
                        c1_e = c1_e + 1
                        c1_p = c1_p + 1
                        word_cnt = word_cnt + 1
                cnt_pred_lines = cnt_pred_lines + 1
                cnt_exp_lines = cnt_exp_lines + 1

            f.write("%s" % ('karaktera: ' + str(expected_chars)) + '   razlika: ' +  str(dif_cnt) + '  dijakritika: '+str(diacritics_on_page)+ '  diacritics_error:  '+str(diacritics_error)+'\n')

#compare('JuznaSrbija0051_crop.tif', 'initial')