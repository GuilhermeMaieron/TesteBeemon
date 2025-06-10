import scrapy

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self, urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = urls.split(',')

    def parse(self, response):
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(),
                "author": quote.css("small.author::text").get(),
                "tags": quote.css("div.tags a.tag::text").getall(),
            }
        
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)



class AuthorSpider(scrapy.Spider):
    name = "author"

    def __init__(self, urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = urls.split(',')

    def parse(self, response):
        name = response.css("h3.author-title::text").get()
        born_date = response.css("span.author-born-date::text").get()
        born_location = response.css("span.author-born-location::text").get()
        description = response.css("div.author-description::text").get()

        yield {
            "name": name.strip() if name else None,
            "born": f"{born_date} {born_location}" if born_date and born_location else None,
            "description": description,
        }