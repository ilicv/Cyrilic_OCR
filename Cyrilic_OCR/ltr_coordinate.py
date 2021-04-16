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


class coordinate:
    def __init__(self):
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.xc = 0
        self.yc = 0

        self.let_width = 0
        self.let_height = 0

        self.letter = ' '
        self.letter_id = 0

        self.img_name = ''
        self.str_coords = ''

        self.found_in = ''
        self.location = ''
        self.ocr_letter = ''
        self.w_coord = ''
        self.ip_line_pos = ""
        self.ip_word_pos = ""
        self.diacritic = 0
        self.superscript = 0
        self.pos_in_word = 0
        self.line_id = 0
        self.word_id = 0

    def copy_from(self, x):
        self.x1 = x.x1
        self.x2 = x.x2
        self.y1 = x.y1
        self.y2 = x.y2

        self.xc = x.xc
        self.yc = x.yc

        self.let_width = x.let_width
        self.let_height = x.let_height

        self.str_coords = x.str_coords
        self.letter = x.letter
        self.letter_id = x.letter_id
        self.img_name = x.img_name
        self.found_in = x.found_in
        self.location = x.location
        self.ocr_letter = x.ocr_letter

        self.ip_line_pos = x.ip_line_pos
        self.ip_word_pos = x.ip_word_pos

        self.w_coord = x.w_coord 

        self.diacritic = x.diacritic
        self.superscript = x.superscript
        self.pos_in_word = x.pos_in_word

        self.line_id = x.line_id
        self.word_id = x.word_id

    def to_str(self):
        self.str_coords = set_tag('let_width',str(self.let_width))+set_tag('let_height',str(self.let_height))+ set_tag('xc',str(self.xc))+set_tag('yc',str(self.yc))+set_tag('x1',str(self.x1))+set_tag('y1',str(self.y1))+set_tag('x2',str(self.x2))+set_tag('y2',str(self.y2))

        s = set_tag('letter_id',str(self.letter_id))+ set_tag('letter',self.letter) +set_tag('ocr_letter',self.ocr_letter) + set_tag('img_name', self.img_name)
        s = s + set_tag('diacritic',str(self.diacritic)) +set_tag('superscript',str(self.superscript)) + set_tag('str_coords',self.str_coords) +set_tag('location',self.location) +set_tag('found_in',self.found_in) + set_tag('w_coord',self.w_coord)
        return s

    def load_from_str(self, s):
        self.line_id = get_tag('wline_id', s)
        self.word_id = get_tag('wwrd_id', s)

        self.letter_id = get_tag('letter_id', s)
        self.letter = get_tag('letter', s)
        self.ocr_letter = get_tag('ocr_letter', s)
        self.img_name = get_tag('img_name', s)

        self.xc = get_tag('xc', s)
        self.yc = get_tag('yc', s)
        self.x1 = int(get_tag('x1', s))
        self.y1 = int(get_tag('y1', s))
        self.x2 = int(get_tag('x2', s))
        self.y2 = int(get_tag('y2', s))
        self.location = get_tag('location', s)

        self.diacritic= int(get_tag('diacritic', s))
        self.superscript= int(get_tag('superscript', s))

        self.ip_line_pos =int(get_tag('wip_line_pos', s))
        self.ip_word_pos =int(get_tag('wip_word_pos', s))

        self.found_in = get_tag('wfound_in', s)

        self.w_coord = get_tag('w_coord', s)
        self.str_coords = get_tag('str_coords', s)


    def update_srt_coords(self):
        self.xc = (self.x1 + self.x2) / 2
        self.yc = (self.y1 + self.y2) / 2

        self.let_width = (self.x2 - self.x1)
        self.let_height = (self.y2 - self.y1)
