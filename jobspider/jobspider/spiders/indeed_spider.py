import scrapy
import urllib2
from jobspider.items import IndeedItem


class IndeedSpider(scrapy.Spider):
    name = "indeed_spider"
    root_url = 'https://www.indeed.co.uk/jobs?q=python&l=london&jt=contract&start=0'
    start_urls = [root_url]
    indeed_root = 'https://www.indeed.co.uk'

    def parse(self, response):

        data = urllib2.urlopen("https://raw.githubusercontent.com/adamalton/recruiterdomains/master/domains.txt").read()
        recruiter_list = data.split("\n")
        recruiter_list = map(lambda x: x.split('.')[0], recruiter_list)

        for res in response.css('.row.result'):
            try:
                company = res.css('.company::text').extract_first().lstrip()

                if company.lower().replace(' ', '') not in recruiter_list:
                    item = IndeedItem()
                    item['company'] = company

                    if res.css('.jobtitle a::attr(href)').extract_first() is None:
                        item['job_url'] = self.indeed_root + res.css('a::attr(href)').extract_first()
                        item['title'] = res.css('a::attr(title)').extract_first()
                    else:
                        item['job_url'] = self.indeed_root + res.css('.jobtitle a::attr(href)').extract_first()
                        item['title'] = res.css('.jobtitle a::attr(title)').extract_first()

                    item['day_rate'] = res.css('.no-wrap::text').extract_first().lstrip() # day rate
                    item['summary'] = res.css('.summary').extract_first()
                yield item
            except Exception:
                pass

        if response.css('.np::text').extract_first() is not None:
            next_page = self.indeed_root + response.css('.pagination a::attr(href)').pop().extract()
            yield response.follow(next_page, self.parse)
