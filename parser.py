import requests
from bs4 import BeautifulSoup
import time
import logging
import import_in_google_sheets


# pip install requests
# pip install beautifulsoup4
# pip install lxml


logging.basicConfig(format='%(asctime)s %(funcName)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)
FORMATTER = logging.Formatter("%(time)s — %(name)s — %(level)s — %(message)s")
Loger = logging.getLogger('MyLoger')
# Loger.setLevel(logging.DEBUG)
Loger.setLevel(logging.ERROR)


DOMAIN = 'https://auto.ria.com/uk'


def get_html(url, user_agent = None, proxy=None, params=None):
    Loger.debug(f'url = {url}\nuser_agent = {user_agent}\nproxy={proxy}\nparams = {params}')
    while True:
        r = requests.get(url, headers=user_agent, proxies=proxy, params=params)    # Response
        if r.status_code == 200:
            Loger.debug(f'OK r.status_code = {r.status_code}')
            return r.text
        else:
            Loger.debug(f'Error r.status_code = {r.status_code}')
            time.sleep(30)


def get_last_page_number(html):
    soup = BeautifulSoup(html, 'lxml')
    pages = soup.find_all('span', class_='page-item mhide')
    if pages:
        last_page = int(pages[-1].text.strip())
        Loger.debug(f'Last page number: {last_page}')
        return int(last_page)
    else:
        Loger.debug(f'None pagination. Last page number: 1')
        return 1


def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')
    searchResult = soup.find('div', id='searchResult')
    result = []
    if searchResult:
        proposition = soup.find_all('div', class_='proposition')
        if proposition:
            for item in proposition:
                proposition_name = item.find('h3', class_='proposition_name')
                a = proposition_name.find('a')
                if a:
                    url = DOMAIN + a.get('href')
                    name = a.find('strong').text
                else:
                    a = 'Not found'
                    url = 'Not found'
                    name = 'Not found'
                    Loger.info('a, url, name not found')
            # ==== price
                lower_block = item.find_all('div', class_='mt-5')
                if lower_block:
                    lower_block = lower_block[-1]
                    price_div = lower_block.find('div', class_='proposition_price')
                    if price_div:
                        price_usd = price_div.find('span', class_='size18').text.strip()
                        price_uah = price_div.find_all('span', class_='size13')
                        if price_uah:
                            price_uah = price_uah[-1].text.strip()
                        else:
                            price_uah = 'Not found'
                            Loger.info('price_uah not found')
                    else:
                        Loger.info('price_div not found')
                        price_usd = 'Not found'
                        price_uah = 'Not found'
                else:
                    Loger.info('lower_block not found')
                region_block = lower_block.find('div', class_='proposition_region')
                city = region_block.find('strong').get('title').strip()
                car_dealership = region_block.text
                index = car_dealership.find('•')
                car_dealership = car_dealership[index+1:]
                # тут має бути збереження всіх результатів в словник наприклад
                result.append({'url': url, 'name': name, 'price_usd': price_usd, 'price_uah': price_uah, 'city': city, 'car_dealership': car_dealership})
        else:
            Loger.info('proposition not found')
            a = 'Not found'
            url = 'Not found'
            name = 'Not found'
    else:
        Loger.info('searchResult not found')
    return result


def main():
    url = input('Введіть url марки для парсингу:\n')
    url = url.rstrip()
    html = get_html(url)
    last_page_number = get_last_page_number(html)
    result = []
    for i in range(1, last_page_number+1):
        page = {'page': i}
        html = get_html(url, params=page)
        result.extend(get_page_data(html))
    url = import_in_google_sheets.main(result)
    print(f'You can open the document using this link: {url}\nThe link is also saved in the file GH_url.txt\n')
    with open('GH_url.txt', 'w') as f:
        f.write(url)


if __name__ == '__main__':
    main()
