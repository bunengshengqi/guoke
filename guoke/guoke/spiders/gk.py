# -*- coding: utf-8 -*-
import scrapy
from pprint import pprint   # 美化打印ppprint

class GkSpider(scrapy.Spider):
    name = 'gk'
    allowed_domains = ['guokr.com']
    start_urls = ['https://www.guokr.com/ask/highlight/']

    def parse(self, response):
        # 先分组,再提取
        li_list = response.xpath('//div[@class="gmain"]/ul[@class="ask-list-cp"]/li')
        for li in li_list:
            item = {}
            item["focus_nums"] = li.xpath('.//p[@class="ask-focus-nums"]/span/text()').extract_first()
            item["answer_list"] = li.xpath('.//p[@class="ask-answer-nums"]/span/text()').extract_first()
            item["title"] = li.xpath('./div[@class="ask-list-detials"]/h2/a/text()').extract_first()
            item["href"] = li.xpath('./div[@class="ask-list-detials"]/h2/a/@href').extract_first()
            item["tag"] = li.xpath('.//div[@class="ask-list-legend"]/p/a/text()').extract()
            item["summary"] = li.xpath('.//p[@class="ask-list-summary"]/text()').extract_first().strip()
            # print(item)
            # 进入详情页
            yield scrapy.Request(
                item["href"],
                callback=self.parse_detail,
                meta={"item": item}
            )

        # 请求下一页,
        # 获取下一页的url地址
        next_url = response.xpath('//a[text()=下一页]/@href').extract_first()
        if next_url is not None:
            yield response.follow(next_url, callback=self.parse)  # 自动补全url地址

    def parse_detail(self, response):
        item = response.meta["item"]
        # item["answer_num"] = response.xpath('//span[@class="answers-num gfl"]/text()').extract_first()
        # 对回答进行分组,每组进行数据的提取
        div_list = response.xpath("//div[contains(@class,'answer gclear')]")

        answer_list = []
        for div in div_list:
            one_answer = {}
            one_answer["name"] = div.xpath('.//a[@class="answer-usr-name"]/@title').extract_first()
            one_answer["support_num"] = div.xpath('.//a[@class="answer-digg-up"]/span/text()').extract_first()
            one_answer["content"] = div.xpath('.//div[@class="answer-txt answerTxt gbbcode-content"]//text()').extract()
            answer_list.append(one_answer)
        item["answer_list"] = answer_list
        pprint(item)
