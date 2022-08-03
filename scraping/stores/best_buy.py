import re
from random import randint
from time import sleep

from bs4 import BeautifulSoup
from celery import shared_task
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@shared_task
def best_buy(driver, item_list):
    load_all(driver)

    # TODO: first delay
    sleep(randint(1, 2))

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    get_all_items(soup, item_list)


@shared_task
def get_all_items(soup, entries):
    # all_items = soup.find_all('div', {'class': 'x-productListItem'})
    all_items = soup.find_all('a', {'itemprop': 'url'})

    for item in all_items:
        item_entry = item_details(item)
        entries.append(item_entry)


@shared_task
def get_name(item, entry):
    item_name = item.find('a', {'itemprop': 'name'}).text
    entry.update({'item': item_name})


@shared_task
def get_brand(item, entry):
    item_brand = item.find('a', {'class': 'item-brand'})
    if item_brand is not None:
        item_brand = item_brand.find('img')['title']
    entry.update({'brand': item_brand})


@shared_task
def get_shipping(item, entry):
    item_shipping = item.find('span', {'class': 'container_1DAvI'}).text
    item_shipping = item_shipping.strip()
    if item_shipping != 'Available to ship':
        item_shipping = 'Sold out online'
    entry.update({'shipping': item_shipping})


@shared_task
def extract_num(string):
    no_commas = string.replace(",", "")
    filtered_string = re.findall(r"\d+\.\d+", no_commas)
    return filtered_string[0]


@shared_task
def get_price(item, entry):
    was_price = item.find('li', {'class': 'price-was'}).getText()
    current_price = item.find('li', {'class': 'price-current'}).getText()

    if was_price != '' and current_price != '':
        normal_price = extract_num(was_price)
        sale_price = extract_num(current_price)
    elif current_price != '':
        normal_price = extract_num(current_price)
        sale_price = None
    elif was_price != '':
        normal_price = extract_num(was_price)
        sale_price = None
    else:
        normal_price = None
        sale_price = None
    entry.update({'normal_price': normal_price})
    entry.update({'sale_price': sale_price})


@shared_task
def get_rating(item, entry):
    item_rating = item.find('i', {'class': 'rating'})
    if item_rating is not None:
        item_rating = item_rating['aria-label'].split(' ')[1]
        num_ratings = item.find('span', {'class': 'item-rating-num'}).getText().strip('()')
        entry.update({'rating': item_rating})
        entry.update({'number_of_ratings': num_ratings})


@shared_task
def get_promo(item, entry):
    item_promo = item.find('p', {'class': 'item-promo'})
    if item_promo is not None:
        item_promo = item_promo.getText()
        if item_promo == "OUT OF STOCK":
            entry.update({'out_of_stock': 'True'})
        else:
            entry.update({'promo': item_promo})
            entry.update({'out_of_stock': 'False'})
    else:
        entry.update({'out_of_stock': 'False'})


@shared_task()
def get_item_id(item, entry):
    item_strong_tag = item.find('strong', string='Item #: ')
    if item_strong_tag is None:
        item_strong_tag = item.find('strong', string='Model #: ')

    if item_strong_tag is None:
        entry.update({'item_id': None})
    else:
        item_text = item_strong_tag.parent.text
        pattern = re.compile('\\b(Item #: |Model #: )')
        item_id = re.sub(pattern, '', item_text)
        entry.update({'item_id': item_id})


@shared_task
def item_details(item):
    item_entry = {}
    item_entry.update({'store': 'Best Buy'})
    get_name(item, item_entry)
    get_brand(item, item_entry)
    get_shipping(item, item_entry)
    get_price(item, item_entry)
    get_rating(item, item_entry)
    get_promo(item, item_entry)
    get_item_id(item, item_entry)
    return item_entry


@shared_task
def load_all(driver):
    while True:
        try:
            WebDriverWait(driver, 25).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'link_3hcyN buttonLoadMoreLink_THBoN')))
        except TimeoutException:
            driver.quit()

        try:
            driver.find_element(By.CLASS_NAME, 'endOfList_b04RG')
            break
        except NoSuchElementException:
            driver.find_element(By.CLASS_NAME, 'button_E6SE9').click()

        # TODO: second delay
        sleep(randint(1, 2))
