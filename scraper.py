import requests
from bs4 import BeautifulSoup
import re
import yaml

# url = 'https://www.amazon.de/Mpow-Handyhalter-Armaturenbrett-Windschutzscheibe-autohandyhalter-Schwarz/dp/B0762GS7MS/ref=sxts_sxwds-bia-wc-p13n1_0?__mk_de_DE=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=23RODVAOJZ3E6&cv_ct_cx=smartphone&dchild=1&keywords=smartphone&pd_rd_i=B0762GS7MS&pd_rd_r=107a3664-1a2a-4a8f-9d95-19453533ee0a&pd_rd_w=xWWu4&pd_rd_wg=TtJ48&pf_rd_p=3f96b164-1992-4801-8017-4d6307a1a2a9&pf_rd_r=67Y54VKP76RBNPX3EMA6&psc=1&qid=1591871327&sprefix=smart%2Caps%2C184&sr=1-1-91e9aa57-911e-4628-99b3-09163b7d9294'

def extract_url(url):
    if url.find("www.amazon.de") != -1:
        index = url.find("/dp/")
        if index != -1:
            index2 = index + 14
            url = "https://www.amazon.de" + url[index:index2]
        else:
            index = url.find("/gp/")
            if index != -1:
                index2 = index + 22
                url = "https://www.amazon.de" + url[index:index2]
            else:
                url = None
    else:
        url = None
    return url

def get_product_details(url):
    with open('config.yaml') as f:
        config_scraper = yaml.load(f, Loader=yaml.FullLoader)['scraper'][0]
    headers = config_scraper['headers'][0]
    details = {"name": "", "price": 0, "ourprice": 0, "dealprice": 0, "coupon": 0, "finalprice": 0, 
               "deal": True, "url": ""}
    _url = extract_url(url)
    if _url == "":
        details = None
    else:
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, "html5lib")
        title = soup.find(id="productTitle")
        # get major price
        try:
            price = soup.find_all("span", {"class" : "priceBlockStrikePriceString a-text-strike"})[0]
        except:
            price = None
        # get ourprice
        price_ourprice = soup.find(id="priceblock_ourprice")
        # get dealprice
        price_dealprice = soup.find(id="priceblock_dealprice")
        # get coupon
        spans = soup.find_all("span", {"class": "a-color-base a-text-bold"})
        coupons = [span.get_text() for span in spans if span.get_text().find("Rabattgutschein") != -1]
        if coupons != []:
            coupon = coupons[0]
        else:
            coupon_euro, coupon_pct, coupon = 0, 0, 0
        # convert prices to float
        list_of_prices = [price, price_ourprice, price_dealprice]
        for i in range(len(list_of_prices)):
            if list_of_prices[i] != None:
                # get price as string
                list_of_prices[i] = list_of_prices[i].get_text().replace('.','').replace(',','.')
                # string to float - replace any non-digits and non-"." by ""
                list_of_prices[i] = float(re.sub(r"[^\d.]", "", list_of_prices[i]))
        price, price_ourprice, price_dealprice = list_of_prices
        if coupon != 0:
            if '€' in coupon:
                coupon_euro = float(re.sub(r"[^\d]", "", coupon)) / 100
                coupon_pct = 0
            else:
                coupon_euro = 0
                coupon_pct = float(re.sub(r"[^\d]", "", coupon)) / 100
        # print(price, price_ourprice, price_dealprice, coupon_euro, coupon_pct)

        # write to details
        if price_dealprice is None and coupon == 0:            
            details["deal"] = False
        price = price or price_ourprice or price_dealprice # this works almost like the coalesce function
        if title is not None and price is not None:
            details["name"] = title.get_text().strip()
            details["price"] = price
            details["ourprice"] = price_ourprice
            details["dealprice"] = price_dealprice
            details["coupon_euro"] = coupon_euro
            details["coupon_pct"] = coupon_pct
            details["finalprice"] = round((min([x for x in [price, price_ourprice, price_dealprice]
                                         if x != None]) - coupon_euro) * (1-coupon_pct),2)
            details["url"] = _url
        else:
            return None
    return details

def get_asin(details):
    return details["url"][len(details["url"])-10:len(details["url"])]