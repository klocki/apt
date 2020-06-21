import yaml     # config
import smtplib  # for sending mail
from email.mime.multipart import MIMEMultipart  # for sending mail
from email.mime.text import MIMEText            # for sending mail
# from string import Template # we don't need this here I guess


def send_mail(subject, message, to):
    with open('config.yaml') as f:
        config_mail = yaml.load(f, Loader=yaml.FullLoader)['mail'][0]

    # set up the SMTP server
    s = smtplib.SMTP(host='smtp.web.de', port=587)
    s.starttls()
    s.login(config_mail['my_adress'], config_mail['password'])

    msg = MIMEMultipart()       # create a message

    # Prints out the message body for our sake
    # print(message)

    # setup the parameters of the message
    msg['From']=config_mail['my_adress']
    msg['To']=to
    msg['Subject']=subject
    
    # add in the message body
    msg.attach(MIMEText(message, 'html'))
    
    # send the message via the server set up earlier.
    s.send_message(msg)
    del msg
    
    # Terminate the SMTP session and close the connection
    s.quit()
    return None


def mail_text_notification(df):
    # 1. mail_head
    mail_text = '''\
    <html>
    <head></head>
    <body>
        <p>Hello,<br><br>
        
    '''
    df_email_notification = df[(df['error'] == False) & (df['f_notification'] == True)].reset_index()
    if len(df_email_notification) != 0:
        # 2. Write table with price reduced items
        mail_text += 'the following items on your tracking list got an price reduction:<br>'
        # define table head
        mail_text += set_table_head() 
        # add column names
        mail_text += set_table_values('Item name', 'price', 'reg_price', 'min_price', 'max_price', 'ini_price', 'date')
        # add rows
        for i in range(len(df_email_notification)):
            item_link               = df_email_notification.loc[i,'url']
            item_name               = "{:30}".format(df_email_notification.loc[i,'name'])
            item_price              = "{:6.2f}".format(df_email_notification.loc[i,'current_price'])
            item_regular_price      = "{:6.2f}".format(df_email_notification.loc[i,'current_regular_price'])
            item_all_time_min_price = "{:6.2f}".format(df_email_notification.loc[i,'all_time_min_price'])
            item_all_time_max_price = "{:6.2f}".format(df_email_notification.loc[i,'all_time_max_price'])
            item_initial_price      = "{:6.2f}".format(df_email_notification.loc[i,'initial_price'])
            item_current_date       = "{:%d.%m.%y}".format(df_email_notification.loc[i,'current_date'])
            mail_text += set_table_values('<a href="'+item_link+'">'+item_name+'</a>', item_price, item_regular_price,
                                            item_all_time_min_price, item_all_time_max_price, item_initial_price, 
                                            item_current_date)
        # close table
        mail_text += set_table_tail()
    
    df_email_new_itmes = df[(df['error'] == False) & (df['last_price'] == 0)].reset_index()
    if len(df_email_new_itmes) != 0:
        # 3. Write table with new items
        mail_text += 'the following items are new on your tracking list:<br>'
        mail_text += set_table_head() 
        mail_text += set_table_values('Item name', 'price', 'reg_price', 'date')
        # add rows    
        for i in range(len(df_email_new_itmes)):
            item_link               = df_email_new_itmes.loc[i,'url']
            item_name               = "{:30}".format(df_email_new_itmes.loc[i,'name'])
            item_price              = "{:6.2f}".format(df_email_new_itmes.loc[i,'current_price'])
            item_regular_price      = "{:6.2f}".format(df_email_new_itmes.loc[i,'current_regular_price'])
            item_current_date       = "{:%d.%m.%y}".format(df_email_new_itmes.loc[i,'current_date'])
            mail_text += set_table_values('<a href="'+item_link+'">'+item_name+'</a>', item_price, item_regular_price,
                                            item_current_date)
        mail_text += set_table_tail()

    df_mail_errors = df[(df['error'] == True)].reset_index()
    if len(df_mail_errors) != 0:
        # 4. Write table with error items
        mail_text += 'for following items an error occure:<br>'
        mail_text += set_table_head() 
        mail_text += set_table_values('Item link')
        # add rows    
        for i in range(len(df_mail_errors)):
            item_link               = "{:30}".format(df_mail_errors.loc[i,'url'])
            mail_text += set_table_values(item_link)
        mail_text += set_table_tail()

    # 5. mail tail
    mail_text += """\
    <br><br><br>
    Greatings your amazon price tracker <br>
    </p>
    </body>
    </html>
    """
    return mail_text


def mail_text_overview(df):
    # 1. mail_head
    mail_text = '''\
    <html>
    <head></head>
    <body>
        <p>Hello,<br><br>
        
    '''
    # 2. Write table with all items
    mail_text += 'the following items are on your tracking list:<br>'
    # define table head
    mail_text += set_table_head() 
    # add column names
    mail_text += set_table_values('Item name', 'price', 'reg_price', 'min_price', 'max_price', 'ini_price', 'date')
    # add rows
    df_email_overview = df[(df['error'] == False)].reset_index()
    for i in range(len(df_email_overview)):
        item_link               = df_email_overview.loc[i,'url']
        item_name               = "{:30}".format(df_email_overview.loc[i,'name'])
        item_price              = "{:6.2f}".format(df_email_overview.loc[i,'current_price'])
        item_regular_price      = "{:6.2f}".format(df_email_overview.loc[i,'current_regular_price'])
        item_all_time_min_price = "{:6.2f}".format(df_email_overview.loc[i,'all_time_min_price'])
        item_all_time_max_price = "{:6.2f}".format(df_email_overview.loc[i,'all_time_max_price'])
        item_initial_price      = "{:6.2f}".format(df_email_overview.loc[i,'initial_price'])
        item_current_date       = "{:%d.%m.%y}".format(df_email_overview.loc[i,'current_date'])
        mail_text += set_table_values('<a href="'+item_link+'">'+item_name+'</a>', item_price, item_regular_price,
                                        item_all_time_min_price, item_all_time_max_price, item_initial_price, 
                                        item_current_date)
    # close table
    mail_text += set_table_tail()
    
    # 3. mail tail
    mail_text += """\
    <br><br><br>
    Greatings your amazon price tracker <br>
    </p>
    </body>
    </html>
    """
    return mail_text

# this functions defines the tables head
def set_table_head():
    table_text = '''\
    <table style="width:100%">\n'''
    return table_text

def set_table_values(*args):
    table_text = '<tr>\n'
    for arg in args:
        table_text += '<th>' + str(arg) + '</th>\n'
    table_text += '</tr>\n'
    return table_text

def set_table_tail():
    table_text = '</table>\n<br><br>\n'''
    return table_text

