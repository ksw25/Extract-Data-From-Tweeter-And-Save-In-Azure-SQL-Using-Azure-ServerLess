import logging
import pandas as pd
from twython import Twython
import pandas as pd
import azure.functions as func
import sqlalchemy
import pyodbc
import urllib


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        logging.info('Function started')
        try:
            
            # Instantiate an object
            
            python_tweets = Twython(<Your CONSUMER_KEY>,<Your CONSUMER_SECRET >)
            logging.info('Function started.')

            # Function to extarct Tweeter Followers for a Given User_ID
            def get_follower_ids(user_id="25073877"):
                # IF you want to LookUp with ScreenName
                #data=list((python_tweets.get_followers_ids(screen_name="screen_name")["ids"]))
                data=list((python_tweets.get_followers_ids(user_id=user_id)["ids"]))
                
                return(data)

            # Function to extarct 200 Tweets for each  Followers_ID for a Given User_ID
            def get_followers_tweet_data(follower_ids,screen_name):
                counter=0
                output=[]
                logging.info("Inside Get_follower_tweet")
                for person in follower_ids:
                    
                    if counter>=100:
                        break
                    try:
                        result=python_tweets.get_user_timeline(user_id=person,count=200,include_rts=False,exclude_replies=True,trim_user=True)
                        # IF you want to LookUp with ScreenName
                        #result=python_tweets.get_user_timeline(screen_name="realDonaldTrump",count=200,include_rts=False,exclude_replies=True,trim_user=True)
                        if result:
                            h=[]
                            for tweet in result:
                                h.append((screen_name,person, tweet['id'],tweet['text']))
                                last_id = tweet['id']
                            size=len(h)

                            new_last_id=-1
                            while (size<200 and last_id!=new_last_id):
                            
                                last_id=new_last_id
                                result = python_tweets.get_user_timeline(user_id=person, count = 200, max_id = last_id,include_rts=False,exclude_replies=True,trim_user=True)
                                # IF you want to LookUp with ScreenName
                                #result = python_tweets.get_user_timeline(screen_name='realDonaldTrump', count = 200, max_id = last_id)
                                for tweet in result:
                                    h.append((screen_name,person, tweet['id'],tweet['text']))
                                    new_last_id = tweet['id']
                                size=len(h)
                            output+=h
                            counter+=1
                    except :
                        continue
                return output

            def Save_to_database(df):
                import sqlalchemy
                import pyodbc
                import pandas as pd
                import urllib
                logging.info("Initiating save to databse function")
              
                params = urllib.parse.quote_plus("Driver={ODBC Driver 17 for SQL Server};Server=tcp:trailtwitterdb.database.windows.net,1433;Database=Trail1twitter;Uid=<Your USer ID>;Pwd=<Your PAssword>;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
                engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
                engine.execute("delete from [dbo].[tweeterdata];")
                logging.info(df)
                df.to_sql("tweeterdata", engine,if_exists='append',schema="dbo")

            logging.info("initiating")
            screen_name=str(name)
            follower_ids=get_follower_ids(screen_name)
            logging.info("follower done")
            output=get_followers_tweet_data(follower_ids,screen_name)
            logging.info("Tweet Extractedd")
            data_new=pd.DataFrame(output,columns=["twitterID","followerID","tweetID","tweet"])
            logging.info("Data_Frame Created")
            
            logging.info("start saving")
            Save_to_database(data_new)
            logging.info("Saved")
            return func.HttpResponse(f"Successfully Extracted and saved result for {name}.")
        except:
            logging.info("error while doing it")
    else:
        return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
        )
