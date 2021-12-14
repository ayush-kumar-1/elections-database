import numpy as np 
import pandas as pd 
from sqlalchemy import create_engine
import json

def lambda_handler(event, context):
    """
    Returns voter turnout by county on zero to three conditions across gender, race, and/or 
    age group. Currently only supports single selection (i.e. single race or all). 
    """
    
    if 'queryStringParameters' in event and event['queryStringParameters'] is not None: 
        try: 
            gender = event['queryStringParameters']["gender"]
        except KeyError: 
            gender = None
            
        try: 
            age_grp = event['queryStringParameters']["age_grp"]
        except KeyError: 
            age_grp = None
        
        try:
            race = event['queryStringParameters']["race"]
        except KeyError:
            race = None
    else: 
        gender = None
        race = None
        age_grp = None
        
    #input validation 
    assert gender in [None, "MALE", "FEMALE"]
    assert race in [None, "BLACK", "WHITE", "ASIA-PI", "NATIVE-AM", "HISP-LT"]
    assert age_grp in [None, "18-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-OVER"]
    
    where_condn = ""
    if gender or race or age_grp:
        where_condn = "WHERE "
        gender_condn = f"gender = '{gender}'" if gender is not None else None
        age_condn = f"age_grp = '{age_grp}'" if age_grp is not None else None
        race_condn = f"race = '{race}'" if race is not None else None
        where_condn += (" AND ".join([cond for cond in [gender_condn, age_condn, race_condn] if cond]))
    
    query = """SELECT county_name, SUM(voted)/SUM(registered) AS turnout FROM county_turnout 
                {0}
                GROUP BY county_name 
                ORDER BY county_name;""".format(where_condn)
    
    conn = connect_to_database()
    turnout = pd.read_sql_query(query, conn)
    conn.close()
    
    return {
        'statusCode': 200,
        'body': turnout.to_json()
    }