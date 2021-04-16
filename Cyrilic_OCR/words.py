import pytesseract
from pytesseract import Output
import cv2
import numpy as np
import codecs
from difflib import SequenceMatcher
import os

line_similariti = 0.35

def get_tag(tag):
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


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def extract_img(img2, x1, x2, y1, y2, offset):
    height = img2.shape[0]
    width = img2.shape[1]
    x2 = x2 + offset
    y2 = y2 + offset
    x1 = x1 - offset
    y1 = y1 - offset
    if x1<1:
        x1 = 1
    if y1<1:
        y1 = 1
    if y2 > height:
        y2 = height
    if x2 > width:
        x2 = width
    crop_img = img2[y1:(y2), (x1):(x2)]

    crop_text = pytesseract.image_to_string(crop_img, lang='srp')

    return (crop_img, crop_text)


def find_line(plain_text, line, line_cnt):
    found = False
    num_of_found = 0
    cnt = 0
    best=0
    sim_cnt = 0

    for txt_line in plain_text:
        txt_line = txt_line.strip('\n')

        sim = similar(txt_line , line)
        if best<sim:
            best = sim
            sim_cnt= cnt

        if txt_line == line:
            found = True
            num_of_found = cnt
        cnt = cnt + 1
    if found == False:
        num_of_found = -1
        if best> line_similariti:
            num_of_found=sim_cnt

    return found, num_of_found


def find_word(line, word, word_pos):
    found = False
    line = line[word_pos:]

    p1 = line.find(word) + word_pos
    p2 = p1 + len(word)

    slpos = line[p2:]
    if p1 !=-1:
        found = True
    
    p3 = slpos.find(word)

    return found, p1, p2


def get_words(filename):
    print (filename)

    p1 = filename.find('\\')
    p2 = filename.find('.')
    result_folder='results\\'+filename[(p1+1):p2]+'\\'

    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
        
    if not os.path.exists(result_folder+'paragraph'):
        os.makedirs(result_folder+'paragraph')
        
    if not os.path.exists(result_folder+'lines'):
        os.makedirs(result_folder+'lines')

    if not os.path.exists(result_folder+'words'):
        os.makedirs(result_folder+'words')

    img = cv2.imread(filename)
    img_selected_pargraph = cv2.imread(filename)
    img_selected_lines = cv2.imread(filename)
    img_selected_words = cv2.imread(filename)

    img2 = cv2.imread(filename)


    height = img.shape[0]
    width = img.shape[1]
    page = 0
    column = 0
    paragraph = 0
    line = 0
    word = 0
    offset = 8

    line_cnt = 0
    word_pos = 0
    word_end = 0

    plain_text = pytesseract.image_to_string(img, lang='srp')
    with codecs.open(result_folder+"plain.txt", "w", encoding="utf-8") as f:
        f.write(plain_text)
    plain_text= plain_text.splitlines()


    lines_list = []
    line_map = []
    words = []
    d = pytesseract.image_to_data(img, output_type=Output.DICT, lang='srp')
    n_boxes = len(d['level'])
    with codecs.open(result_folder+"word_output.txt", "w", encoding="utf-8") as f:
        for i in range(n_boxes):
            (text,level, x, y, w, h) = (d['text'][i], d['level'][i],d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            x1 = x
            y1 = y
            x2 = x+w
            y2 = y+h

            #page
            if level==1:
                page = i
                #cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            #column
            if level==2:
                column = i
                #cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            #paragraph
            if level==3:
                paragraph = i
                cv2.rectangle(img_selected_pargraph, (x1, y1), (x2, y2), (0, 255, 0), 2)
                (crop_img, crop_text) =  extract_img(img2, x1, x2, y1, y2, offset)
                cv2.imwrite(result_folder+'paragraph\\paragraph_'+str(i).zfill(4)+'.jpg', crop_img)
                f.write("paragraph->"+text+'\n')
                #line_map.append(str(line_cnt)+','+str(paragraph).zfill(4) + ',' + str(line).zfill(4))

            #line
            if level==4:
                line = i
                cv2.rectangle(img_selected_lines, (x1, y1), (x2, y2), (255, 0, 0), 2)

                (crop_img, crop_line) =  extract_img(img2, x1, x2, y1, y2, offset)
                found, line_cnt = find_line(plain_text, crop_line, line_cnt)

                cv2.imwrite(result_folder+'lines\\line_'+str(i).zfill(4)+'.jpg', crop_img)
                location = '(P('+ str(page) + ',' + str(column) + ',' + str(paragraph).zfill(4) +',' + str(line).zfill(4) + ')P)'
                coords = '(C(' + str(x1) + ',' + str(x2) + ',' + str(y1) + ',' + str(y2) + ')C)'
                f.write('line->' + location + coords + crop_line+ '\n')
                lines_list.append(crop_line)
                line_map.append(set_tag('txt_line',str(line_cnt).zfill(4))+set_tag('par',str(paragraph).zfill(4)) +set_tag('img_line', str(line).zfill(4)))

                word_pos = 0
                word_end = 0

                #print(text)
                #print(crop_line)
                #print('-----------------------------')

            #words
            if level==5:
                word = i
                cv2.rectangle(img_selected_words, (x1, y1), (x2, y2), (0, 0, 255), 2)

                (crop_img, crop_word) =  extract_img(img2, x1, x2, y1, y2, offset)

                #print (line_cnt)
                found, word_pos, word_end = find_word(plain_text[line_cnt], text, word_end)

                cv2.imwrite(result_folder+'words\\words_'+str(i)+'.tif', crop_img)
                location = set_tag('wpage',str(page)) + set_tag('wcolumn',str(column)) + set_tag('wpar',str(paragraph).zfill(4)) +set_tag('wline_id', str(line).zfill(4)) + set_tag('wwrd_id', str(word))
                coords = set_tag('wcx1',str(x1)) + set_tag('wcx2',str(x2)) + set_tag('wcy1',str(y1)) + set_tag('wcy2',str(y2))
                f.write("word->"+ set_tag('widx', str(i)) + location + coords + set_tag('wlen',str(len(text))) + set_tag('wip_line_pos',str(line_cnt)) + set_tag('wip_word_pos',str(word_pos)) +  set_tag('wfound_in',text) + '\n')

                #print(text)
                #print(crop_word)
                #print('-----------------------------')
                words.append(location + coords + text)


    with codecs.open(result_folder+"line_map.txt", "w", encoding="utf-8") as f:
        for line in line_map:
            f.write(line+ '\n')

    cv2.imwrite(result_folder+'selected_pargraph.jpg', img_selected_pargraph)
    cv2.imwrite(result_folder+'selected_lines.jpg', img_selected_lines)
    cv2.imwrite(result_folder+'selected_words.jpg', img_selected_words)
    return(words)

#get_words('scan\\Dubrovnik0018_crop.tif')

