import numpy as np 
import pandas as pd 
from sqlalchemy import create_engine
import json

def lambda_handler(event, context):
    host=""
    port=5432
    dbname="election_data"
    user="ayush"
    password=""
    conn = create_engine('mysql+pymysql://{0}:{1}@{2}/{3}'
                .format(user, password,host, dbname)).connect()
                
    query = """WITH cands AS (SELECT candidate_id, 
        co.contest_id, 
        candidate_name, 
        candidate_party
    FROM 
    contests co JOIN candidates ca ON co.contest_id = ca.contest_id
    WHERE co.sheet_number = 2 AND co.election_year = 2016 AND ca.election_month = 11)
    
    SELECT 
        candidate_name,
        candidate_party,
        county_name, 
        total_votes 
    FROM results_by_county rbc JOIN cands cad ON rbc.candidate_id = cad.candidate_id
    ORDER BY candidate_name, county_name;"""
    
    total_results = pd.read_sql_query(query, conn)
    pivoted_results = pd.DataFrame({"county_name": total_results.county_name.unique()})
    result_column = "total_votes"
    
    for candidate in total_results.candidate_name.unique():
        pivoted_results[candidate] = total_results[total_results.candidate_name == candidate].reset_index()[result_column]
    
    conn.close()
    
    return {
        'statusCode': 200,
        'body': pivoted_results.to_json()
    }
