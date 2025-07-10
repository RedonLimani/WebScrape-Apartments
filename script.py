from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from datetime import datetime
import pandas as pd


def get_num(s):
    digits = ""
    for char in s:
        if char.isdigit():
            digits += char
    return int(digits) if digits else None

def clean_text(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return ", ".join(lines)

def scrape_main():
    driver = webdriver.Chrome()
    driver.get('https://www.hiddenvillagembp.com/floorplans')

    time.sleep(5)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    driver.quit()

    floorplans = [clean_text(i.text) for i in soup.select('.card-header h2')]
    beds = [get_num(i.parent.text) for i in soup.select('.nu-bed')]
    bathrooms = [get_num(i.parent.text) for i in soup.select('.nu-bathroom')]
    areas = [get_num(i.parent.text) for i in soup.select('.nu-area')]

    results = []
    for i in range(len(floorplans)):
        results.append({
            'floorplan': floorplans[i],
            'bedrooms': beds[i],
            'bathrooms': bathrooms[i],
            'area': areas[i]
        })

    plansurl=[]
    availabile = soup.find_all(lambda tag: tag.name == "a" and "AVAILABILITY" in tag.text)
    for i in availabile:
        plansurl.append("https://www.hiddenvillagembp.com"+i.get("href"))

    plansurl=list(set(plansurl))
    return results , plansurl
#print(plansurl)


def scrape(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    rows = []

    diva = soup.find('div', id="availApts")
    apartments = diva.find_all('div', class_='card')
    apartments = soup.select('div#availApts  div.card')
    # print(apartments)
    for i in apartments:
        # print(i)
        dicti = {}
        dicti['ID'] = get_num(i.select('h3 > span')[0].text)
        date = i.select('p >span')[0].text
        try:
            dicti['Availaible']= datetime.strptime(date).date()
        except (ValueError, TypeError):
            dicti['Availaible']= datetime.today().date()
        dicti['Price'] = get_num(i.select('p')[1].text)
        rows.append(dicti)

    info = {'bedrooms': 'nu-bed', 'bathrooms': 'nu-bathroom', 'area': 'nu-area'}
    for i in rows:
        for key, value in info.items():
            i[key] = get_num(soup.find(class_=value).parent.text)

        i['floorplan'] = clean_text(soup.find('h2', class_="h3 font-weight-normal").text)

        # amneities=''
        # li = soup.find(lambda tag: tag.name == "h2" and 'Features & Amenities' in tag.text).parent
        # li=li.find_all('li')
        # for j in li:
        # amneities+=j.text
        # i['Amnesities']=clean_text(amneities)
    driver.quit()
    return rows

def update(results,new):
    for i, apt in enumerate(results):
        if apt.get('floorplan') == new.get('floorplan')and len(apt)==4 :
            results[i] = new
            return
    results.append(new)

def main():
    results,plansurl = scrape_main()
    for url in plansurl:
        for i in scrape(url):
            update(results,i)

    df=pd.DataFrame(results)
    df.to_csv('output.csv', index=False)

if __name__ == '__main__':
    while True:
        main()
        time.sleep(60 * 60)