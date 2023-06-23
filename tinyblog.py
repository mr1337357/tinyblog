import os
import sys
import shutil
from string import Template

articles = {}

class article:
    def __init__(self,filename,config):
        self.filename = filename
        self.meta = {}
        self.meta['blogname'] = config.configs['blogname']
        self.text=[]
        self.load()
        
    def read_meta(self,meta):
        assign = meta.split('=')
        if len(assign) == 2:
            name = assign[0]
            start = assign[1].find('\'') + 1
            end = assign[1].find('\'',start)
            value = assign[1][start:end]
            self.meta[name] = value
        
    def load(self):
        infile = open(self.filename,'r')
        for line in infile.readlines():
            line = line[:-1] #I prefer to remove EOL
            if line.startswith('<!--TBLOG ') and line.endswith('-->'):
                meta = line[10:-3]
                self.read_meta(meta)
            else:
                self.text.append(line)
                
    def __lt__(self,other):
        return self.meta['date'] > other.meta['date']

class config:
    def __init__(self):
        self.configs = {}
        configfile = open('articles/config.ini','r')
        for line in configfile.readlines():
            line = line[:-1]
            s = line.split('=')
            if len(s) == 2:
                self.configs[s[0]]=s[1]
        
def make_filename(article):
    return '{}-{}.html'.format(article.meta['date'],article.meta['title'])
        
def make_navi(articles,count=3):
    navi = ''
    if count < 1 or count > len(articles):
        count = len(articles)
    for i in range(count):
        article=articles[i]
        navi += '<a href="{}">{}</a><br>'.format(make_filename(article),article.meta['title'])
    return navi
        
def make_articles(template,articles):
    navi = make_navi(articles)
    for article in articles:
        article.meta['navi'] = navi
        article.meta['text'] = ''.join(article.text)
        filecontent = template.substitute(article.meta)
        outfile = open('blog/{}-{}.html'.format(article.meta['date'],article.meta['title']),'w')
        outfile.write(filecontent)

def make_index(template,articles,config):
    bloginfo = {}
    navi = make_navi(articles,0)
    bloginfo['navi']=navi
    bloginfo['blogname']=config.configs['blogname']
    for i in range(3):
        if len(articles) <= i:
            bloginfo['fn'+str(i+1)] = ''
            bloginfo['title'+str(i+1)] = ''
            bloginfo['date'+str(i+1)] = ''
            bloginfo['text'+str(i+1)] = ''
        else:
            bloginfo['fn'+str(i+1)] = make_filename(articles[i])
            bloginfo['title'+str(i+1)] = articles[i].meta['title']
            bloginfo['date'+str(i+1)] = articles[i].meta['date']
            bloginfo['text'+str(i+1)] = articles[i].meta['text']
    filecontent = template.substitute(bloginfo)
    outfile = open('blog/index.html','w')
    outfile.write(filecontent)

if __name__ == '__main__':
    configfile = config()
    articles = []
    if not os.path.isdir('articles'):
        os.mkdir('articles')
    if not os.path.isdir('blog'):
        os.mkdir('blog')
    for file in os.listdir('articles'):
        if not file.endswith('.txt'):
            continue
        a = article('articles/' + file,configfile)
        articles.append(a)
    articles.sort()
    article_template_text = ''.join(open('template/article.html','r').readlines())
    article_template = Template(article_template_text)
    make_articles(article_template,articles)
    index_template_text = ''.join(open('template/index.html','r').readlines())
    index_template = Template(index_template_text)
    make_index(index_template,articles,configfile)
    shutil.copyfile('template/article.css','blog/article.css')
    shutil.copyfile('template/index.css','blog/index.css')
