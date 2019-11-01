# Extract-Data-From-Tweeter-And-Save-In-Azure-SQL-Using-Azure-ServerLess
## Project Statement:

Given a twitter ID, get a minimum of 100 followers (Modified this to keep in Azure function 5-10 min timeout period) and for each follower gather upto 200 tweets
Store the tuple (twitterID,followerID,tweetID,tweet) into a table managed in Azure Sql Service.
1) You will have to create and setup a free Azure account.
2) Create a database, and a table in that Azure account.
3) Create a twitter account with API 
4). given twitter ID, gather follower ids of that twitter ID
4.1) for each of the follower ID gather upto 200 original tweets 
--- exclude retweets, messages 
5) Store that into the Azure table
6) Write a client to query that Azure table.
6.1) List all tweets for a given twitter ID
6.2) List follower ID for a given twitter ID

## Technology Used:
	1.	Python
	2.	Twython library to extract tweeter data
	3.	Azure Function
	4.	Azure SQL server
 
### Things I learned:
	1.	Azure SQL Server Usage from localhost as well as Azure Server-less and Azure Databricks.
	2.	Azure Function.
	3.	Learned twython library usage to extract tweets .

## Brief Summary of steps followed while doing the project:
	1.	Created a Tweeter Developer Account.
	2.	Wrote a python script to extract the Follower's ID for a given User ID. 
  
```python
def get_follower_ids(user_id="25073877"):
              # IF you want to LookUp with ScreenName
              #data=list((python_tweets.get_followers_ids(screen_name="screen_name")["ids"]))
              data=list((python_tweets.get_followers_ids(user_id=user_id)["ids"]))

              return(data)
```
	3.	Wrote a python script the take Followers ID extracted in the previous step and retrieve at max 200 tweets for each. 
  
  ```python
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
```
	4.	Created an Azure SQL database.
	5.	Wrote a python script to take the result from step 3 and save it to the Azure SQL server.
  
  ```python
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
  ```
	6.	Created an Azure function project and func. Modify script to work on Azure Function.
	7.	Create 2 More Client functions for the following purpose.
	◦	List all tweets for a given twitter ID
  ```python
  if name:
        pd.set_option('display.max_colwidth', -1)
        pd.set_option('display.max_rows', 1000)
        params = urllib.parse.quote_plus("Driver={ODBC Driver 17 for SQL Server};Server=tcp:trailtwitterdb.database.windows.net,1433;Database=Trail1twitter;Uid=<USER ID>;Pwd=<PASSWORD>;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
        engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
        # result = engine.execute('SELECT COUNT(*) FROM [dbo].[tweeterdata]')
        # result.fetchall()
        query = "Select [tweeterdata].[tweet] from [dbo].[tweeterdata] WHERE [dbo].[tweeterdata].[followerID]={};  ".format(name)
        logging.info(query)
        df = pd.read_sql(query, engine)
        print(df)
        if df.shape[0]!=0:
            return func.HttpResponse(f" {df}")
        else:
            return func.HttpResponse(f" No Tweets for Twitter ID {name}!")
  
  ```
	◦	List follower ID for a given twitter ID
  ```python
  if name:
        logging.info("Starting")
        pd.set_option('display.max_colwidth', -1)
        pd.set_option('display.max_rows', 1000)
        params = urllib.parse.quote_plus("Driver={ODBC Driver 17 for SQL Server};Server=tcp:trailtwitterdb.database.windows.net,1433;Database=Trail1twitter;Uid=<User ID>;Pwd=<Password>;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
        engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
        # result = engine.execute('SELECT COUNT(*) FROM [dbo].[tweeterdata]')
        # result.fetchall()
        query = "Select distinct [tweeterdata].[followerID] from [dbo].[tweeterdata] WHERE [dbo].[tweeterdata].[twitterID]={};  ".format(name)
        logging.info(query)
        df = pd.read_sql(query, engine)
        
        print(df)
        if df.shape[0]!=0:
            return func.HttpResponse(f" {df}")
        else:
            return func.HttpResponse(f" NO Followers Data for Twitter ID {name}!")

  ```

## Links for each Function:(These are just template for you guys to look over. I have turned off the activation of these links so that they won't work. **I am not rich, sadly:cry::cry:.**)
	
	Task 1: To save Followers' ID and their Respective Tweets.(Placed in TweetWork in MyFunctionProj Directory)
	◦	https://demo.azurewebsites.net/api/Tweetwork
	◦	for example https://demo.azurewebsites.net/api/Tweetwork?name=25073877
	
	Task 2: List all tweets for a given twitter ID. (Placed in Client1BigData in MyFunctionProj Directory)
	◦	https://demo.azurewebsites.net/api/Client1BigData?code=NyhLElXnjBz08QButk1jkbaYLVdJE9vAKnX09CN1vrg==
	◦	for example https://demo.azurewebsites.net/api/Client1BigData?code=NyhLElXnjBz08QButk1jkbaYLVdJE9vAK9CN1vrg==&name=979178022367461376
	
	Task 3: List follower ID for a given twitter ID. (Placed in Client2BigData in MyFunctionProj Directory)
	◦	https://demo.azurewebsites.net/api/Client1BigData?code=NyhLElXnjBz08QButk1jkbaYLVdJE9vAK9CN1vrg==
	◦	for example https://demo.azurewebsites.net/api/client2bigdata?code=2MO/r/Wvk5JQFsbQ1KKkA0hdWF1OCfdeyZjpENpoNkVGIS57Waw==&name=25073877

## Challenges Faced:
* If you are using Mac for debugging Azure function in Visual Studio, it is very hard as sometimes Visual studio does not create an exact extension/helper file to make debugging work. Personally, For me, It didn't work at all. I had to push function online every time i wanted to check it. **But I found the solution for it now.**There are 3 files in .vscode then are sometimes screwed up. I would be mentioning them and what should they looks like.
Namely,
1. *task.json*
```json
   {
  "version": "2.0.0",
  "tasks": [
    {
      "type": "func",
      "command": "host start",
      "problemMatcher": "$func-watch",
      "isBackground": true,
      "dependsOn": "pipInstall"
    },
    {
      "label": "pipInstall",
      "type": "shell",
      "osx": {
        "command": "/Users/karanwadhwa/Downloads/Big\\ Data\\ Online/P1/MyFunctionProj/.venv/bin/python3.6 -m pip install -r MyFunctionProj/requirements.txt"
      },
      "windows": {
        "command": "${config:azureFunctions.pythonVenv}\\Scripts\\python -m pip install -r requirements.txt"
      },
      "linux": {
        "command": "${config:azureFunctions.pythonVenv}/bin/python -m pip install -r requirements.txt"
      },
      "problemMatcher": [
        
      ]
    }
  ]
}
```

2. *launch.json*
  
```json
   {
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach to Python Functions",
      "type": "python",
      "request": "attach",
      "port": 9091,
      "preLaunchTask": "func: host start"
    }
  ]
}
```
   
3. *settings.json*
   
```json
   {
    "python.pythonPath": "<Python path>",
    "azureFunctions.deploySubpath": "<MyFunctionProj directory name>",
    "azureFunctions.scmDoBuildDuringDeployment": true,
    "azureFunctions.pythonVenv": ".venv",
    "azureFunctions.projectLanguage": "Python",
    "azureFunctions.projectRuntime": "~2",
    "debug.internalConsoleOptions": "neverOpen"
}
   
```
  
* Azure Functions has its limitation as compared to AWS lambda. When I started writing it, I thought it would be the same as AWS lambda as both are serverless, but implementing it was way hard for two reasons. First, Azure function does not allow online code editing, which is provided by AWS.


## Follow up:
* If I was making this for a company and had enough resources, I would have gone with Azure function Dedicated App Plan which have maximum time limit of 30 mins.


