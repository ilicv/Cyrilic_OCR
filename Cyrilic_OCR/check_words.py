import codecs
import ltr_coordinate as ltc

def check_crd(crd_list, avr_let_width, avr_let_height):
    wrd_cnt = 0
    prev_word = ''
    
    c_let_word = ''
    c_ocr_word = ''

    word_beg = 0
    word_end = 0

    for i in range(len(crd_list)):
        crd = crd_list[i]
        if prev_word != '':
            if crd.found_in != prev_word:
                #print (prev_word.lower())
                #print (c_let_word.lower())
                #print (c_ocr_word.lower())
                wrd_cnt = 0
                c_let_word = ''
                c_ocr_word = ''
                #exit()
                word_end = i
                #print (word_beg,',',word_end)
                word_beg = i 
                #print ('-----')
        if wrd_cnt<len(crd.found_in):
            crd.pos_in_word = wrd_cnt
            crd.letter = crd.found_in[wrd_cnt]
            #if 0:
            #    print ('-----')
            #    print (crd.found_in)
            #    print (wrd_cnt)
            #    print (crd.letter, crd.ocr_letter)
            #    print (crd.img_name)
            
            c_let_word = c_let_word + crd.letter
            c_ocr_word = c_ocr_word + crd.ocr_letter

        wrd_cnt = wrd_cnt + 1
        prev_word = crd.found_in

    avr_let_width3 = avr_let_width
    avr_let_height3 = avr_let_height

    return crd_list

def check_crd_range(crd_list, rbeg, rend):
    wrd_cnt = 0
    prev_word = ''

    c_let_word = ''
    c_ocr_word = ''

    word_beg = 0
    word_end = 0

    similarity_idx = 0

    for i in range(rbeg, rend):
        crd = crd_list[i]
        if (i > rbeg) and (i < rend-1):
            p_crd = crd_list[i-1]
            n_crd = crd_list[i+1]
            if ((n_crd.x1-p_crd.x2)>-200) and ((n_crd.x1-p_crd.x2)<5) and ((n_crd.y1-p_crd.y1)<10):
                inside = True

            overlap_next=(crd.x2-n_crd.x1)/(crd.x2-crd.x1)

            if (overlap_next>0.7) and ((n_crd.y1-p_crd.y1)<10):
                inside = True

            overlap_prev=(p_crd.x2-crd.x1)/(crd.x2-crd.x1)
            if (overlap_prev>0.7) and ((n_crd.y1-p_crd.y1)<10):
                inside = True
                #print ('overlap 3')

        if prev_word != '':
            if crd.found_in != prev_word:
                #print (prev_word.lower())
                #print (c_let_word.lower())
                #print (c_ocr_word.lower())
                #print ('-----')
                wrd_cnt = 0
                c_let_word = ''
                c_ocr_word = ''
                #exit()
                word_end = i-1
                #print (word_beg,',',word_end)
                word_beg = i
        if wrd_cnt<len(crd.found_in):
            crd.pos_in_word = wrd_cnt
            if 1:
                #print ('-----')
                #print (crd.found_in)
                #print (wrd_cnt)
                #print (crd.letter, crd.ocr_letter)
                
                if crd.letter.lower() == crd.ocr_letter.lower():
                    similarity_idx = similarity_idx + 1

                #print (crd.img_name)
            c_let_word = c_let_word + crd.letter
            c_ocr_word = c_ocr_word + crd.ocr_letter

        wrd_cnt = wrd_cnt + 1
        prev_word = crd.found_in

    #print ('similarity_idx: ' + str(similarity_idx))
    return crd_list

def check_words(filename):
    p1 = filename.find('\\')
    p2 = filename.find('.')
    result_folder='results\\'+filename[(p1+1):p2]+'\\'
    crd_list = []

    with codecs.open(result_folder+'letters_coordinates.txt', encoding='utf-8') as f:
        for line in f:
            crd = ltc.coordinate()
            crd_str = line.strip('\n')
            crd.load_from_str(crd_str)
            crd_list.append(crd)

    return crd_list

#crd_list = check_words('Dubrovnik0018_crop.tif')
#check_crd_range(crd_list, 67, 76)

#print ("complete")
