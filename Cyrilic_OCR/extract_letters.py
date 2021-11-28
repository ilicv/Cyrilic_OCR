import pytesseract
import cv2
from pytesseract import Output
import codecs
from shutil import copyfile
import recognize as rc
import recognize_connected as rc_con
import get_letter as gl

import ltr_coordinate as ltc
import os


def get_tag(tag, line):
    res = ''
    tag_beg = '<'+tag+'>'
    tag_end = '</'+tag+'>'
    p1 = line.find(tag_beg) 
    p2 = line.find(tag_end)
    if (p1>1) or (p2>p1):
        res = line[(p1+len(tag_beg)):p2]
    return (res)


def set_tag(tag, value):
    res = ''
    tag_beg = '<'+tag+'>'
    tag_end = '</'+tag+'>'
    res = tag_beg + value + tag_end
    return (res)


with codecs.open('selected_letters.txt', encoding='utf-8') as f:
    for line in f:
        selected = line.strip('\n')
        
with open('tesseract_language.ini', 'r') as f:
    for line in f:
        tesseract_language = line.strip('\n')

doc_structure = []


def get_coords(d, i, height, offset):

    (text,left,top,right,bottom) = (d['char'][i],d['left'][i],d['top'][i],d['right'][i],d['bottom'][i])
    x1 = left
    y1 = height - top
    x2 = right
    y2 = height - bottom

    x1 = x1 - offset
    y1 = y1 - offset
    if x1 < 0:
        x1 = 0
    if y1 < 0:
        y1 = 0

    x2 = x2 + offset
    y2 = y2 + offset

    crd = ltc.coordinate()
    crd.x1 = x1
    crd.x2 = x2
    crd.y1 = y1
    crd.y2 = y2

    crd.letter = text

    crd.update_srt_coords()
    crd = find_word(crd)

    return crd


def find_word(crd):
    for word in doc_structure:
        if 'word' in word:
            w_coord = word
            word_idx = get_tag('widx', word)

            location = get_tag('location', word)
            line_id = get_tag('wline_id', word)
            word_id = get_tag('wwrd_id', word)

            ip_line_pos =int(get_tag('wip_line_pos', word))
            ip_word_pos =int(get_tag('wip_word_pos', word))

            found_in = get_tag('wfound_in', word)

            wx1 = get_tag('wcx1', word)
            wx2 = get_tag('wcx2', word)
            wy1 = get_tag('wcy1', word)
            wy2 = get_tag('wcy2', word)

            wx1 = float(wx1)
            wx2 = float(wx2)
            wy1 = float(wy1)
            wy2 = float(wy2)

            if (wx1<crd.xc) and (crd.xc<wx2) and (wy1<crd.yc) and (crd.yc<wy2):
                crd.found_in = found_in
                crd.location = location
                crd.w_coord = w_coord
                crd.ip_line_pos = ip_line_pos
                crd.ip_word_pos = ip_word_pos
                crd.line_id = line_id
                crd.word_id = word_id

    return crd


def save_letter(crop_img, t, letters_cnt, i, crd, letters, result_folder, letter_name):
    if len(crop_img) > 0:
        if not os.path.exists(result_folder+'letters\\'):
            os.makedirs(result_folder+'letters\\')

        img_name = letter_name + 'letter'+str(crd.letter_id).zfill(5)+'.bmp'
        cv2.imwrite(result_folder+'letters\\'+ img_name, crop_img)
        #ocr_letter = pytesseract.image_to_string(crop_img,lang='srp', config='--psm 10')
        ocr_letter = pytesseract.image_to_string(crop_img,lang=tesseract_language, config='--psm 10')
        if  ord(ocr_letter[-1]) == 12:
            ocr_letter = ocr_letter[:-1]
            ocr_letter = ocr_letter[:-1]

        crd.ocr_letter = ocr_letter
        crd.img_name = img_name

        crd.diacritic = 0

        letters.append(str(crd.letter_id)+', '+ t + ',,' +ocr_letter  +','+crd.str_coords+'\n')

    return crd


def save_letter10(crop_img, t, letters_cnt, i, crd, letters, result_folder, letter_name):
    if len(crop_img) > 0:
        if not os.path.exists(result_folder+'letters10\\'):
            os.makedirs(result_folder+'letters10\\')

        img_name = letter_name+ 'letter'+str(crd.letter_id).zfill(5)+'.bmp'
        cv2.imwrite(result_folder+'letters10\\'+ img_name, crop_img)

    return crd

def check_crd(crd_list, avr_let_width, avr_let_height):
    wrd_cnt = 0
    prev_word = ''
    for crd in crd_list:
        if prev_word != '':
            if crd.found_in != prev_word:
                #print (prev_word)
                wrd_cnt = 0

        if wrd_cnt<len(crd.found_in):
            crd.pos_in_word = wrd_cnt
            crd.letter = crd.found_in[wrd_cnt]
            #print ('-----')
            #print (crd.found_in)
            #print (wrd_cnt)
            #print (crd.letter, crd.ocr_letter)
            #print (crd.img_name)

        wrd_cnt = wrd_cnt + 1
        prev_word = crd.found_in

    avr_let_width3 = avr_let_width
    avr_let_height3 = avr_let_height

    return crd_list


def get_crd_list(filename):
    p1 = filename.find('\\')
    p2 = filename.find('.')
    result_folder='results\\'+filename[(p1+1):p2]+'\\'
    letter_name = filename[p1+1:p1+3]+filename[p2-9:p2-4]

    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    crop_letters = True

    offset = 3
    #offset = 0

    img = cv2.imread(filename)
    img2 = cv2.imread(filename)

    height = img.shape[0]
    width = img.shape[1]

    #d = pytesseract.image_to_boxes(img, output_type=Output.DICT, lang='srp') <<<<<
    d = pytesseract.image_to_boxes(img, output_type=Output.DICT, lang=tesseract_language)
    n_boxes = len(d['char'])
    avr_let_width = 0
    avr_let_height = 0
    cnt = 0


    for i in range(n_boxes):
        crd = get_coords(d, i, height, offset)

        avr_let_width = avr_let_width + (crd.x2 - crd.x1)
        avr_let_height = avr_let_height + (crd.y2 - crd.y1)
        cnt = cnt + 1


    avr_let_width = avr_let_width/cnt
    avr_let_height = avr_let_height/cnt

    avr_let_width20 = avr_let_width + avr_let_width*0.75
    avr_let_height20 = avr_let_height + avr_let_height*0.20

    avr_let_width30 = avr_let_width + avr_let_width*0.75 + avr_let_width*0.75


    use_prev_text = False
    letters = []
    crd_list = []
    letters_cnt = 0

    con_list = []

    for i in range(n_boxes):
        up_cord = False
        down_cord = False

        prev_text = crd.letter
        crd = get_coords(d, i, height, offset)
        extracted = False
        inside = False

        prev = i-1
        next = i+1

        ltr_off = 10

        if (prev in range(n_boxes)) and (next in range(n_boxes)):
            if len(crd_list)>0:
                p_crd = crd_list[-1]
            else:
                p_crd = get_coords(d, prev, height, offset)
            n_crd = get_coords(d, next, height, offset)

            #print ('CRD:',i,'p', p_crd.letter, p_crd.y1,p_crd.y2, 'c', crd.letter,ord(crd.letter), crd.y1, crd.y2, 'n', crd.letter, n_crd.y1,n_crd.y2 )
            # check superscript J
            if ord(crd.letter)==1112:
                #print((crd.y1 - p_crd.y1),(crd.y1 - n_crd.y1))
                #print((crd.y2 - p_crd.y2),(crd.y2 - n_crd.y2))
                if  ((crd.y1 - p_crd.y1) < -5) or ((crd.y1 - n_crd.y1) < -5):
                    up_cord = True
                if  ((crd.y2 - p_crd.y2) < -5) or ((crd.y2 - n_crd.y2) < -5):
                    down_cord = True


            if ((n_crd.x1-p_crd.x2)>-200) and ((n_crd.x1-p_crd.x2)<5) and (n_crd.word_id==p_crd.word_id):
                inside = True

            overlap_next=((crd.x2-n_crd.x1)/(crd.x2-crd.x1))
            if (overlap_next>0.7) and (crd.word_id==n_crd.word_id):
                inside = True

            overlap_prev=((p_crd.x2-crd.x1)/(crd.x2-crd.x1))

            if (overlap_prev>0.7) and (p_crd.word_id==crd.word_id):
                inside = True

        crop_img = img2[crd.y1:crd.y2, crd.x1:crd.x2]
        crop_img10 = img2[crd.y1-13:crd.y2, crd.x1:crd.x2+10]
        res_con = rc_con.recognize_letter(crop_img)

        ##### ekstrakcija svih slika
        ''' 
        t = crd.letter

        crd.letter_id = letters_cnt
        crd = save_letter(crop_img, t, letters_cnt, i, crd, letters, letter_name)
        crd_list.append(crd)
        letters_cnt = letters_cnt + 1
        cv2.rectangle(img, (crd.x1,crd.y1), (crd.x2,crd.y2) , (255,0,255), 2)
        con_list.append(res_con)
        '''
        #####

        if (res_con[0] == 1):

            if not inside:
                cv2.rectangle(img, (crd.x1,crd.y1), (crd.x2,crd.y2) , (255,0,0), 2)
                if down_cord and up_cord:
                    cv2.rectangle(img, (crd.x1,crd.y1), (crd.x2,crd.y2) , (0,0,255), 2)
                    crd.superscript = 1


                t = crd.letter

                crd.letter_id = letters_cnt
                crd = save_letter(crop_img, t, letters_cnt, i, crd, letters, result_folder, letter_name)
                save_letter10(crop_img10, t, letters_cnt, i, crd, letters, result_folder, letter_name)

                crd_list.append(crd)
                letters_cnt = letters_cnt + 1

        if (res_con[2] == 1):
            crd_a = ltc.coordinate()
            crd_b = ltc.coordinate()

            crd_a.copy_from(crd)
            crd_b.copy_from(crd)

            crd_a.x2 = crd.x1 + int(crd.let_width/2)-2
            crd_b.x1 = crd.x1 + int(crd.let_width/2)+2

            cv2.rectangle(img, (crd_b.x1,crd_b.y1), (crd_b.x2,crd_b.y2) , (0,255,0), 2)

            crop_img_a = img2[crd_a.y1:crd_a.y2, crd_a.x1:crd_a.x2]
            crop_img_b = img2[crd_b.y1:crd_b.y2, crd_b.x1:crd_b.x2]

            crop_img_a10 = img2[crd_a.y1-13:crd_a.y2, crd_a.x1:crd_a.x2+10]
            crop_img_b10 = img2[crd_b.y1-13:crd_b.y2, crd_b.x1:crd_b.x2+10]

            crd_a.letter_id = letters_cnt
            crd_a.update_srt_coords()

            if len(crd_list)>0:
                p_crd2 = crd_list[-1]
                if ((p_crd2.x2-crd.x1) < (avr_let_width/2)) or ((crd.y1-p_crd.y1)>30):
                    crd_a = save_letter(crop_img_a, crd_a.letter, letters_cnt, i, crd_a, letters, result_folder, letter_name)
                    save_letter10(crop_img_a10, crd_a.letter, letters_cnt, i, crd_a, letters, result_folder, letter_name)
                    cv2.rectangle(img, (crd_a.x1,crd_a.y1), (crd_a.x2,crd_a.y2) , (0,255,0), 2)
                    crd_list.append(crd_a)
                    letters_cnt = letters_cnt + 1
                #else:
                    #print('overlap with previous')
            else:
                crd_a = save_letter(crop_img_a, crd_a.letter, letters_cnt, i, crd_a, letters, result_folder, letter_name)
                save_letter10(crop_img_a10, crd_a.letter, letters_cnt, i, crd_a, letters, result_folder, letter_name)
                cv2.rectangle(img, (crd_a.x1,crd_a.y1), (crd_a.x2,crd_a.y2) , (0,255,0), 2)
                crd_list.append(crd_a)
                letters_cnt = letters_cnt + 1


            crd_b.letter_id = letters_cnt
            crd_b.update_srt_coords()
            crd_b = save_letter(crop_img_b, crd_b.letter, letters_cnt, i, crd_b, letters, result_folder, letter_name)
            save_letter10(crop_img_b10, crd_b.letter, letters_cnt, i, crd_b, letters, result_folder, letter_name)
            crd_list.append(crd_b)
            letters_cnt = letters_cnt + 1

            extracted = True
            use_prev_text = False

        if (res_con[3] == 1):
            crd_a = ltc.coordinate()
            crd_b = ltc.coordinate()
            crd_c = ltc.coordinate()

            crd_a.copy_from(crd)
            crd_b.copy_from(crd)
            crd_c.copy_from(crd)

            crd_a.x2 = crd.x1 + int(crd.let_width*1/3)-2
            
            crd_b.x1 = crd.x1 + int(crd.let_width*1/3)+2
            crd_b.x2 = crd.x1 + int(crd.let_width*2/3)-2
            
            crd_c.x1 = crd.x1 + int(crd.let_width*2/3)+2


            cv2.rectangle(img, (crd_a.x1,crd_a.y1), (crd_a.x2,crd_a.y2) , (0,255,255), 2)
            cv2.rectangle(img, (crd_b.x1,crd_b.y1), (crd_b.x2,crd_b.y2) , (0,255,255), 2)
            cv2.rectangle(img, (crd_c.x1,crd_c.y1), (crd_c.x2,crd_c.y2) , (0,255,255), 2)


            crop_img_a = img2[crd_a.y1:crd_a.y2, crd_a.x1:crd_a.x2]
            crop_img_b = img2[crd_b.y1:crd_b.y2, crd_b.x1:crd_b.x2]
            crop_img_c = img2[crd_c.y1:crd_b.y2, crd_c.x1:crd_c.x2]

            crop_img_a10 = img2[crd_a.y1-13:crd_a.y2, crd_a.x1:crd_a.x2+10]
            crop_img_b10 = img2[crd_b.y1-13:crd_b.y2, crd_b.x1:crd_b.x2+10]
            crop_img_c10 = img2[crd_c.y1-13:crd_b.y2, crd_c.x1:crd_c.x2+10]

            crd_a.letter_id = letters_cnt
            crd_a.update_srt_coords()
            crd_a = save_letter(crop_img_a, crd_a.letter, letters_cnt, i, crd_a, letters, result_folder, letter_name)
            save_letter10(crop_img_a10, crd_a.letter, letters_cnt, i, crd_a, letters, result_folder, letter_name)
            crd_list.append(crd_a)
            letters_cnt = letters_cnt + 1

            crd_b.letter_id = letters_cnt
            crd_b.update_srt_coords()
            crd_b = save_letter(crop_img_b, crd_b.letter, letters_cnt, i, crd_b, letters, result_folder, letter_name)
            save_letter10(crop_img_b10, crd_b.letter, letters_cnt, i, crd_b, letters, result_folder, letter_name)
            crd_list.append(crd_b)
            letters_cnt = letters_cnt + 1


            crd_c.letter_id = letters_cnt
            crd_c.update_srt_coords()
            crd_c = save_letter(crop_img_c, crd_c.letter, letters_cnt, i, crd_c, letters, result_folder, letter_name)
            save_letter10(crop_img_c10, crd_c.letter, letters_cnt, i, crd_c, letters, result_folder, letter_name)
            crd_list.append(crd_c)
            letters_cnt = letters_cnt + 1

            extracted = True
            use_prev_text = False

    cv2.imwrite(result_folder+'selected_letters.jpg', img)

    return crd_list, avr_let_width, avr_let_height


def find_diacritics(crd_list, filename):

    p1 = filename.find('\\')
    p2 = filename.find('.')
    result_folder='results\\'+filename[(p1+1):p2]+'\\'

    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    img_diacritics = cv2.imread(filename)

    # training letters begins at
    training_cnt = 3000
    for crd in crd_list:
        #print (crd.letter_id, crd.letter.upper() , selected.upper())
        if crd.letter.upper() in selected.upper():
            if not os.path.exists(result_folder+'letters\\'):
                os.makedirs(result_folder+'letters\\')
            if not os.path.exists(result_folder+'training\\'):
                os.makedirs(result_folder+'training\\')

            training_cnt = training_cnt + 1

            res = rc.recognize(result_folder+'letters10\\'+crd.img_name)
            #print (str(crd.img_name) +' '+ str(res))

            if (crd.superscript == 1):
                cv2.rectangle(img_diacritics, (crd.x1,crd.y1), (crd.x2,crd.y2) , (0,255,0), 2)

            if (res[0] != 1):
                cv2.rectangle(img_diacritics, (crd.x1,crd.y1), (crd.x2,crd.y2) , (0,0,255), 2)

            if (res[2] == 1):
                crd.diacritic = 2
                dletter = gl.get_letter(crd.letter, 2)

            if (res[3] == 1) and  (res[16] == 0):
                crd.diacritic = 3
                dletter = gl.get_letter(crd.letter, 3)

            if (res[4] == 1):
                crd.diacritic = 4
                dletter = gl.get_letter(crd.letter, 4)

            if (res[5] == 1):
                crd.diacritic = 5
                dletter = gl.get_letter(crd.letter, 5)

            if (res[6] == 1)and(res[3] == 0) :
                crd.diacritic = 6
                dletter = gl.get_letter(crd.letter, 6)

            if (res[7] == 1):
                crd.diacritic = 3
                dletter = gl.get_letter(crd.letter, 6)

            if (res[13] == 1):
               crd.diacritic = 13

            if (res[13] == 1) and (res[2] == 1):
               crd.diacritic = 1302

            if (res[13] == 1) and (res[3] == 1):
               crd.diacritic = 1303

            if (res[13] == 1) and (res[4] == 1):
               crd.diacritic = 1304

            if (res[13] == 1) and (res[5] == 1):
               crd.diacritic = 1305

            if (res[13] == 1) and (res[6] == 1):
               crd.diacritic = 1306

            if (res[16] == 1) and (res[3] == 0):
               crd.diacritic = 16

            if (res[16] == 1) and (res[3] == 1):
                crd.diacritic = 316

            # letter sh 25
            if (res[22] == 1):
               crd.diacritic = 22

            # letter p  24
            if (res[23] == 1):
               crd.diacritic = 23

             # letter g 27
            if (res[24] == 1):
               crd.diacritic = 24
               #print ('G')
               #exit()

            # letter v  26
            if (res[25] == 1):
               crd.diacritic = 25
               #print ('V')
               #exit()


    with codecs.open(result_folder+"letters_coordinates.txt", "w", encoding="utf-8") as f:
        for crd in crd_list:
            f.write("%s" % crd.to_str()+'\n')

    cv2.imwrite(result_folder+'img_diacritics.jpg', img_diacritics)


def extract_letters(filename):
    print ('extracting coordinates from: '+ filename)
    p1 = filename.find('\\')
    p2 = filename.find('.')
    result_folder='results\\'+filename[(p1+1):p2]+'\\'

    with codecs.open(result_folder + 'word_output.txt', encoding='utf-8') as f:
        for line in f:
            line = line.strip('\n')
            doc_structure.append(line)


    print ('get_crd_list...')
    crd_list, avr_let_width, avr_let_height = get_crd_list(filename)
    print ('check_crd...')
    crd_list = check_crd(crd_list, avr_let_width, avr_let_height)
    print ('find_diacritics...')
    find_diacritics(crd_list, filename)

#extract_letters('scan\\'+'Dubrovnik0019_small2.tif')