import scrapy
import time
from datetime import datetime
from dc.items import DcItem
from dc.custom_fun import *

class DcSpider(scrapy.Spider):
    name = "dc"
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES' : {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
        }
    }
    
    def __init__(self, **kwargs):
        with open('/home/sol4/workspace/dc_inside/dc_crawl/dc/dc/spiders/target_gall.txt', 'r') as f:
            gall_ids = f.readlines()

        with open('/home/sol4/workspace/dc_inside/dc_crawl/dc/dc/spiders/last_crawl_time.txt', 'r') as f:
            self.lastCrawlTime = f.readline()

        st = time.localtime()
        dt = datetime(*st[:6])
        with open('/home/sol4/workspace/dc_inside/dc_crawl/dc/dc/spiders/last_crawl_time.txt', 'w') as f:
            f.write(str(dt))

        self.url_lst = []
        for gall_id in gall_ids:
            gall_id = re.sub('\n', '', gall_id)
            self.url_lst.append(make_galleryURL(gall_id))
        
        super().__init__(**kwargs)
        
    def start_requests(self):

        # 2페이지 클롤링 / 페이지당 게시글 100개 총 1000개의 게시글 크롤링
        for url in self.url_lst:
            # print('START CRAWL : ' + url)
            for page in range(1,550):
                gall_url = url + "&page=" + str(page) + "&list_num=100"
                yield scrapy.Request(gall_url, callback=self.parse, meta = { 'url' : url })
        
    def parse(self, response):
        links = response.xpath('//*[@class="ub-content us-post"]/td[@class="gall_tit ub-word"]/a[1]/@href').extract()
        writed_at = response.xpath('//*[@class="ub-content us-post"]/td/@title').extract()
        # print('LINKS LEN : ', len(links),  ' WRITED_AT LEN : ', len(writed_at), ' TYPE : ', type(writed_at))
        # print('RESPONSE URLJOIN : ', links)
        links = list(map(response.urljoin, links))
        
        for idx, link in enumerate(links):

            if writed_at[idx] < self.lastCrawlTime :
                # print("PASSING POST!! writed_at : ", writed_at)
                continue

            yield scrapy.Request(link, callback=self.page_parse, meta={**response.meta})
    
    def page_parse(self, response):
        item = DcItem()
        item["title"] = response.xpath('//*[@class="gallview_head clear ub-content"]/h3/span[2]/text()').extract_first()
        
        contents = response.xpath('//*[@class="write_div"]/p/text()').extract()
        post = ''
        for content in contents:
            content = re.sub('[\n\t]', '', content)
            content += '\n'
            post += content
        item['content'] = post[:-2]

        item["date"] = response.xpath('//*[@class="gall_date"]/text()').extract_first()
        item["views"] = response.xpath('//*[@class="fr"]/span[1]/text()').extract_first()[3:]
        item["recommend"] = response.xpath('//*[@class="gall_reply_num"]/text()').extract_first()[3:]
        item["link"] = response.url
        
        url = response.meta.pop('url')
        #item['gall_code'] = re.search('(?<=id=).+', url).group(0)
        
        article_no = int(re.search('(?<=no=)[0-9]+', response.url).group(0))
        item['article_no'] = article_no
        get_comments(article_no)
        
        time.sleep(0.75)

        yield item
