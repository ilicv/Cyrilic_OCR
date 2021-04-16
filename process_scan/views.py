
import os
import sys

import os.path
from os import path

from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from django import forms
import process_scan.models
from django.db.models import Q
import codecs
import socket
import cv2
from scipy import ndimage


pjoin = os.path.join

# from django.template.context_processors import request
root_dir = os.path.dirname(os.path.realpath(__file__))

sys.path.append(pjoin(root_dir,'process_scan','templates'))
sys.path.append(pjoin(root_dir, 'python_code'))
sys.path.append(pjoin(root_dir, 'Cyrilic_OCR'))
#import Cyrilic_OCR.ocr_main as om
#import ocr_main as om

max_paralell = 8



import zipfile
import filecmp

from django.db import connection
from django.db import transaction
import subprocess
from django.core.files.storage import FileSystemStorage
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


# internal function for OCR
def ifun_ocr(file, rotate):
    page = scaned_page()

    pos1 = file.find('.')
    filename = file[:pos1]
    filename_txt = filename+'.txt'

    page.original_scan = pjoin('Cyrilic_OCR', 'scan', file)
    if rotate == "True":
        file_left = filename + '_left.tif'
        file_right = filename + '_right.tif'
        path_left = pjoin('Cyrilic_OCR', 'scan', file_left)
        path_right = pjoin('Cyrilic_OCR', 'scan', file_right)
        print (path_left + '\n')
        print (path_right + '\n')

        sc_image = cv2.imread(page.original_scan)
        print ('img loaded\n')
        #rotation angle in degree
        rotated_p1 = ndimage.rotate(sc_image, 0.1, cval=255)
        rotated_n1 = ndimage.rotate(sc_image, -0.1, cval=255)
        print ('img rotated\n')

        cv2.imwrite(path_left, rotated_p1)
        cv2.imwrite(path_right, rotated_n1)
        print ('new img saved\n')
        #exit()

    page.filename = filename

    sdia = pjoin('Cyrilic_OCR', 'results',filename,'img_diacritics.jpg')
    if path.exists(sdia):
        page.selected_diacritics = sdia

    current_dir = os.getcwd()
    os.chdir(pjoin(current_dir,'Cyrilic_OCR'))
    #os.system("C:\Windows\System32\cmd.exe /c Cyrilic_OCR\main.bat "+file)
    os.system('python main.py '+file)

    original = pjoin('results', filename, filename_txt)
    target = pjoin('results', filename, filename+'_backup.txt')
    shutil.copyfile(original, target)
    if rotate == "True":
        os.system('python main.py '+file_left)
        os.system('python main.py '+file_right)
        
        pos1 = file_left.find('.')
        filename_left = file_left[:pos1]
        #original = pjoin('Cyrilic_OCR', 'results', filename_left, filename_txt)
        #target = pjoin('Cyrilic_OCR', 'results', filename, filename+'_left.txt')
        original = pjoin('results', filename_left, filename_left + '.txt')
        target = pjoin('results', filename, filename + '_left.txt')
        shutil.copyfile(original, target)
        pos1 = file_right.find('.')
        filename_right = file_right[:pos1]
        #original = pjoin('Cyrilic_OCR', 'results', file, filename_right, filename_txt)
        #target = pjoin('Cyrilic_OCR', 'results', filename, filename+'_right.txt')
        original = pjoin('results', filename_right, filename_right + '.txt')
        target = pjoin('results', filename, filename + '_right.txt')
        shutil.copyfile(original, target)
        shutil.rmtree(pjoin('results', filename_left))
        shutil.rmtree(pjoin('results', filename_right))

        os.system('python start_compare.py '+file)

    os.chdir(current_dir)
    
    if rotate == "True":
        os.remove(path_left) 
        os.remove(path_right) 

    return page

    
def get_paragraph(lmc_list, line):
    par = ''
    img_line = ''
    for lmc in lmc_list:
        if lmc.txt_line == line:
            par = lmc.par
            img_line = lmc.img_line
    print (line, par, img_line)
    return (par, img_line)


class compare_case:
    def __init__(self):
        self.line = ''
        self.word_pos =''
        self.paragraph = ''
        self.predicted = ''
        self.rotated = ''
        self.rotated_word = ''
        self.pred_word = ''
        self.p_word_beg = ''
        self.p_word_end = ''


class line_map_class:
    def __init__(self):
        self.txt_line = ''
        self.par =''
        self.img_line = ''


class scaned_page:
    def __init__(self):
        self.original_scan = ''
        self.selected_diacritics = ''
        self.selected_letters = ''
        self.selected_words = ''
        self.selected_lines = ''
        self.selected_pargraph = ''
        self.save_corrections = ''
        self.plain_modified_left = ''
        self.plain_modified_right = ''
        self.line_map = ''
        self.line_disp = ''


class page_paragraphs:
    def __init__(self):
        self.par_lines = []
        self.par_imgs = []
        self.file = ''
        self.filename = ''


def index(request):
    #current_path = os.path.realpath(__file__)

    scan_folder = pjoin('Cyrilic_OCR', 'scan')
    #results_folder = pjoin(current_path, 'Cyrilic_OCR', 'results')

    files = os.listdir(scan_folder)

    list_of_pages = []
    for file in files:
        page = scaned_page()
        page.file = file

        pos1 = file.find('.')
        filename = file[:pos1]
        filename_txt = filename+'.txt'

        page.original_scan = pjoin('Cyrilic_OCR', 'scan', file)
        
        #page.original_scan = file
        page.filename = filename

        sdia = pjoin('Cyrilic_OCR', 'results',filename,'img_diacritics.jpg')
        #print(sdia)
        if path.exists(sdia):
            page.selected_diacritics = sdia
        slett = pjoin('Cyrilic_OCR', 'results',filename,'selected_letters.jpg')
        if path.exists(slett):
            page.selected_letters = slett
        sword = pjoin('Cyrilic_OCR', 'results',filename,'selected_words.jpg')
        if path.exists(sword):
            page.selected_words = sword
        sline = pjoin('Cyrilic_OCR', 'results',filename,'selected_lines.jpg')
        if path.exists(sline):
            page.selected_lines = sline
        spar = pjoin('Cyrilic_OCR', 'results',filename,'selected_pargraph.jpg')
        if path.exists(spar):
            page.selected_pargraph = spar

        sav_cor = pjoin('Cyrilic_OCR', 'results',filename,filename_txt)
        if path.exists(sav_cor):
            page.save_corrections = sav_cor

        plain_modified_left = pjoin('Cyrilic_OCR', 'results',filename,filename+'_left.txt')
        if path.exists(plain_modified_left):
            page.plain_modified_left = plain_modified_left
        plain_modified_right = pjoin('Cyrilic_OCR', 'results',filename,filename+'_right.txt')
        if path.exists(plain_modified_right):
            page.plain_modified_right = plain_modified_right

        list_of_pages.append(page)

    # Python Program to Get IP Address
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    print("Your Computer Name is:" + hostname)
    print("Your Computer IP Address is:" + IPAddr)

    #return HttpResponse("index page template location :  " + home_template)
    #return render(request, 'process_scan/home.html')
    context = {
               'files': files,
               'list_of_pages':list_of_pages,
               'hostname':hostname,
               'IPAddr':IPAddr
               }

    return render(request, 'home.html', context)
# end def index

'''
def process_scan(request):
    #return render(request, 'appint/home.html')
    return HttpResponse('This is the process_scan!')
# end def process_scan
'''

def show_result(request):
    scan_folder = pjoin('Cyrilic_OCR', 'scan')
    
    if request.method == 'GET':
        file = request.GET.get('file', 0)
        print(file)
        
        num_cases = int(request.GET.get('num_cases', 0))

    print('num_cases:',num_cases)
    if str(num_cases)!="0":
        save_compare(request)

    page = scaned_page()
    page.file = file

    pos1 = file.find('.')
    filename = file[:pos1]
    filename_txt = filename+'.txt'

    page.original_scan = pjoin('Cyrilic_OCR', 'scan', file)

    page.filename = filename

    sdia = pjoin('Cyrilic_OCR', 'results',filename,'img_diacritics.jpg')
    if path.exists(sdia):
        page.selected_diacritics = sdia
        page.selected_diacritics = 'Cyrilic_OCR/results/'+filename+'/img_diacritics.jpg'
        

    slett = pjoin('Cyrilic_OCR', 'results',filename,'selected_letters.jpg')
    if path.exists(slett):
        page.selected_letters = slett
        page.selected_letters = 'Cyrilic_OCR/results/'+filename+'/selected_letters.jpg'
    sword = pjoin('Cyrilic_OCR', 'results',filename,'selected_words.jpg')
    if path.exists(sword):
        page.selected_words = sword
        page.selected_words = 'Cyrilic_OCR/results/'+filename+'/selected_words.jpg'
    sline = pjoin('Cyrilic_OCR', 'results',filename,'selected_lines.jpg')
    if path.exists(sline):
        page.selected_lines = sline
        page.selected_lines = 'Cyrilic_OCR/results/'+filename+'/selected_lines.jpg'
    spar = pjoin('Cyrilic_OCR', 'results',filename,'selected_pargraph.jpg')
    if path.exists(spar):
        page.selected_pargraph = spar
        page.selected_pargraph = 'Cyrilic_OCR/results/'+filename+'/selected_pargraph.jpg'

    spmod = pjoin('Cyrilic_OCR', 'results',filename,filename_txt)
    if path.exists(spmod):
        page.plain_modified = spmod
        f = open(spmod, 'r')
        file_content = ''
        with codecs.open(spmod, encoding='utf-8') as f:
            for line in f:
                file_content = file_content + line
        page.plain_modified_content = file_content

    par_folder = pjoin('Cyrilic_OCR', 'results',filename,'paragraph')

    par_files = os.listdir(par_folder)
    list_of_paragraph = []
    for file in par_files:
        list_of_paragraph.append(pjoin(par_folder,file))


    context = {
               'page': page,
               'list_of_paragraph':list_of_paragraph
               }
    return render(request, 'show_result.html', context)

# end def show_result


def get_differeces(file, rotation):
    scan_folder = pjoin('Cyrilic_OCR', 'scan')
    page = scaned_page()
    page.file = file

    pos1 = file.find('.')
    filename = file[:pos1]
    filename_txt = filename+'.txt'


    page.original_scan = pjoin('Cyrilic_OCR', 'scan', file)

    page.filename = filename

    sdia = pjoin('Cyrilic_OCR', 'results',filename,'img_diacritics.jpg')
    if path.exists(sdia):
        page.selected_diacritics = sdia

    # get information from line_map file
    lmc_list = []
    line_map_file = pjoin('Cyrilic_OCR', 'results',filename,'line_map.txt')
    with codecs.open(line_map_file, encoding='utf-8') as f:
        for line in f:
            lmc = line_map_class()
            lmc.txt_line = get_tag(line, 'txt_line')
            lmc.par = get_tag(line, 'par')
            lmc.img_line = get_tag(line, 'img_line')
            lmc_list.append(lmc)

    num_cases = 0
    rep = ''
    cc_list = []
    print(filename)
    print(filename+'1')
    print(rotation)
    print(rotation+'1')
    com_report = pjoin('Cyrilic_OCR', 'results',filename,'report_'+rotation+'.txt')
    if path.exists(com_report):
        prev_line = '-1'
        with codecs.open(com_report, encoding='utf-8') as f:
            for line in f:
                print(line)
                line_err = get_tag(line, 'line_num')
                if prev_line !=line_err:
                    cc = compare_case()
                    cc.line_cnt = num_cases
                    cc.line = line_err
                    cc.line_disp = str(int(get_tag(line, 'line_num'))+1)

                    cc.word_pos = get_tag(line, 'word_pos')
                    cc.predicted = get_tag(line, 'predicted')

                    cc.missing_pred = get_tag(line, 'missing_pred')
                    cc.missing_rotated = get_tag(line, 'missing_rotated')


                    cc.rotated = get_tag(line, 'rotated')
                    cc.pred_word = get_tag(line, 'pred_word')
                    cc.rotated_word = get_tag(line, 'rotated_word')

                    cc.predicted_bold = get_tag(line, 'predicted')
                    if get_tag(line, 'p_word_beg') != '':
                        cc.p_word_beg = int(get_tag(line, 'p_word_beg'))
                        cc.p_word_end = int(get_tag(line, 'p_word_end'))


                        pred1=cc.predicted[0:cc.p_word_beg]
                        pred2=cc.predicted[cc.p_word_beg:cc.p_word_end]
                        pred3=cc.predicted[cc.p_word_end:]
                        cc.predicted_bold = pred1 + '<b><font  color="#ED0000">' + pred2 + '</font></b>'+ pred3

                    cc.rotated_bold = get_tag(line, 'rotated')
                    if get_tag(line, 'r_word_beg') != '':
                        cc.r_word_beg = int(get_tag(line, 'r_word_beg'))
                        cc.r_word_end = int(get_tag(line, 'r_word_end'))

                        rot1=cc.rotated[0:cc.r_word_beg]
                        rot2=cc.rotated[cc.r_word_beg:cc.r_word_end]
                        rot3=cc.rotated[cc.r_word_end:]
                        cc.rotated_bold = rot1 + '<b><font  color="#0000ED">' + rot2 + '</font></b>'+ rot3
                        print(cc.rotated_bold)


                    print(line)
                    line_num = int(get_tag(line, 'line_num'))
                    line_num = str(line_num).zfill(4)
                    par, img_line = get_paragraph(lmc_list, line_num)
                    cc.par_file = pjoin('Cyrilic_OCR', 'results', filename, 'paragraph', 'paragraph_' + par + '.jpg')
                    cc.img_line_file = pjoin('Cyrilic_OCR', 'results', filename, 'lines', 'line_'+img_line + '.jpg')
                    num_cases = num_cases + 1
                    cc_list.append(cc)
                    prev_line = line_err
                else:
                    cc.word_pos = 'Vise reci se razlikuje u ovoj liniji'
                    #cc.predicted = ''
                    cc.missing_pred = 'err'
                    cc.missing_rotated = ''
                    if get_tag(line, 'p_word_beg') != '':
                        cc.p_word_beg = int(get_tag(line, 'p_word_beg')) 
                        cc.p_word_end = int(get_tag(line, 'p_word_end')) 


                        pred1=cc.predicted[0:cc.p_word_beg]
                        pred2=cc.predicted[cc.p_word_beg:cc.p_word_end]
                        pred3=cc.predicted[cc.p_word_end:]
                        cc.predicted_bold = '<b><font  color="#ED0000">' + pred1 +  pred2 + pred3 + '</font></b>'

                    if get_tag(line, 'r_word_beg') != '':
                        cc.r_word_beg = int(get_tag(line, 'r_word_beg'))
                        cc.r_word_end = int(get_tag(line, 'r_word_end'))

                        rot1=cc.rotated[0:cc.r_word_beg]
                        rot2=cc.rotated[cc.r_word_beg:cc.r_word_end]
                        rot3=cc.rotated[cc.r_word_end:]
                        cc.rotated_bold = '<b><font  color="#0000ED">' + rot1 + rot2 + rot3 + '</font></b>'
                        print(cc.rotated_bold)

    spmod = pjoin('Cyrilic_OCR', 'results',filename,filename_txt)
    if path.exists(spmod):
        page.plain_modified = spmod
        f = open(spmod, 'r')
        file_content = ''
        with codecs.open(spmod, encoding='utf-8') as f:
            for line in f:
                file_content = file_content + line
        page.plain_modified_content = file_content

    par_folder = pjoin('Cyrilic_OCR', 'results',filename,'paragraph')

    par_files = os.listdir(par_folder)
    list_of_paragraph = []
    for file in par_files:
        list_of_paragraph.append(pjoin(par_folder,file))

    return page, cc_list, num_cases, list_of_paragraph


def compare(request):
    if request.method == 'GET':
        file = request.GET.get('file', 0)
        rotation = request.GET.get('rotation', 0)

        current_dir = os.getcwd()
        os.chdir(pjoin(current_dir,'Cyrilic_OCR'))
        os.system('python start_compare.py '+file)
        os.chdir(current_dir)

        print(file)

    page, cc_list, num_cases, list_of_paragraph = get_differeces(file, rotation)


    context = {
               'page': page,
               'list_of_paragraph':list_of_paragraph,
               'cc_list':cc_list,
               'num_cases':num_cases,
               'rotation':rotation,
               
               }
    return render(request, 'compare.html', context)
# end def compare


def save_compare(request):
    page = scaned_page()

    if request.method == 'GET':
        file = request.GET.get('file', 0)
        print(file)
        rotation = request.GET.get('rotation', 0)
        page, cc_list, num_cases, list_of_paragraph = get_differeces(file, rotation)

    pos1 = file.find('.')
    filename = file[:pos1]
    filename_txt = filename+'.txt'

    print('open')
    spmod = pjoin('Cyrilic_OCR', 'results',filename,filename_txt)
    print('open'+spmod)
    file_content = []
    if path.exists(spmod):
        page.plain_modified = spmod
        f = open(spmod, 'r')
        with codecs.open(spmod, encoding='utf-8') as f:
            for line in f:
                file_content.append(line)
                print(line)

    if request.method == 'GET':
        num_cases = int(request.GET.get('num_cases', 0))
        #word = []
        #line = []
        for idx in range(0,num_cases):
            corrected_word = request.GET.get('word'+str(idx), 0) 
            corrected_line = request.GET.get('line'+str(idx), 0) 
            cc = cc_list[idx]
            print('-------------')
            print(cc.line, cc.predicted)

            line_to_correct = int(cc.line)
            if line_to_correct<len(file_content):
                print(file_content[line_to_correct])
                print('cw: ',corrected_word)
                print('cl: ',corrected_line)

                if cc.p_word_beg != '' and corrected_word !='':
                    print('corrected word')
                    pred1=cc.predicted[0:cc.p_word_beg]
                    pred2=cc.predicted[cc.p_word_beg:cc.p_word_end]
                    if cc.word_pos !='0':
                        pred3=cc.predicted[cc.p_word_end-1:]
                    else:
                        pred3=cc.predicted[cc.p_word_end:]
                    corrected = pred1 + corrected_word + pred3+'\n'
                    print(corrected)
                    file_content[line_to_correct] = corrected

                if corrected_line !='':
                    print('line')

                    corrected = corrected_line+'\n'
                    print(corrected)
                    file_content[line_to_correct] = corrected
                print('================')


    save_cor = pjoin('Cyrilic_OCR', 'results',filename,filename_txt)
    with codecs.open(save_cor, "w", encoding="utf-8") as f:
        for line in file_content:
            f.write(line)

    #compare modified with expected text
    current_dir = os.getcwd()
    os.chdir(pjoin(current_dir,'Cyrilic_OCR'))
    os.system('python compare_expected.py '+file)
    os.chdir(current_dir)

    context = {
               'page': page,
               }

    #return render(request, 'save_corrections.html', context)
    #return render(request, 'show_result.html', context)
# end def save_compare


def start_ocr(request):
    scan_folder = pjoin('Cyrilic_OCR', 'scan')

    if request.method == 'GET':
        file = request.GET.get('file', 0)
        print(file)

    if request.method == 'GET':
        rotate = request.GET.get('rotate', 0)
        print('rotate'+ str(rotate))

    page= ifun_ocr(file, rotate)
    
    context = {
               'page': page,
               'file':file
               }
    return render(request, 'ocr_processing_completed.html', context)
# end start_ocr


def save_corrections(request):
    page = scaned_page()

    if request.method == 'GET':
        modified_text = request.GET.get('modified_text', 0)
        modified_text = modified_text.replace('<br />', '\n')
        modified_text = modified_text.replace('<br/>', '\n')
        modified_text = modified_text.replace('<br>', '\n')
        modified_text = modified_text.replace('</p>', '')
        modified_text = modified_text.replace('<p>', '')
        #print(modified_text)
        page.modified_text = modified_text

    if request.method == 'GET':
        file = request.GET.get('file', 0)
        page.file = file

    pos1 = file.find('.')
    filename = file[:pos1]
    filename_txt = filename+'.txt'

    page.original_scan = pjoin('Cyrilic_OCR', 'scan', file)
    
    page.filename = filename


    sdia = pjoin('Cyrilic_OCR', 'results',filename,'img_diacritics.jpg')
    if path.exists(sdia):
        page.selected_diacritics = sdia
        
        
    save_cor = pjoin('Cyrilic_OCR', 'results',filename,filename_txt)
    with codecs.open(save_cor, "w", encoding="utf-8") as f:
        f.write(modified_text)

    par_folder = pjoin('Cyrilic_OCR', 'results',filename,'paragraph')

    par_files = os.listdir(par_folder)
    list_of_paragraph = []
    for file in par_files:
        list_of_paragraph.append(pjoin(par_folder,file))

        page.plain_modified_content = modified_text
        
        

        
    context = {
               'page': page,
               'list_of_paragraph':list_of_paragraph
               }

    #return render(request, 'save_corrections.html', context)
    return render(request, 'show_result.html', context)
# end def save_corrections


def show_paragraph(request):
    scan_folder = pjoin('Cyrilic_OCR', 'scan')
    
    if request.method == 'GET':
        file = request.GET.get('file', 0)

    ppar = page_paragraphs()
    ppar.file = file
    
    pos1 = file.find('.')
    filename = file[:pos1]
    filename_txt = filename+'.txt'

    
    ppar.filename = filename

    lmap = pjoin('Cyrilic_OCR', 'results',filename,'line_map.txt')
    if path.exists(lmap):
        ppar.line_map = lmap
        
    pmod = pjoin('Cyrilic_OCR', 'results',filename,filename_txt)
    if path.exists(pmod):
        ppar.pmod = pmod
        
    pmod_lines = []
    with codecs.open(pmod, encoding='utf-8') as f:
        for line in f:
            pmod_lines.append(line.strip())



    f = open(lmap, 'r')
    lines_map = f.readlines()
      
    count = 0
    prev_par = -1
    lines_par = []
    cnt = 0
    for line in lines_map:
        s = line.strip()
        s = s.split(',')
        if (prev_par !=-1)and(prev_par != s[1]):
            ppar.par_lines.append(lines_par)
            ppar.par_imgs.append('paragraph\\'+'paragraph_'+s[1]+'.jpg')
            print ('#######################################')
            print(len(pmod_lines))
            print (str(lines_par))
            print ('paragraph\\'+'paragraph_'+s[1]+'.jpg')
            print ('#######################################')
            lines_par = []
        else:
            if (cnt<len(pmod_lines)):
                lines_par.append(pmod_lines[cnt])
        prev_par=s[1]

        cnt = cnt + 1
        
        print ('a',s[0],'b',s[1],s[2])

    print ('#######################################')
    print (len(pmod_lines))
    print (len(lines_map))
    print ('#######################################')

        
        

    context = {
               'ppar': ppar
               }
    return render(request, 'show_result.html', context)
# end def show_paragraph


def not_processed_pages(request):
    #current_path = os.path.realpath(__file__)
    
    scan_folder = pjoin('Cyrilic_OCR', 'scan')
    #results_folder = pjoin(current_path, 'Cyrilic_OCR', 'results')
    
    files = os.listdir(scan_folder)

    list_of_pages = []
    for file in files:
        page = scaned_page()
        page.file = file
        
        pos1 = file.find('.')
        filename = file[:pos1]
        filename_txt = filename+'.txt'

        page.original_scan = pjoin('Cyrilic_OCR', 'scan', file)
        
        #page.original_scan = file
        page.filename = filename

        sdia = pjoin('Cyrilic_OCR', 'results',filename,'img_diacritics.jpg')
        #print(sdia)
        if path.exists(sdia):
            page.selected_diacritics = sdia
        slett = pjoin('Cyrilic_OCR', 'results',filename,'selected_letters.jpg')
        if path.exists(slett):
            page.selected_letters = slett
        sword = pjoin('Cyrilic_OCR', 'results',filename,'selected_words.jpg')
        if path.exists(sword):
            page.selected_words = sword
        sline = pjoin('Cyrilic_OCR', 'results',filename,'selected_lines.jpg')
        if path.exists(sline):
            page.selected_lines = sline
        spar = pjoin('Cyrilic_OCR', 'results',filename,'selected_pargraph.jpg')
        if path.exists(spar):
            page.selected_pargraph = spar

        sav_cor = pjoin('Cyrilic_OCR', 'results',filename,filename_txt)
        if path.exists(sav_cor):
            page.save_corrections = sav_cor

        plain_mod = pjoin('Cyrilic_OCR', 'results',filename,filename_txt)
        if path.exists(plain_mod):
            page.plain_modified= plain_mod

        if path.exists(plain_mod)==False:
            list_of_pages.append(page)

    # Python Program to Get IP Address 
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    print("Your Computer Name is:" + hostname)
    print("Your Computer IP Address is:" + IPAddr)

    context = {
               'files': files,
               'list_of_pages':list_of_pages,
               'hostname':hostname,
               'IPAddr':IPAddr
               }
    return render(request, 'not_processed_pages.html', context)
# end def not_processed_pages


def process_in_paralell(pp_files, pp_rotate):
    print ('process_in_paralell')
    print (pp_files)
    print (pp_rotate)

    current_dir = os.getcwd()
    os.chdir(pjoin(current_dir,'Cyrilic_OCR'))
    script = pjoin('main_rotate.py')
    if len(pp_files)>0:
        p0 = subprocess.Popen(["python", script, pp_files[0], pp_rotate[0] ])
    if len(pp_files)>1:
        p1 = subprocess.Popen(["python", script, pp_files[1], pp_rotate[1] ])
    if len(pp_files)>2:
        p2 = subprocess.Popen(["python", script, pp_files[2], pp_rotate[2] ])
    if len(pp_files)>3:
        p3 = subprocess.Popen(["python", script, pp_files[3], pp_rotate[3] ])
    if len(pp_files)>4:
        p4 = subprocess.Popen(["python", script, pp_files[4], pp_rotate[4] ])
    if len(pp_files)>5:
        p5 = subprocess.Popen(["python", script, pp_files[5], pp_rotate[5] ])
    if len(pp_files)>6:
        p6 = subprocess.Popen(["python", script, pp_files[6], pp_rotate[6] ])
    if len(pp_files)>7:
        p7 = subprocess.Popen(["python", script, pp_files[7], pp_rotate[7] ])
    if len(pp_files)>8:
        p8 = subprocess.Popen(["python", script, pp_files[8], pp_rotate[8] ])
    if len(pp_files)>9:
        p9 = subprocess.Popen(["python", script, pp_files[9], pp_rotate[9] ])
    if len(pp_files)>10:
        p10 = subprocess.Popen(["python", script, pp_files[10], pp_rotate[10] ])
    if len(pp_files)>11:
        p11 = subprocess.Popen(["python", script, pp_files[11], pp_rotate[11] ])
    if len(pp_files)>12:
        p12 = subprocess.Popen(["python", script, pp_files[12], pp_rotate[12] ])
    if len(pp_files)>13:
        p13 = subprocess.Popen(["python", script, pp_files[13], pp_rotate[13] ])
    if len(pp_files)>14:
        p14 = subprocess.Popen(["python", script, pp_files[14], pp_rotate[14] ])
    if len(pp_files)>15:
        p15 = subprocess.Popen(["python", script, pp_files[15], pp_rotate[15] ])

    if len(pp_files)>0:
        p0.wait()
    if len(pp_files)>1:
        p1.wait()
    if len(pp_files)>2:
        p2.wait()
    if len(pp_files)>3:
        p3.wait()
    if len(pp_files)>4:
        p4.wait()
    if len(pp_files)>5:
        p5.wait()
    if len(pp_files)>6:
        p6.wait()
    if len(pp_files)>7:
        p7.wait()
    if len(pp_files)>8:
        p8.wait()
    if len(pp_files)>9:
        p9.wait()
    if len(pp_files)>10:
        p10.wait()
    if len(pp_files)>11:
        p11.wait()
    if len(pp_files)>12:
        p12.wait()
    if len(pp_files)>13:
        p13.wait()
    if len(pp_files)>14:
        p14.wait()
    if len(pp_files)>15:
        p15.wait()

    os.chdir(pjoin(current_dir))

    return 0

def ocr_not_processed_pages(request):
    if request.method == 'GET':
        rotate = request.GET.get('rotate', 0)
        print('rotate'+ str(rotate))
        
    scan_folder = pjoin('Cyrilic_OCR', 'scan')

    files = os.listdir(scan_folder)

    list_of_pages = []
    pp_files = []
    pp_rotate = []
    cnt = 0
    for file in files:
        pos1 = file.find('.')
        filename = file[:pos1]
        filename_txt = filename+'.txt'
        plain_mod = pjoin('Cyrilic_OCR', 'results',filename,filename_txt)
        if path.exists(plain_mod)==False:
            #page = ifun_ocr(file, rotate)
            cnt = cnt +1
            pp_files.append(file)
            pp_rotate.append(rotate)
            
            ###############
            page = scaned_page()

            pos1 = file.find('.')
            filename = file[:pos1]
            filename_txt = filename+'.txt'

            page.original_scan = pjoin('Cyrilic_OCR', 'scan', file)
            page.filename = filename

            sdia = pjoin('Cyrilic_OCR', 'results',filename,'img_diacritics.jpg')
            if path.exists(sdia):
                page.selected_diacritics = sdia
            ###############

            list_of_pages.append(page)
            if cnt==max_paralell:
                process_in_paralell(pp_files, pp_rotate)
                pp_files = []
                pp_rotate = []
                cnt = 0
    process_in_paralell(pp_files, pp_rotate)

    context = {
               'page': page,
               'file':file
               }
    return render(request, 'ocr_processing_completed.html', context)
# end ocr_not_processed_pages

def restore_ocr_text(request):
    if request.method == 'GET':
        file = request.GET.get('file', 0)
    pos1 = file.find('.')
    filename = file[:pos1]
    filename_txt = filename+'.txt'

    source = pjoin('Cyrilic_OCR', 'results', filename, filename+'_backup.txt')
    target = pjoin('Cyrilic_OCR', 'results', filename, filename_txt)
    shutil.copyfile(source, target)

    page = scaned_page()
    page.file = file

    page.original_scan = pjoin('Cyrilic_OCR', 'scan', file)

    page.filename = filename

    sdia = pjoin('Cyrilic_OCR', 'results',filename,'img_diacritics.jpg')
    if path.exists(sdia):
        page.selected_diacritics = sdia
        page.selected_diacritics = 'Cyrilic_OCR/results/'+filename+'/img_diacritics.jpg'

    slett = pjoin('Cyrilic_OCR', 'results',filename,'selected_letters.jpg')
    if path.exists(slett):
        page.selected_letters = slett
        page.selected_letters = 'Cyrilic_OCR/results/'+filename+'/selected_letters.jpg'
    sword = pjoin('Cyrilic_OCR', 'results',filename,'selected_words.jpg')
    if path.exists(sword):
        page.selected_words = sword
        page.selected_words = 'Cyrilic_OCR/results/'+filename+'/selected_words.jpg'
    sline = pjoin('Cyrilic_OCR', 'results',filename,'selected_lines.jpg')
    if path.exists(sline):
        page.selected_lines = sline
        page.selected_lines = 'Cyrilic_OCR/results/'+filename+'/selected_lines.jpg'
    spar = pjoin('Cyrilic_OCR', 'results',filename,'selected_pargraph.jpg')
    if path.exists(spar):
        page.selected_pargraph = spar
        page.selected_pargraph = 'Cyrilic_OCR/results/'+filename+'/selected_pargraph.jpg'

    spmod = pjoin('Cyrilic_OCR', 'results',filename,filename_txt)
    if path.exists(spmod):
        page.plain_modified = spmod
        f = open(spmod, 'r')
        file_content = ''
        with codecs.open(spmod, encoding='utf-8') as f:
            for line in f:
                file_content = file_content + line
        page.plain_modified_content = file_content

    par_folder = pjoin('Cyrilic_OCR', 'results',filename,'paragraph')

    par_files = os.listdir(par_folder)
    list_of_paragraph = []
    for file in par_files:
        list_of_paragraph.append(pjoin(par_folder,file))


    context = {
               'page': page,
               'list_of_paragraph':list_of_paragraph
               }
    return render(request, 'show_result.html', context)
