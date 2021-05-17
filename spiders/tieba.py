# 一个简单的增量式爬虫，用于增量式爬取百度某吧的前5页内容
import requests
import scrapy
import time
import requests
import json
import hashlib
import redis
from lxml import etree
import xml.etree.ElementTree as ET
from tiebaSpider.IPProxy import IPProxy
from tiebaSpider.items import TieItem
from tiebaSpider.items import FloorItem
from tiebaSpider.items import FloorFloorItem
class TiebaSpider(scrapy.Spider):
    name = 'tieba'
    last_update_time = 0
    pool = None
    redis = None
    page_urls = [
                    "https://tieba.baidu.com/f?kw=%E6%8A%97%E5%8E%8B%E8%83%8C%E9%94%85&ie=utf-8",
                    "https://tieba.baidu.com/f?kw=%E6%8A%97%E5%8E%8B%E8%83%8C%E9%94%85&ie=utf-8&pn=50",
                    "https://tieba.baidu.com/f?kw=%E6%8A%97%E5%8E%8B%E8%83%8C%E9%94%85&ie=utf-8&pn=100",
                    "https://tieba.baidu.com/f?kw=%E6%8A%97%E5%8E%8B%E8%83%8C%E9%94%85&ie=utf-8&pn=150",
                    "https://tieba.baidu.com/f?kw=%E6%8A%97%E5%8E%8B%E8%83%8C%E9%94%85&ie=utf-8&pn=200"]
    start_urls = ["https://tieba.baidu.com/f?kw=%E6%8A%97%E5%8E%8B%E8%83%8C%E9%94%85&ie=utf-8"]

    def parse(self, response):
        self.pool = redis.ConnectionPool(host="127.0.0.1",port = 6379,password="",max_connections=42)
        self.redis = redis.Redis(connection_pool=self.pool,decode_responses=True)
        
        for i in self.page_urls: 
            yield scrapy.Request(i, callback = self.parse_page, dont_filter = True)

        used_time = int(time.time()) - self.last_update_time

    def parse_page(self, response):
        #从前5页解析出帖子的网址
        urls = response.xpath("//a[@class='j_th_tit ']/@href").extract()
        for url in urls:
            full_url = "https://tieba.baidu.com" + url
            yield scrapy.Request(full_url, callback = self.parse_tie, dont_filter=True)
        
    def parse_tie(self, response):
        tie_id = response.url.split('/')[-1]
        title = response.xpath("//h3[@class='core_title_txt pull-left text-overflow  ']/@title").extract_first()
        time = response.xpath("//span[contains(text(), '楼') and contains(@class, 'tail-info')]/following-sibling::span[1]/text()").extract_first()
        author = response.xpath('//a[contains(@class,"p_author_name") and contains(@class,"j_user_card")]/text()').extract_first()
        if (self.redis.sadd("tie", tie_id)): #判断是否是新贴
            yield from self.save_tie(tie_id=tie_id,author=author,title=title,time=time)
        pages = response.xpath("//li[@class='l_reply_num']/span[@class='red']/text()").extract()[1]
        for page in range(1, int(pages)+1):
            yield scrapy.Request(response.url+"?pn="+str(page), callback=self.parse_tie_pages,dont_filter=True)
        

    def parse_tie_pages(self, response):
        #解析出帖子每页的数据
        p = response.url.split('/')[-1]
        pid = p.split('?')[0]
        page_num = p.split('=')[-1]
        total_comments_params = {
            "fid": "177019292",
            "tid": pid,
            "pn": page_num,
            "see_lz": '0',
            "t": str(int(time.time()))
        }
        r = requests.get("https://tieba.baidu.com/p/totalComment", params = total_comments_params, proxies = IPProxy.getIp())
        comments = json.loads(r.text)['data']['comment_list']
        floors = response.xpath("//div[@class='l_post l_post_bright j_l_post clearfix  ']")
        for floor in floors:
            floor_num = floor.xpath(".//span[contains(text(), '楼') and contains(@class, 'tail-info')]/text()").extract_first()[:-1]
            floor_time = floor.xpath(".//span[contains(text(), '楼') and contains(@class, 'tail-info')]/following-sibling::span[1]/text()").extract_first()
            floor_author = floor.xpath('.//a[contains(@class,"p_author_name") and contains(@class,"j_user_card")]/text()').extract_first()
            floor_content = floor.xpath(".//div[contains(@class,'d_post_content') and contains(@class,'j_d_post_content ')]/text()").extract_first().strip()
            floor_id = floor.xpath("./@data-pid").extract_first()
            
            if (self.redis.sadd("floor","tie_id: "+pid+"floor_num: "+floor_num)): #判断是否是新楼
                yield from self.save_floor(tie_id=pid,floor_num=floor_num,author=floor_author,content=floor_content,time=floor_time)
            if (floor_id in comments):
                for c in comments[floor_id]['comment_info']:
                    #楼中楼
                    ff_author = c['username']
                    ff_time = str(c['now_time'])
                    ff_content = c['content']
                    ff_id = hashlib.md5((ff_author+ff_time+ff_content).encode(encoding = 'UTF-8')).hexdigest()
                    
                    if (self.redis.sadd("floorfloor", "tie_id: " + pid + "floor_num: "+floor_num +"ff_id: "+str(ff_id))): #判断是否是新楼中楼
                        yield from self.save_floor_floor(tie_id=pid,floor_num=floor_num,author=ff_author,content=ff_content,time=ff_time)
                floor_page_num = 2
                flag = True
                while flag: #楼中楼多于一页的数据
                    f_params = {
                        "tid": pid,
                        "pid": floor_id,
                        "pn": str(floor_page_num),
                        "t": str(int(time.time()))
                    }
                    f_r = requests.get("https://tieba.baidu.com/p/comment", params=f_params, proxies = IPProxy.getIp())
                    f_html = etree.HTML(f_r.text)
                    f_comments = f_html.xpath("//li[contains(@class, 'lzl_single_post')]")
                    if len(f_comments) == 0:
                        flag = False
                        break
                    for f in f_comments:
                        f_comment = etree.HTML(ET.tostring(f))
                        ff_author = f_comment.xpath("//a[@class='at j_user_card ']/text()")[0]
                        ff_content = f_comment.xpath("//span[@class='lzl_content_main']")[0].xpath('string(.)').strip()
                        ff_time = f_comment.xpath("//span[@class='lzl_time']/text()")[0]
                        ff_id = hashlib.md5((ff_author+ff_time+ff_content).encode(encoding = 'UTF-8')).hexdigest()
                        
                        if (self.redis.sadd("floorfloor", "tie_id: "+ pid+ "floor_num: "+ floor_num+"ff_id: "+ str(ff_id))): #判断是否是新楼中楼
                            yield from self.save_floor_floor(tie_id=pid,floor_num=floor_num,author=ff_author,content=ff_content,time=ff_time)
                    floor_page_num = floor_page_num + 1

    def save_tie(self, **kwargs):
        item = TieItem()
        item['tie_id'] = kwargs['tie_id']
        item['author'] = kwargs['author']
        item['title'] = kwargs['title']
        item['time'] = kwargs['time']
        yield item

    def save_floor(self, **kwargs):
        item = FloorItem()
        item['tie_id'] = kwargs['tie_id']
        item['floor_num'] = kwargs['floor_num']
        item['author'] = kwargs['author']
        item['content'] = kwargs['content']
        item['time'] = kwargs['time']
        yield item

    def save_floor_floor(self, **kwargs):
        item = FloorFloorItem()
        item['tie_id'] = kwargs['tie_id']
        item['floor_num'] = kwargs['floor_num']
        item['author'] = kwargs['author']
        item['content'] = kwargs['content']
        item['time'] = kwargs['time']
        yield item