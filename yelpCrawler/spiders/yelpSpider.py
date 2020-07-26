# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from yelpCrawler.items import YelpcrawlerItem
from yelpCrawler.cities import cities_list
import traceback
import os
import re
import csv
import time

class YelpspiderSpider(scrapy.Spider):
    name = 'yelpSpider'
    allowed_domains = ['yelp.com']
    
    def start_requests(self):
        for city in cities_list:
            url = "https://www.yelp.com/search?find_desc=Retirement+Homes&find_loc={}".format(city)
            time.sleep(1)
            yield Request(url, dont_filter=True, callback=self.parse)
    
    def parse(self, response):
        # Item list
        nodes = response.xpath("//li[@class='lemon--li__373c0__1r9wz border-color--default__373c0__3-ifU']")
        for node in nodes:
            item_link = ''.join(node.xpath(".//h4[@class='lemon--h4__373c0__1yd__ heading--h4__373c0__27bDo alternate__373c0__2Mge5']//a[@class='lemon--a__373c0__IEZFH link__373c0__1G70M link-color--inherit__373c0__3dzpk link-size--inherit__373c0__1VFlE']/@href").extract()).strip()
            if item_link:
                print('&&&&&', item_link, '&&&&&')
                time.sleep(1)
                link_ = "https://www.yelp.com" + item_link
                yield Request(link_, callback=self.parse_item, dont_filter=True)

        # pagination
        next_page = ''.join(response.xpath("//a[@class='lemon--a__373c0__IEZFH link__373c0__1G70M next-link navigation-button__373c0__23BAT link-color--inherit__373c0__3dzpk link-size--inherit__373c0__1VFlE']/@href").extract()).strip()
        if next_page:
            next_page = "https://www.yelp.com" + next_page
            time.sleep(1)
            yield Request(next_page, callback=self.parse)
                
    def parse_item(self, response):
        result_dict = dict()
        retirement_home_url = response.url
        
        home_name = ''.join(response.xpath("//h1[@class='lemon--h1__373c0__2ZHSL heading--h1__373c0__dvYgw undefined heading--inline__373c0__10ozy']/text()").extract()).strip()
        if not home_name:
            return
        
        # Address and phone
        PHONE = ''.join(response.xpath("//div[@class='lemon--div__373c0__1mboc arrange-unit__373c0__o3tjT arrange-unit-fill__373c0__3Sfw1 border-color--default__373c0__3-ifU']//p[contains(text(),'Phone number')]/following-sibling::p//text()").extract()).strip()
        WEBSITE = ''.join(response.xpath("//div[@class='lemon--div__373c0__1mboc arrange-unit__373c0__o3tjT arrange-unit-fill__373c0__3Sfw1 border-color--default__373c0__3-ifU']//p[contains(text(),'Business website')]/following-sibling::p//text()").extract()).strip()
        address = '|'.join(response.xpath("//address[@class='lemon--address__373c0__2sPac']//text()").extract()).strip()
        ADDRESS = address.replace("|", " ").strip()
        if "|" in address:
            city_state = address[address.rindex("|")+1:]
            CITY = city_state.split(",")[0].strip()
            state = city_state.split(",")[1].strip()
            STATE = ''.join(re.findall('[A-Z]', state)).strip()
        elif (address != '') and ("," in address):
            CITY = address.split(",")[0].strip()
            state = address.split(",")[1].strip()
            state = address.split(",")[1].strip()
            STATE = ''.join(re.findall('[A-Z]', state)).strip()
        else:
            CITY = ''
            STATE = ''

        result_dict['HomeName'] = home_name
        result_dict['PhoneNumber'] = PHONE
        result_dict['Address'] = ADDRESS
        result_dict['City'] = CITY
        result_dict['State'] = STATE
        result_dict['Website'] = WEBSITE

        result_csv = os.path.dirname(os.path.abspath(__file__)) + '/result.csv'
        file_exist = os.path.isfile(result_csv)
        with open(result_csv, "a", newline="") as f:
            fieldnames = ["HomeName", "City", "State", "Address", "PhoneNumber", "Website"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exist:
                writer.writeheader()
            writer.writerow(result_dict)

        yield result_dict    