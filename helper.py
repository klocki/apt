import pandas as pd

def analyze_and_add_db_history(df_url, df_db):
    # all_time_max_finalprice
    max_price = df_db.groupby(['url'])['finalprice'].max().reset_index().rename(columns={'url': 'url_short', 'finalprice': 'all_time_max_price'})
    # all_time_min_finalprice
    min_price = df_db.groupby(['url'])['finalprice'].min().reset_index().rename(columns={'url': 'url_short', 'finalprice': 'all_time_min_price'})
    # initial_date
    tmp_initial_date = df_db.groupby(['url'])['date'].min().reset_index()
    initial_date = pd.merge(df_db, tmp_initial_date, on = ['url', 'date']).rename(columns={'url': 'url_short', 'date': 'initial_date', 'finalprice': 'initial_price'})
    # current_date
    tmp_current_date = df_db.groupby(['url'])['date'].max().reset_index()
    current_date = pd.merge(df_db, tmp_current_date, on = ['url', 'date']).rename(columns={'url': 'url_short', 'date': 'current_date', 'finalprice': 'current_price', 'price': 'current_regular_price', 'deal': 'f_deal'})
    
    # merge informations to url.csv
    df_url = df_url[['url', 'e_mail', 'error', 'asin', 'url_short', 'current_price']].rename(columns={'current_price': 'last_price'})
    df_url['last_price'] = df_url['last_price'].fillna(0)
    df_url = pd.merge(df_url, max_price, on = 'url_short', how = 'left')
    df_url = pd.merge(df_url, min_price, on = 'url_short', how = 'left')
    df_url = pd.merge(df_url, initial_date[['url_short', 'initial_date', 'initial_price']], on = 'url_short', how = 'left')
    df_url = pd.merge(df_url, current_date[['url_short', 'current_date', 'current_price', 'current_regular_price', 'f_deal', 'name']], on = 'url_short', how = 'left')
    df_url['f_notification'] = df_url['last_price'] > df_url['current_price']
    # for price in [price for price in df_url.keys() if price.find('price') != -1]:
    #     df_url[price] = df_url[price].apply(lambda x: "{:,.2f}€".format(x))
    df_url = df_url[['url', 'e_mail', 'name', 'f_deal', 'current_price', 'current_regular_price', 'last_price', 'all_time_min_price', 'all_time_max_price', 'initial_price', 'initial_date', 'current_date', 'f_notification', 'url_short', 'error']]

    return df_url



import http.client as httplib

def have_internet():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False