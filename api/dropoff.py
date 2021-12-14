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
            year = int(event['queryStringParameters']["year"])
        except KeyError: 
            year = 2016

        try: 
            month = int(event['queryStringParameters']["month"]) 
        except KeyError: 
            month = 11
        try: 
            county = event['queryStringParameters']["county_name"]
        except KeyError: 
            county = 'Fulton'
    else: 
        year = 2016
        month = 11
        county = 'Fulton'

        
    #input validation 
    assert county in ["Appling","Atkinson","Bacon","Baker","Baldwin","Banks","Barrow","Bartow","Ben Hill",
        "Berrien","Bibb","Bleckley","Brantley","Brooks","Bryan","Bulloch","Burke","Butts","Calhoun","Camden",
        "Candler","Carroll","Catoosa","Charlton","Chatham","Chattahoochee","Chattooga","Cherokee","Clarke","Clay",
        "Clayton","Clinch","Cobb","Coffee","Colquitt","Columbia","Cook","Coweta","Crawford","Crisp","Dade","Dawson",
        "Decatur","DeKalb","Dodge","Dooly","Dougherty","Douglas","Early","Echols","Effingham","Elbert","Emanuel",
        "Evans","Fannin","Fayette","Floyd","Forsyth","Franklin","Fulton","Gilmer","Glascock","Glynn","Gordon",
        "Grady","Greene","Gwinnett","Habersham","Hall","Hancock","Haralson","Harris","Hart","Heard","Henry","Houston",
        "Irwin","Jackson","Jasper","Jeff Davis","Jefferson","Jenkins","Johnson","Jones","Lamar","Lanier","Laurens",
        "Lee","Liberty","Lincoln","Long","Lowndes","Lumpkin","Macon","Madison","Marion","McDuffie","McIntosh","Meriwether",
        "Miller","Mitchell","Monroe","Montgomery","Morgan","Murray","Muscogee","Newton","Oconee","Oglethorpe","Paulding",
        "Peach","Pickens","Pierce","Pike","Polk","Pulaski","Putnam","Quitman","Rabun","Randolph","Richmond","Rockdale",
        "Schley","Screven","Seminole","Spalding","Stephens","Stewart","Sumter","Talbot","Taliaferro","Tattnall","Taylor",
        "Telfair","Terrell","Thomas","Tift","Toombs","Towns","Treutlen","Troup","Turner","Twiggs","Union","Upson","Walker",
        "Walton","Ware","Warren","Washington","Wayne","Webster","Wheeler","White","Whitfield","Wilcox","Wilkes","Wilkinson",
        "Worth"]
    
    query = """SELECT co.contest_name, co.sheet_number, SUM(total_votes) AS total_votes
                FROM candidates ca 
                JOIN contests co ON ca.contest_id = co.contest_id
                JOIN results_by_county rbc ON ca.candidate_id = rbc.candidate_id
                WHERE county_name = '{0}' AND co.election_month = 11 AND co.election_year = 2016
                GROUP BY contest_name
                ORDER BY total_votes DESC;""".format(county)
    
    conn = connect_to_database()
    turnout = pd.read_sql_query(query, conn)
    conn.close()
    
    return {
        'statusCode': 200,
        'body': turnout.to_json()
    }