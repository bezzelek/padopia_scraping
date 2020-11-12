"""This is only draft"""


def parse_agency_content(self, response, **kwargs):
    logger.info('Scraping agency page...')
    items = AgencyItem()

    agency_source_website = 'https://www.idealista.com/'
    agency_website_country = 'Spain'
    agency_name_extract = response.xpath('//*[@id="commercial-name"]/text()').extract()
    agency_name = ''.join(agency_name_extract).strip()
    agency_logo = 'https:' + response.xpath('//*[@id="office-container"]/picture/img/@src').get()
    agency_link = response.url
    agency_phone = response.xpath("//span[@class='icon-phone']/text()").get()
    agency_address_extract = response.xpath('//*[@id="office-info"]/a/span/text()').extract()
    agency_address = 'Address: ' + ''.join(agency_address_extract).strip()
    agency_overview = 'Phone: ' + agency_phone + '\n' + agency_address

    agency_name_lower = agency_name.lower()
    punctuation = "!@#$%^&*()_-+<>?:.,;"
    for symbol in agency_name_lower:
        if symbol in punctuation:
            agency_name_lower = agency_name_lower.replace(symbol, "")
    agency_slug = agency_name_lower.replace(" ", "-")
    date_time = datetime.utcnow()

    items['agency_source_website'] = agency_source_website
    items['agency_website_country'] = agency_website_country
    items['agency_name'] = agency_name
    items['agency_logo'] = agency_logo
    items['agency_link'] = agency_link
    items['agency_phone'] = agency_phone
    items['agency_overview'] = agency_overview
    items['agency_slug'] = agency_slug
    items['date_time'] = date_time

    logger.info('Yielding new agency item...')
    yield items
