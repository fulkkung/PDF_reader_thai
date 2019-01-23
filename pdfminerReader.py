import codecs
import io
from pythainlp.spell import spell
from pylexto import LexTo

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from tika import parser

import re

def extract_text_from_pdf(pdf_path,layout=True):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
        # laparams = LAParams(line_margin=1, word_margin=10, char_margin=40, boxes_flow=1)
        # converter = TextConverter(resource_manager, fake_file_handle, laparams=laparams)
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
 
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, 
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
 
        text = fake_file_handle.getvalue()
 
    # close open handles
    converter.close()
    fake_file_handle.close()
 
    if text:
        return text
def thai_distributed_spacing_formatter(text):
    """
    remove the additional white space within the line that align with thai-distributed
    """
    # the Thai-distributed modified the text when the line has a space.
    # the gap between character is greater than normal.
    # therefore, the pdfminer is detected as a space.

    data = text

    return data

def regex_formatter(text):
    data = text
    # manage aum vowel
    b = 0
    aum_format = [' า',' ่า',' ้า',' ๊า',' ๋า','้่า','่่า','๊่า','๋่า']
    replacer = ['ำ','่ำ','้ำ','๊ำ','๋ำ','้ำ','่ำ','๊ำ','๋ำ']
    expand = 10
    for i in range(len(aum_format)): 
        b=0 # search from start document       
        ind = data.find(aum_format[i],b)
        while(ind != -1):
            # print("s--"+data[ind-expand:ind+expand])
            data = data[:ind]+ replacer[i] + data[ind+len(aum_format[i]):]
            # print("t--"+data[ind-expand:ind+expand])
            b = ind
            ind = data.find(aum_format[i],b)
    # print(data)
    # fragment = data.split(" ")
    # for i in range(len(fragment)):
    #     if(re.match('.*[ิืึีั]$',fragment[i])):
    #         print(fragment[i],fragment[i+1])
        
    l = [m.start() for m in re.finditer('([ิืึีั]) ', data)]
    # print(l)
    
    for ind in l:
        # print("s "+data[ind-expand:ind+expand])
        data = data[:ind+1]+ '่' + data[ind+2:]
        # print("t "+data[ind-expand:ind+expand])
    return data
def dictionary_formatter(text):
    data = text

    f = codecs.open("aum_list.txt","r","utf-8")
    doc = f.read()
    f.close()
    aum_list = doc.split("\n")

    f = codecs.open("aum_typo_list.txt","r","utf-8")
    doc = f.read()
    f.close()
    aum_typo_list = doc.split("\n")
    
    for i in range(len(aum_typo_list)):
        if aum_typo_list[i] in data and len(aum_typo_list[i]) > 3:
            # print(aum_typo_list[i],aum_list[i])
            data = data.replace(aum_typo_list[i],aum_list[i])

    lexto = LexTo()
    words, types = lexto.tokenize(data)
    # print(words)
    zz = zip(words,types)
    doc = ''
    for w,t in zz:
        if t == 'unknown' and w[-1] == '่':
            print(w[:-1])
            w = w[:-1]
        doc += w
    data = doc
    data.replace('เทำ','เท่า')
    return data
def extract_pdf(fname):
    data = extract_text_from_pdf(fname)
    # print("->"+data)
    data = regex_formatter(data)
    data = dictionary_formatter(data)
    return data