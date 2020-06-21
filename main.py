
from scraper import get_product_details, get_asin               # get information from amazon
from db import add_product_detail, get_product_history          # write information to mongodb
from helper import analyze_and_add_db_history, have_internet    # helper functions i. e. manipulations on url.csv
from mail import send_mail, mail_text_notification, mail_text_overview      # send emails
from time import sleep
from datetime import datetime                                   # get todays date
import yaml                                                     # config
import pandas as pd
import os
import sys


def amazon_price_checker():
    # check for internet connection:
    if have_internet() == False:
        sys.exit()

    # 0. Load config
    with open('config.yaml') as f:
        config_url = yaml.load(f, Loader=yaml.FullLoader)['url_csv'][0]
    with open('config.yaml') as f:
        config_mail = yaml.load(f, Loader=yaml.FullLoader)['mail'][0]
    
    # 1. read csv and write backup
    df_url = pd.read_csv(config_url['url_csv_name'], delimiter=';', decimal = ',')
    df_url.to_csv(config_url['url_csv_backup_name'], sep = ';', decimal = ',')
    # 2. get ASINs for each url
    list_historie = []
    for i in range(len(df_url)):
        details = get_product_details(df_url.loc[i, "url"]) # scraper
        if details is None:
            df_url.loc[i, "error"] = True
        else:
            df_url.loc[i, "asin"] = get_asin(details) # scraper
            df_url.loc[i, "url_short"] = details["url"]
            # 3. update MongoDB
            inserted = add_product_detail(details) # db
            if inserted:
                df_url.loc[i, "error"] = False
            else:
                df_url.loc[i, "error"] = True
            # 4. get_history for each ASIN from MongoDB
            list_historie += get_product_history(df_url.loc[i, "asin"])['details'] # db
    # 5. analyze list and merge to url
    df_db = pd.DataFrame(list_historie)
    df_url = analyze_and_add_db_history(df_url, df_db) # helper
    # 6. save some informations to csv 
    # try to write to csv, if it's locked, try again later.
    # unfortunately all manual informations (added during the run of this programm) will be lost
    checker_save = 0
    while checker_save < 6:
        try:
            df_url.to_csv(config_url['url_csv_name'], sep = ';', decimal = ',')
            # os.remove(config_url['url_csv_backup_name']) # delet backup
            checker_save = 6
        except:
            sleep(60)
            checker_save += 1

    # 7. send mail
    for email in df_url['e_mail'].fillna(config_mail['default_address']).unique():
        # 7.1 send daily notifications
        if email != config_mail['default_address']:
            df_url_send = df_url[(df_url['error'] == False) & (df_url['e_mail'] == email)].copy() # send error only to main user
        else:
            df_url_send = df_url[(df_url['error'] == True) | (df_url['e_mail'] == email)].copy()
        # check if a) error exists or b) notification exists or c) new entry exists
        if df_url_send['error'].max() == True or df_url_send['f_notification'].max() == True or 0  in df_url_send['last_price'].unique():
            message = mail_text_notification(df_url_send)
            send_mail('An announcement from your amazon_price_tracker', message, email)

        # 7.2 send weekly overview
        if datetime.today().weekday() == 5: # if today is Saturday
            message = mail_text_overview(df_url_send)
            send_mail('Your weekly overview from your amazon_price_tracker', message, email)
    return df_url