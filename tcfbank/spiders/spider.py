import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import TcfbankItem
from itemloaders.processors import TakeFirst
import requests

base_url = "https://news.tcfbank.com/Services/PressReleaseService.svc/GetPressReleaseList"

payload="{\"serviceDto\":{\"ViewType\":\"2\",\"ViewDate\":\"\",\"RevisionNumber\":\"1\",\"LanguageId\":\"1\",\"Signature\":\"\",\"ItemCount\":-1,\"StartIndex\":0,\"TagList\":[],\"IncludeTags\":true},\"pressReleaseBodyType\":0,\"pressReleaseSelection\":3,\"pressReleaseCategoryWorkflowId\":\"1cb807d2-208f-4bc3-9133-6a9ad45ac3b0\",\"excludeSelection\":1}"
headers = {
  'authority': 'news.tcfbank.com',
  'pragma': 'no-cache',
  'cache-control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'accept': 'application/json, text/javascript, */*; q=0.01',
  'x-newrelic-id': 'VQYBUlRVChACVlhbBQMCVlU=',
  'x-requested-with': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
  'content-type': 'application/json; charset=UTF-8',
  'origin': 'https://news.tcfbank.com',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
  'referer': 'https://news.tcfbank.com/news/default.aspx',
  'accept-language': 'en-US,en;q=0.9,bg;q=0.8',
  'cookie': '__cfduid=d69f997fd7fb69764a46deb8f264a89111617179390; _uetsid=43e5005091fb11eb912c5147a5952e78; _uetvid=43e5202091fb11ebafdab5a6e9422ca6; _ga=GA1.2.791885405.1617179393; _gid=GA1.2.480202524.1617179393; _fbp=fb.1.1617179393048.1289869367; cd_user_id=17887673e402bb-012066765e2259-52193c12-1fa400-17887673e41438; bpazaws52gukakzc__ctrl0_ctl42_uccaptcha=pc5w+gPaXO0S33d24JRkV6UL8Jw2vEUerzInpp48j9S/FohJeRyv+C1/DFQO6ZjhcLps+N/ZnxnbsGgNV/vJz5OHHxsFSl9ncsePtgPCFvOgNNBF85T4naSJyGkopoPPTJI1LrJ8zhEYW9NswPfo0b5daT8Er/WzzpWFmLwH5emF0EWs/9zMgAKeHvmUopWxVvsoZLdaM1FZMAGJliE3R/3120rxm8CJa7Uks7auoZG95MrA9XNT3WmZQwUiuJGf'
}


class TcfbankSpider(scrapy.Spider):
	name = 'tcfbank'
	start_urls = ['https://news.tcfbank.com/news/default.aspx']

	def parse(self, response):
		data = requests.request("POST", base_url, headers=headers, data=payload)
		raw_data = json.loads(data.text)
		for post in raw_data['GetPressReleaseListResult']:
			url = post['LinkToDetailPage']
			date = post['PressReleaseDate']
			title = post['Headline']
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date, 'title': title})

	def parse_post(self, response, title, date):
		if 'pdf' in response.url:
			return
		description = response.xpath('//div[@class="module_body"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=TcfbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
