# -*- coding: utf-8 -*-
import scrapy

class NcovSpider(scrapy.Spider):
    name = 'ncov'
    allowed_domains = ['ncov.moh.gov.vn']
    start_urls = ['https://ncov.moh.gov.vn/web/guest/dong-thoi-gian/']

    def parse(self, response):
        timeline = response.xpath("/html/body/div[1]/div/div/div[2]/div/div/div/div/div/div/div[1]/div/div/section/div/div/div/div[3]/div/div/div/div/ul")
        for news in timeline:
            time = news.css("div.timeline-detail > div.timeline-head > h3::text").get()
            content = news.css("div.timeline-detail > div.timeline-content > p::text").get()
            link = response.request.url.split('?')[0]
            yield {'time': time, 'content': content, 'link': link}

        next_page = response.xpath("/html/body/div[1]/div/div/div[2]/div/div/div/div/div/div/div[1]/div/div/section/div/div/div/div[4]/ul/li[2]/a")
        yield from response.follow_all(next_page)

