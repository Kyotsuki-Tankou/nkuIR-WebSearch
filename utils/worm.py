import requests
import os
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor,as_completed

urls=[f'https://news.nankai.edu.cn/mtnk/system/count//0006000/000000000000/000/000/c0006000000000000000_000000{i}.shtml' for i in range(965,969)]
urls.append('https://news.nankai.edu.cn/mtnk/index.shtml')#幽默南开新闻网怎么第一页的结构不一样

title2url_df=pd.DataFrame(columns=['url'])
title2url_df.index.name='title'

res_dict={}#URL->text
href_urls=[]

def crawlIndex(urls):
    cnt=0
    href_urls=[]
    for url in urls:
        cnt+=1
        print(f"{cnt} : Processing Page: {url}")
        response=requests.get(url)
        if(response.status_code==200):
            soup=BeautifulSoup(response.content,'html.parser')
            links=soup.find_all('a',href=True,target="_blank")
            for link in links:
                href=link['href']
                text=link.get_text().replace('/','^')
                # print(f"href: {href}, text: {text}")
                res_dict[href]=text
                href_urls.append(href)
    return href_urls

def procPage(url):
    if 'pages' not in os.listdir():
        os.mkdir('./pages')
    try:
        if url.startswith('http') or url.startswith('https'):
            response = requests.get(url)
            soup=BeautifulSoup(response.content,'html.parser')
            if soup.title:
                title_text=soup.title.string.replace('-媒体南开-南开大学','').replace('/','^')
                print(f'Title:{title_text}')
                if len(title_text)>0:
                    filepath=f'pages/{title_text}.html'
                    with open(filepath,'w',encoding='utf-8') as f:
                        f.write(str(soup.prettify()))
                    title2url_df.loc[title_text]=url
                
    except:
        print(f"error in {url}")
        
def do_page(url_list,max_worker=10):
    cnt=0
    url_list=list(set(url_list))
    # for url in url_list:
    #     cnt+=1
    #     print(f"{cnt}/{len(url_list)} : Processing Page: {url}")
    #     procPage(url)
    with ThreadPoolExecutor(max_workers=max_worker) as executor:
        future2url={executor.submit(procPage,url): url for url in url_list}
        for future in as_completed(future2url):
            url=future2url[future]
            try:
                future.result()
                cnt+=1
                print(f'{cnt}/{len(url_list)} completed.')
            except Exception as exc:
                print(f"{url} generated an exception: {exc}")
        
        
if __name__=='__main__':
    # crawlIndex(urls=urls)      \
    # procPage("https://news.nankai.edu.cn/mtnk/system/2024/12/01/030064788.shtml")  
    href_urls=crawlIndex(urls=urls)
    do_page(href_urls)
    title2url_df.to_csv("title2url.csv")
# 'https://news.nankai.edu.cn/mtnk/index.shtml'        

