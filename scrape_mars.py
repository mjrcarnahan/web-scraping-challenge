# Dependencies
from bs4 import BeautifulSoup
import requests
import pandas as pd
from splinter import Browser
import pymongo

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": 'chromedriver.exe'}
    return Browser("chrome", **executable_path, headless=False)

def scrape_info():
    browser = init_browser()
         
    # NASA Mars News

    url = 'https://mars.nasa.gov/news/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    results = soup.find_all(class_="slide")
    # Loop through returned results

    title = results[0].find(class_="content_title").text
    paragraph = results[0].find(class_="rollover_description_inner").text
    
    # JPL Mars Space Images

    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    fancybox = soup.find('a', class_='fancybox')
    url_text = fancybox['data-fancybox-href']
    image_url = ['https://www.jpl.nasa.gov' + url_text]

    # # Mars Weather

    url = 'https://twitter.com/marswxreport?lang=en'
    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(response.text, 'lxml')
    # Examine the results, then determine element that contains sought info
    results = soup.find('p', class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text" )
    mars_weather = results.text


    # # Mars Hemispheres

    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    links = browser.find_by_css('.description .itemLink')
    num_links = len(links)

    image_urls = []
    titles = []

    for i in range(0, num_links):
        browser.find_by_css('.description .itemLink')[i].click()
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.find(class_="downloads")
        image_urls.append(results.a['href'])
        browser.visit(url)

    links = browser.find_by_css('.description .itemLink')

    for link in links:
        titles.append(link.text)

    hemisphere_image_urls = []

    for i in range(0, num_links):
        hemisphere_image_urls.append({"title" : titles[i], "img_url" : image_urls[i]})

    # # Mars Facts

    # URL of page to be scraped
    url = 'https://space-facts.com/mars/'
    tables = pd.read_html(url)
    df = tables[0]
    df.columns=["Description","Values"]
    df=df.to_html()
    df.replace('\n', '')

    # Create Mars Dictionary
    mars_dict = {
        "news_title": title,
        "paragraph_text": paragraph,
        "featured_image": image_url[0],
        "weather": mars_weather,
        "facts": str(df),
        "image_urls": image_urls
    }

    return mars_dict