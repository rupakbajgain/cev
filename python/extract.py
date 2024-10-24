import requests
from bs4 import BeautifulSoup
import os, json
import shutil

baseURL = 'https://www.examveda.com'

def handle_image(u):
    url = baseURL+u
    filename = '../data_img/'+'_'.join(u.split('/')[-2:])
    if os.path.exists(filename):
        return filename
    response = requests.get(url, stream=True)
    print('Image', filename)
    with open(filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    return filename

def get_content(e):
    rc=[]
    for i in e.contents:
        s = i.string
        if not s:
            s=i.get_text()
        if i.name==None:
            if s.startswith('$$'):
                rc.append(['math', s[2:-2]])
            else:
                rc.append(['span', s])
        elif i.name=='p' or i.name=='i' or i.name=='sup' or i.name=='span' or i.name=='sub' or i.name=='b':
            rc.append([i.name, s])
        elif i.name=='img':
            rc.append(['img', handle_image(i['src'])])
        elif i.name=='br':
            rc.append(['br'])
        elif i.name=='t':
            rc.append(['span', s])
        elif i.name=='pi<':
            rc.append(['span', '< pi <'])
        elif i.name=='pi<27<':
            rc.append(['span', '< pi < 27 <'])
        elif i.name=='where':
            rc.append(['span', 'where l is the length of port ship the to use'])
        else:
            print(i)
            raise i.name
    return rc

def crawl_page(u):
    soup=u
    if isinstance(u, str):
        print(u)
        url = u
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
    q_s = soup.findAll("article", {"class": 'question'})
    o=[]
    for i in q_s:
        q_main = i.find("div", {"class": 'question-main'})
        if not q_main:
            continue
        q_inner = i.find("div", {"class": 'question-inner'})
        q_ans = i.find("div", {"class": 'answer_container'})
        r={}
        r['que'] = get_content(q_main)
        options =[]
        for i in q_inner.findAll('p'):
            if i.get('class') == ['hidden']:
                continue
            options.append(get_content(i.contents[5]))
        r['options']=options
        r['ans'] = q_ans.find('strong').text.strip()[-1:]
        explanation = q_ans.contents[1].contents[1].contents[5]
        if not explanation.text.strip()=='No explanation is given for this question  Let\'s Discuss on Board':       
            r['explanation'] = explanation.contents[2].text
            print(r['explanation'])
        o.append(r)
    return o

def crawl_section(u):
    soup=u
    if isinstance(u, str):
        print(u)
        url = u
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
    pagination = soup.find("div", {"class": 'pagination'})
    links = pagination.findAll("a")
    arr = crawl_page(soup)
    for i in links[:-1]:
        arr.extend(crawl_page(i['href']))
    return arr

def crawl_categories(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    arr = [crawl_section(soup)]
    s = soup.find('ul', {'class': 'more-section'})
    if not s:
        return arr
    for i in s.findAll('a'):
        arr.append(crawl_section(i['href']))
    return arr

def crawl_main():
    url = baseURL+'/mcq-question-on-civil-engineering/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    categories_div = soup.find_all("article", {"class": 'col-sm-12 margin-top-10'})
    for k in categories_div:
        url= k.h3.a['href']
        title= k.h3.a.text.strip()
        filename = f"../data/{title}.json"
        print(title)
        if not os.path.exists(filename):
            p = crawl_categories(url)
            with open(filename, 'w') as f:
                json.dump(p, f)

def main():
    crawl_page('https://www.examveda.com/civil-engineering/practice-mcq-question-on-theory-of-structures/');

if __name__ == "__main__":
    crawl_main()
    #main()
