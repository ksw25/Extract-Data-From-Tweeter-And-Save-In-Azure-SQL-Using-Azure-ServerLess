import logging
import sqlalchemy
import pyodbc
import pandas as pd
import urllib
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

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

    else:
        return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
        )
