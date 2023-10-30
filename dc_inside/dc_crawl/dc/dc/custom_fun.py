import time
import requests, re
import json
from bs4 import BeautifulSoup

from fake_useragent import UserAgent
ua = UserAgent()

from datetime import datetime, timedelta

from tqdm import tqdm

import pandas as pd

import warnings
warnings.filterwarnings('ignore')

headers = {
    'user-agent' : ua.random
}

#갤러리 타입 가져오기(마이너, 일반)
def get_gallery_type(dc_id):
    #url로 requests를 보내서 redirect시키는지 체크한다.
    url = f'https://gall.dcinside.com/board/lists/?id={dc_id}'
    result = url
    
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")
    if "location.replace" in str(soup):
        redirect_url = str(soup).split('"')[3]
        result = redirect_url
    if "mgallery" in result:
        result = "mgallery/board"
    else:
        result = "board"
        
    return result

def make_galleryURL(gall_id):
    base_url = "https://gall.dcinside.com/"
    url = base_url + get_gallery_type(gall_id) + "/lists?id=" + gall_id

    return url


def get_comments(article_no):
    url = 'https://gall.dcinside.com/board/comment/'
    page = 1

    params  = {'id' : 'dcbest',
            "no" : article_no,
            'cmt_id' : 'dcbest',
            'cmt_no' : article_no,
            'e_s_n_o' : '3eabc219ebdd65f23d',
            'comment_page' : page,
            '_GALLTYPE_' : 'G'
    }


    headers = {
        "User-Agent" : ua.random,
        'X-Requested-With' : 'XMLHttpRequest',
        'Accept' : 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate, br'
    }

    try:
        with open('/home/sol4/workspace/dc_inside/dc_crawl/dc/dc/spiders/gall_comments.json', 'r') as f:
            comments = json.load(f)
    except:
        comments = dict()

    tmp = []

    while True:
        res = requests.post(url, data=params, headers = headers)
        if page == 1:
            commnet_max_page = int(res.json()['total_cnt'] / 100) + 1

        if page == commnet_max_page : break

        else:
            page += 1

            for cmt in res.json()['comments']:
                tmp.append(delTagBlank(cmt['memo']))

    comments[article_no] = tmp

    with open('/home/sol4/workspace/dc_inside/dc_crawl/dc/dc/spiders/gall_comments.json', 'w') as f:
        json.dump(comments, f)


def delTagBlank(txt):
    result = re.sub('(?<=\<).+(?=\>)', '' , txt)
    result = re.sub('[\t\r\n<>]+', '', result)
    result = re.sub('[ ]{2,}', ' ', result)
    return result