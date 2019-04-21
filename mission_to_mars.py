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

def scrape_news(browser, url):
        # scrape latest new article
        soup = visit_url(browser, url)

        news_titles = soup.find_all('div', class_ = "content_title")
        news_p = soup.find_all('div', class_ = "article_teaser_body")
        return news_titles[0].a.text, news_p[0].text

def scrape_featured_image(browser, url):
        # scrape a featured image from NASA website
        soup = visit_url(browser, url)
        featured_image_url = soup.find('a', class_= "button fancybox")['data-fancybox-href']
        featured_image_url = 'https://www.jpl.nasa.gov'+ featured_image_url
        return featured_image_url

def scrape_weather_tweet(browser, url):
        # Scrape latest weather tweet
        soup = visit_url(browser, url)
        latest_tweet = soup.find_all('p', class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text")
        return latest_tweet[0].text

def scrape_mars_facts(browser, url):
        # Scrape a table with marse facts and return it as an html <table> string

        soup = visit_url(browser, url)

        mars_attr = soup.find_all('td', class_="column-1")
        mars_facts = soup.find_all('td', class_="column-2")

        mars_facts_dict = {}
        for attr, fact in zip(mars_attr, mars_facts):
                mars_facts_dict[attr.text.strip().split(':')[0]] = fact.text.strip()


        facts_df = pd.DataFrame.from_dict(mars_facts_dict, orient = "index")

        facts_table = facts_df.to_html(header = False)

        return facts_table.replace('\n', '')


def scrape_hemisphere_img(browser, url):

        soup = visit_url(browser, url)


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


def scrape():
        browser = init_browser()

        mars_new_instance = {}

        try:
                # scrape latest new article
                title, news = scrape_news(browser, 'https://mars.nasa.gov/news/')

                # scrape a featured image from NASA website
                image_url = scrape_featured_image(browser, 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars')

                # Scrape latest weather tweet
                latest_tweet = scrape_weather_tweet(browser, 'https://twitter.com/marswxreport?lang=en')

                # Scrape Mars facts:
                mars_facts = scrape_mars_facts(browser, 'https://space-facts.com/mars/')

                # Scrape all Mars hemisphere images and names
                hemisphere_image_urls = scrape_hemisphere_img(browser, 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars')
 


                mars_new_instance = {'news-title': title, 
                                        'news-summary': news,
                                        'featured-image-url': image_url,
                                        'current-weather':latest_tweet,
                                        'mars-facts': mars_facts,
                                        'hemisphere-images': hemisphere_image_urls
                                        }

                write_to_mongo(mars_new_instance)

        except:
                pass


        return mars_new_instance



def write_to_mongo(mars_new_instance):

        conn = 'mongodb://localhost:27017'
        client = pymongo.MongoClient(conn)

        db = client.mars_db

        db.request_instances.drop()
        db.request_instances.insert_one(mars_new_instance)


# mars_news = scrape()
# print(mars_news)

# # 