import os
import json
from os import listdir
import latexcodec
# importing the module
import PIL
from PIL import Image

tex_start = '''\\documentclass[11pt,a4paper]{article}
\\usepackage[inline]{enumitem}
\\usepackage{amsmath}
\\usepackage{graphicx}

\\setlist{itemsep=0mm,topsep=0px,itemsep=0px}

\\begin{document}

\\pagenumbering{gobble}
\\tableofcontents
'''

# Yield successive n-sized
# chunks from l.
def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

dir_data = '../data'

def generate_tex(a):
    o = ''
    last_br = False
    for i in a:
        if i[0]=='span':
            o+=to_latex(i[1])
        elif i[0]=='p':
            if not i[1]:
                continue#more deep contents
            o+=f'\\par {to_latex(i[1])}\n'
        elif i[0]=='i':
            o+='\\emph{'+to_latex(i[1])+'}'
        elif i[0]=='b':
            o+='\\textbf{'+to_latex(i[1])+'}'
        elif i[0]=='sup':
            o+='\\^{}'+f'{to_latex(i[1])}'
        elif i[0]=='sub':
            o+=f'\\_ {to_latex(i[1])}'
        elif i[0]=='img':
            o+='\\includegraphics{'+i[1]+'}\n'
        elif i[0]=='br':
            o+=' \\\\\n'
        elif i[0]=='math':
            o+=f'$ {i[1]} $'
        else:
            print(i)
            raise i
    return o

def explanations(d, f):
    des = []
    for c, i in enumerate(d):
        if 'explanation' in i:
            des.append([c,i['explanation']])
    if len(des):
        f.write('\\\\\\textbf{Explanation}\\\\\n')
        for i in des:
            if(i[1][:2]=='$$'):
                f.write(str(i[0]+1)+'.'+i[1]+'\n')
            else:
                f.write(str(i[0]+1)+'.'+to_latex(i[1])+'\n')

def answer_key(d, f):
    f.write('\\textbf{Answer Key}\n')
    f.write('\\begin{tabular}{ | c | c c c c c c c c c c | }\n')
    f.write('\\hline\n')
    f.write(' & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 0 \\\\\n')
    f.write('\\hline\n')
    ans = []
    for i in d:
        ans.append(i['ans'])
    ans = list(divide_chunks(ans, 10))
    for c, i in enumerate(ans):
        f.write(str(c*10)+' ')
        for j in i:
            f.write(f'& {j} ')
        for j in range(10-len(i)):
            f.write('&   ')
        f.write('\\\\\n')
    f.write('\\hline\n')
    f.write('\\end{tabular}\n')
    explanations(d, f)

def get_length(k):
    l=0
    for i in k:
        if i[0]=='span' or i[0] == 'i' or i[0] == 'sup' or i[0]=='sup' or i[0]=='p' or i[0]=='b':
            l+=len(i[1])+4
        elif i[0]=='br':
            pass
        elif i[0]=='img':
            #assume mono even when not
            try:
                img = PIL.Image.open(i[1])
                wid, _ = img.size
                l+=wid/12
            except:
                pass
    return l

def determine_short(o):
    l = map(get_length, o)
    m = max(l)
    s = sum(l)
    measure =73#just guess
    if s>measure:
        return False
    elif m>measure/4:
        return False
    return True

def to_latex(s):
    """s=s.replace('∝','$\\propto$')
    s=s.replace('≅','$\\cong$')
    s=s.replace('⊥','$\\bot$')
    s=s.replace('φ','$\\phi$')
    s=s.replace('γ','$\\gamma$')
    s=s.replace('^','\\^{}')
    """
    try:
        return s.encode('latex').decode()
    except:
        return s

def generate_tex_q(t):
    l = generate_tex(t)
    if l[:4]=='\\par':
        return l[5:]
    return l

def dump_section(data, f):
    f.write('\\begin{enumerate}\n')
    for i in data:
        f.write('\\item{'+generate_tex_q(i['que'])+'}\n')
        is_short = determine_short(i['options'])
        if is_short:
            f.write('\\\\\\begin{enumerate*}[itemjoin=\\qquad, label=\\Alph*.]\n')
        else:
            f.write('\\begin{enumerate}[label=\\Alph*.]\n')
        for j in i['options']:
            f.write('\\item{'+generate_tex(j)+'}\n')
        if is_short:
            f.write('\\end{enumerate*}\n')
        else:
            f.write('\\end{enumerate}\n')
    f.write('\\end{enumerate}\n')
    answer_key(data, f)

def dump_chapter(path, f):
    f1 = open(path)
    data = json.load(f1)
    f1.close()
    for c, i in enumerate(data):
        if(c):
            f.write('\\clearpage\n')
        f.write('\\subsection*{Section '+str(c+1)+'}\n')
        dump_section(i, f)

def main():
    f = open("../tex/main.tex", "w")
    f.write(tex_start)
    f.write('\\clearpage\n')
    f.write('\\pagenumbering{arabic}\n')
    for filename in listdir(dir_data):
        title = filename[:-5]
        if title in ['Railway Engineering','Docks and Harbor Engineering','Elements of Remote Sensing','Highway Engineering','Airport Engineering','SI Units','Hydraulics and Fluid Mechanics','Advanced Surveying','Water Supply Engineering','Design of Steel Structures','Structural Design Specifications','Waste Water Engineering','Irrigation Engineering']:
            continue
        f.write('\\clearpage\n')
        f.write('\\section{'+title+'}\n')
        dump_chapter(f'{dir_data}/{filename}', f)
    f.write('\\end{document}')
    f.close()

if __name__ == "__main__":
    main()
