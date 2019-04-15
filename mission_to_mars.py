#!/usr/bin/env python
# coding: utf-8

# In[7]:


from splinter import Browser
from bs4 import BeautifulSoup
from pprint import pprint
import pandas as pd
import pymongo


# In[8]:


executable_path = {'executable_path': 'chromedriver.exe'}
browser = Browser('chrome', **executable_path, headless=False)


# In[9]:


url = 'https://mars.nasa.gov/news/'
browser.visit(url)


# In[10]:


html = browser.html
soup = BeautifulSoup(html, 'html.parser')

news_titles = soup.find_all('div', class_ = "content_title")
news_p = soup.find_all('div', class_ = "article_teaser_body" )

mars_new_instance = {'news-title': news_titles[0].text, 'news-summary': news_p[0].text}


# In[11]:


img_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
browser.visit(img_url)
html = browser.html
soup = BeautifulSoup(html, 'html.parser')

featured_image_url = soup.find('a', class_= "button fancybox")['data-fancybox-href']


# In[12]:


featured_image_url = 'https://www.jpl.nasa.gov'+ featured_image_url
mars_new_instance['featured-image-url'] = featured_image_url


# In[13]:


tw_url = 'https://twitter.com/marswxreport?lang=en'
browser.visit(tw_url)
html = browser.html
soup = BeautifulSoup(html, 'html.parser')


# In[14]:


latest_tweet = soup.find_all('p', class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text")
mars_new_instance['current-weather'] = latest_tweet[0].text


# In[15]:


sf_url = 'https://space-facts.com/mars/'
browser.visit(sf_url)
html = browser.html
soup = BeautifulSoup(html, 'html.parser')


# In[16]:


mars_attr = soup.find_all('td', class_="column-1")
mars_facts = soup.find_all('td', class_="column-2")
for attr, fact in zip(mars_attr, mars_facts):
    print(attr.text, fact.text)


# In[17]:


mars_facts_dict = {}
for attr, fact in zip(mars_attr, mars_facts):
    mars_facts_dict[attr.text.strip().split(':')[0]] = fact.text.strip()

mars_facts_dict


# In[18]:


facts_df = pd.DataFrame.from_dict(mars_facts_dict, orient = "index")
facts_df


# In[19]:


facts_df.to_html(header = False)


# In[20]:


hemi_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
browser.visit(hemi_url)
html = browser.html
soup = BeautifulSoup(html, 'html.parser')


# In[21]:


hemi_links = soup.find_all('a', class_= "itemLink product-item")
links = []
for a in hemi_links:
    hemi_url = 'https://astrogeology.usgs.gov'+a['href']
    if hemi_url not in links:
        links.append(hemi_url)
print(links)


# In[22]:


import time
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


# In[23]:


hemisphere_image_urls


# In[24]:


# Create connection variable
conn = 'mongodb://localhost:27017'

# Pass connection to the pymongo instance.
client = pymongo.MongoClient(conn)

# Connect to a database. Will create one if not already available.
db = client.mars_db


# In[28]:


# Drops collection if available to remove duplicates
db.request_instances.drop()

# Creates a collection in the database and inserts two documents
db.request_instances.insert_one(mars_new_instance)


# In[30]:


# Drops collection if available to remove duplicates
db.facts.drop()

# Creates a collection in the database and inserts two documents
db.facts.insert_one(mars_facts_dict)


# In[31]:


# Drops collection if available to remove duplicates
db.images.drop()

# Creates a collection in the database and inserts two documents
db.images.insert_many(hemisphere_image_urls)


# In[ ]:




