import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import BnpItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class BnpSpider(scrapy.Spider):
	name = 'bnp'
	start_urls = ['https://www.bnpparibas-pf.bg/novini.html']

	def parse(self, response):
		post_links = response.xpath('//h2/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//li/a[@title="следваща"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):

		date = response.xpath('//time/text()').get()
		title = response.xpath('//div[@class="clearfix"]/following-sibling::h2/text()').get()
		content = response.xpath('//div[@class="clearfix"]/following-sibling::p//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=BnpItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
