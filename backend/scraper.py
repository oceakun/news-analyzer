import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://timesofindia.indiatimes.com/home/headlines"
page_request = requests.get(url)
data = page_request.content
soup = BeautifulSoup(data, "html.parser")

def headlines():
    results = []
    for divtag in soup.find_all('div', {'class': 'headlines-list'}):
        for ultag in divtag.find_all('ul', {'class': 'clearfix'}):
            for litag in ultag.find_all('li'):
                a_tag = litag.find('a')
                if a_tag and 'href' in a_tag.attrs:
                    href = "https://timesofindia.indiatimes.com" + a_tag['href']
                    title = a_tag.text.strip()
                    results.append({"Title": title, "URL": href, "Category": "Headlines"})
    return results

def metrocityheadlines():
    results = []
    for wrapperdivtag in soup.find_all('div', {'class': 'metro-cities'}):
        for innerdivtag in wrapperdivtag.find_all('div',{'class':'headlines-list'}):
            for ultag in innerdivtag.find_all('ul', {'class': 'clearfix'}):
                for litag in ultag.find_all('li'):
                    a_tag = litag.find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        href = "https://timesofindia.indiatimes.com" + a_tag['href']
                        span_tag = litag.find('span', {'class': 'w_tle'})
                        title = span_tag.text.strip() if span_tag else ""
                        results.append({"Title": title, "URL": href, "Category": "Metro City Headlines"})
    return results

def businessheadlines():
    results = []
    for wrapperdivtag in soup.find_all('div', {'class': 'business'}):
        for ultag in wrapperdivtag.find_all('ul', {'class': 'clearfix'}):
            for litag in ultag.find_all('li'):
                a_tag = litag.find('a')
                if a_tag and 'href' in a_tag.attrs:
                    href = "https://timesofindia.indiatimes.com" + a_tag['href']
                    span_tag = litag.find('span', {'class': 'w_tle'})
                    title = span_tag.text.strip() if span_tag else ""
                    results.append({"Title": title, "URL": href, "Category": "Business Headlines"})
    return results

def worldheadlines():
    results = []
    div1 = soup.find('div', {'class': 'world'})
    if div1:
        for ultag in div1.find_all('ul', {'class': 'news_card clearfix'}):
            for litag in ultag.find_all('li'):
                a_tag = litag.find('a')
                span_tag = litag.find('span', {'class': 'w_tle'})
                if a_tag and span_tag:
                    href = "https://timesofindia.indiatimes.com" + a_tag['href']
                    title = span_tag.text.strip()
                    results.append({"Title": title, "URL": href, "Category": "World Headlines"})
    return results

def categoryheadlines():
    results = []
    categories_div = soup.find_all('div', {'class': 'categories'})
    for div in categories_div:
        for div2 in div.find_all('div',{'class':'inner'}):
            ul_tag = div2.find('ul', {'class': 'news_card clearfix'})
            if ul_tag:
                for li in ul_tag.find_all('li'):
                    a_tag = li.find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        href = "https://timesofindia.indiatimes.com" + a_tag['href']
                        title = a_tag.text.strip() if a_tag else ""
                        results.append({"Title": title, "URL": href, "Category": "Category Headlines"})
    return results

all_results = (
    headlines() + 
    metrocityheadlines() + 
    businessheadlines() + 
    worldheadlines() + 
    categoryheadlines()
)

csv_file = 'news_headlines.csv'
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["Title", "URL", "Category"])
    writer.writeheader()
    for row in all_results:
        writer.writerow(row)

def getarticle(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    elements = soup.find_all(class_='_s30J clearfix')
    return [element.get_text(strip=True) for element in elements]

df = pd.read_csv(csv_file)

df['Article'] = df['URL'].apply(getarticle)

df.to_csv(csv_file, index=False, encoding='utf-8')