#!/usr/bin/env python
# coding: utf-8
from splinter import Browser
from bs4 import BeautifulSoup
from pprint import pprint
import pandas as pd
import pymongo
import time


def init_browser():
        executable_path = {'executable_path': 'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'}
        browser = Browser('chrome', **executable_path, headless=False)
        return browser

def visit_url(browser, url):
        browser.visit(url)
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        return soup


def scrape():
        browser = init_browser()

        # scrape latest new article
        soup = visit_url(browser, 'https://mars.nasa.gov/news/')

        news_titles = soup.find_all('div', class_ = "content_title")
        news_p = soup.find_all('div', class_ = "article_teaser_body")

        print(news_titles, news_p)
        mars_new_instance = {'news-title': news_titles[0].a.text, 
                                'news-summary': news_p[0].text}


        # scrape a featured image from NASA website
        soup = visit_url(browser, 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars')

        featured_image_url = soup.find('a', class_= "button fancybox")['data-fancybox-href']


        featured_image_url = 'https://www.jpl.nasa.gov'+ featured_image_url
        mars_new_instance['featured-image-url'] = featured_image_url

        # Scrape latest weather tweet
        soup = visit_url(browser, 'https://twitter.com/marswxreport?lang=en')
        latest_tweet = soup.find_all('p', class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text")
        
        # Build a dictionary with latest news, a featured image and latest weather tweet
        mars_new_instance['current-weather'] = latest_tweet[0].text

        return mars_new_instance

 


def scrape_mars_facts():
        browser = init_browser()

        sf_url = 'https://space-facts.com/mars/'
        browser.visit(sf_url)
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')

        mars_attr = soup.find_all('td', class_="column-1")
        mars_facts = soup.find_all('td', class_="column-2")

        mars_facts_dict = {}
        for attr, fact in zip(mars_attr, mars_facts):
                mars_facts_dict[attr.text.strip().split(':')[0]] = fact.text.strip()


        facts_df = pd.DataFrame.from_dict(mars_facts_dict, orient = "index")

        facts_table = facts_df.to_html(header = False)

        return facts_table.replace('\n', '')

def scrape_hemisphere_img():
        browser = init_browser()

        hemi_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
        browser.visit(hemi_url)
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')


        hemi_links = soup.find_all('a', class_= "itemLink product-item")
        links = []
        for a in hemi_links:
                hemi_url = 'https://astrogeology.usgs.gov'+a['href']
        if hemi_url not in links:
                links.append(hemi_url)


        hemisphere_image_urls = []
        for link in links:
                browser.visit(link)
                html = browser.html
                soup = BeautifulSoup(html, 'html.parser')
                img_dict = {}
                img_dict['title'] = soup.find('h2', class_ = "title").text.strip('Enhanced')
                img_dict['img_url'] = soup.find('a', target = "_blank")['href']
                hemisphere_image_urls.append(img_dict)
                time.sleep(3)

        return hemisphere_image_urls


def write_to_mongo(mars_new_instance):

        conn = 'mongodb://localhost:27017'
        client = pymongo.MongoClient(conn)

        db = client.mars_db

        db.request_instances.drop()
        db.request_instances.insert_one(mars_new_instance)

        # db.facts.drop()
        # db.facts.insert_one(mars_facts_dict)

        # db.images.drop()
        # db.images.insert_many(hemisphere_image_urls)

mars_news = scrape()
write_to_mongo(mars_news)
