# import os
# import asyncio
# import aiofiles
# import pandas as pd
# import httpx
# from parsel import Selector

import requests
from bs4 import BeautifulSoup

urls=[f'https://news.nankai.edu.cn/mtnk/system/count//0006000/000000000000/000/000/c0006000000000000000_000000{i}.shtml' for i in range(968,969)]
urls.append('https://news.nankai.edu.cn/mtnk/index.shtml')#幽默南开新闻网怎么首页的结构不一样

res_dict={}#URL->text

def crawlIndex(urls):
    cnt=0
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
                print(f"href: {href}, text: {text}")
                res_dict[href]=text

if __name__=='__main__':
    crawlIndex(urls=urls)          
# 'https://news.nankai.edu.cn/mtnk/index.shtml'        

