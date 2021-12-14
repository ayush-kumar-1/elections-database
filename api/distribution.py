import numpy as np 
import pandas as pd 
from sqlalchemy import create_engine
import json

def lambda_handler(event, context):
    """
    Returns voter turnout on a single county on a single axis. 
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
        try: 
            axis = event['queryStringParameters']["axis"]
        except KeyError: 
            axis = 'age_grp' 
        try: 
            metric = event['queryStringParameters']["metric"]
        except KeyError: 
            metric = "voted"
    else: 
        year = 2016
        month = 11
        county = 'Fulton'
        axis = 'age_grp'
        metric = 'voted'

    metrics =  ["voted", "registered", "turnout"]

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
    assert year > 1990 and year < 2022
    assert month > 0 and month < 13 
    assert axis in ["age_grp", "gender", "race"]
    assert metric in metrics
    
    metric_strings = ["SUM(voted)", "SUM(registered)", "SUM(voted)/SUM(registered)"]
    
    query = """SELECT {0}, {2} AS {3}
                FROM county_turnout
                WHERE county_name = '{1}'
                GROUP BY {0} 
                ORDER BY {0}; 
                    """.format(axis, county, metric_strings[metrics.index(metric)], metric)
    
    conn = connect_to_database()
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return {
        'statusCode': 200,
        'body': df.to_json()
    }
