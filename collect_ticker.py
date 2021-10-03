import twint, re, smtplib, nest_asyncio, settings
import pandas as pd
from datetime import date, timedelta
nest_asyncio.apply()

def twint_to_pandas(columns): #Creds to Favio Vazques
    return twint.output.panda.Tweets_df[columns]

def getTweets(username): #runs a twint search and returns a pandas df
    c = twint.Config()
    c.Username = username 
    c.Limit = 2000
    c.Hide_output = True
    c.Pandas = True
    c.Since = (date.today()).strftime("%Y-%m-%d") #startDate
#     c.Until = (date.today() + timedelta(1)).strftime("%Y-%m-%d") #endDate
    twint.run.Search(c)
    
    try:
        df = twint_to_pandas(["date", "username", "tweet"])
    except Exception as e:
        print("No data available for today!")
        df = pd.DataFrame()
        
    return df    

def send_email(df):
    gmail_user = settings.EMAIL_USERNAME
    gmail_password = settings.EMAIL_PASSWORD
    sent_from = gmail_user
    to = [settings.EMAIL_TO]
    subject = ', '.join(df.ticker[0]) + " ticker!!"
    body = df.tweet.loc[0]

    email_text = """From:{0}\nTo:{1}\nSubject:{2}\n\n{3}""".format(sent_from, to, subject, body)

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        print ("Email sent successfully!")
    except Exception as ex:
        print ("Something went wrong….",ex)

def check_last_tweet(df):
    """
    Description: Checks if the latest tweet is true and if it has any new ticker

    returns: boolean
    """
    df_old = pd.read_csv("tweets.csv")
    df_ticker_old = pd.read_csv('ticker.csv')
    ticker_old = set(df_ticker_old.ticker.unique())
    ticker_new = set(df.head(2).ticker.explode())
    if len(ticker_new) > 0:
        #Check if latest tweet is same as first tweet in csv
        if df_old.tweet.loc[0] != df.tweet.loc[0] and not ticker_new.issubset(ticker_old) :
            df.head(10).to_csv("tweets.csv", index=False)
            with open('ticker.csv','a') as fd:
                new_tickers = ticker_new - ticker_old 
                new_tickers = {x for x in new_tickers if x==x}
                print(new_tickers)
                for t in new_tickers:
                    fd.write('\n')
                    fd.write(t)
            return True # TODO: check two tweets with old tweets
        else:
            return False

if __name__ == "__main__":
    df = pd.DataFrame()
    df = getTweets("Stark011235")
    df["ticker"] = df.tweet.apply(lambda x: ['$' + i for i in re.findall(r'\$(\w+)', x)])
    if check_last_tweet(df):
        send_email(df)