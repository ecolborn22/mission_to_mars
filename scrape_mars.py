#!/usr/bin/env python
# coding: utf-8
# # Mission to Mars

# Add dependencies
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import urllib.request
from splinter import Browser

def scrape():
    mars_dict = {}
    # NASA Mars News-----------------------------------------------------------------------------------------------------
    news_url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    # Collect latest news title and paragraph text
    # Access site and get the "soup"
    response = requests.get(news_url)
    news_soup = bs(response.text, 'html.parser')
    # Locate and save title text
    titles = news_soup.find_all("div", class_="content_title")
    news_title = titles[0].text
    # Locate and save paragraph text
    paragraphs = news_soup.find_all("div", class_="rollover_description_inner")
    news_p = paragraphs[0].text
    mars_dict['title'] = news_title
    mars_dict['paragraph'] = news_p

    # JPL Mars-----------------------------------------------------------------------------------------------------------
    mars_images_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    # Use splinter to find image url for current featured Mars image and save as featured_image_url
    # Define executable path and browser
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    # Access website on chromedriver
    browser.visit(mars_images_url)
    # Save url to full size featured jpg image
    mars_img_html = browser.html
    # Find the main featured image href using splinter -- interact with page
    browser.click_link_by_partial_text('FULL IMAGE')
    # Visit page with actual full image
    # browser.find_by_xpath('//*[@id="fancybox-lock"]/div/div[2]/div/div[1]/a[2]').click()
    # ^^ says button is not interactable
    feat_img_html = bs(browser.html, 'html.parser')
    long_path = feat_img_html.find('a', class_='button fancybox')['data-fancybox-href']
    featured_image_url = 'https://www.jpl.nasa.gov/' + long_path
    # Close browser
    browser.quit()
    mars_dict['image_url'] = featured_image_url

    # Mars Weather--------------------------------------------------------------------------------------------------------
    mars_twitter_url = "https://twitter.com/marswxreport?lang=en"
    # Scrape latest Mars weather tweet text as mars_weather
    twit_response = requests.get(mars_twitter_url)
    twit_soup = bs(twit_response.text, 'html.parser')
    # Find all tweet containers
    tweets = twit_soup.find_all("div", class_="js-tweet-text-container")
    weather_tweets = []
    # Filter out tweets that aren't actually weather reports
    for tweet in tweets:
        #print(tweet.text)
        if "pressure" in tweet.text:
            weather_tweets.append(tweet)
    # Save the most recent weather report tweet
    mars_weather = weather_tweets[0].text
    mars_dict['weather'] = mars_weather

    # Mars Facts----------------------------------------------------------------------------------------------------------
    fact_page_url = "https://space-facts.com/mars/"
    # Scrape table containing facts about the planet like diameter, mass, etc.
    # Convert data to HTML table string
    # Access the page and make the soup
    fact_response = requests.get(fact_page_url)
    fact_soup = bs(fact_response.text, 'lxml')
    # Find the table
    table = fact_soup.find('table', attrs={'class':'tablepress-id-comp-mars'})
    table_rows = table.find_all('tr')
    # Import table as a dataframe
    l = []
    for tr in table_rows:
        th = tr.find_all('th')
        if len(th) != 0:
            header = [tr.text for tr in th]
        else:
            td = tr.find_all('td')
            row = [tr.text for tr in td]
            l.append(row)
    fact_df = pd.DataFrame(l, columns=header)
    # Convert table to html in pandas
    fact_html = fact_df.to_html()
    mars_dict['facts'] = fact_html

    # Mars Hemispheres-----------------------------------------------------------------------------------------------------
    astrogeology_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    # obtain high resolution images for each of Mars' hemispheres
    # *** YOU WILL NEED TO CLICK EACH OF THE LINKS TO THE HEMISPHERES IN ORDER TO FIND THE IMAGE URL TO THE FULL RESOLUTION IMAGE***
    # Save image url for full resolution and hemisphere title in dictionary containing img_url and title
    # Each individual link to full size images
    # I wasn't sure what link we actually wanted.... and the instructions did not say to use splinter to click
    full_img_links = ["https://astrogeology.usgs.gov/search/map/Mars/Viking/cerberus_enhanced",
                    "https://astrogeology.usgs.gov/search/map/Mars/Viking/schiaparelli_enhanced",
                    "https://astrogeology.usgs.gov/search/map/Mars/Viking/syrtis_major_enhanced",
                    "https://astrogeology.usgs.gov/search/map/Mars/Viking/valles_marineris_enhanced"]
    hemisphere_image_urls = []
    for url in full_img_links:
        hemi_response = requests.get(url)
        hemi_soup = bs(hemi_response.text, 'html.parser')    
        row = {'title': hemi_soup.title.text.split(' Enhanced')[0],
            'img_url': hemi_soup.find('div', class_='downloads').a['href']}
        hemisphere_image_urls.append(row)
    mars_dict['hemispheres'] = hemisphere_image_urls
    return mars_dict