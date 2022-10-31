# This app performs analysis on the gitcoin grant applications json files 
# The analysis includes reviews of offchain data to identify issues in submission validity
# A score is assigned based on checks made using the address and the description
# A higher number means higher need of scrutiny. Lower number means less red flags

from web3 import Web3
import re
import pandas as pd
import requests
import os


def valid_wallet(row, score, comments):
    # Check if wallet is valid
    is_valid_address = Web3.isAddress(row["address"])
    if (is_valid_address):
        score+=0
        comments.append("Valid Ethereum Address. ")
    else:
        score+=2
        comments.append("Invalid Ethereum Address. ")

    return comments, score; 

def check_links_in_desc(row, score, comments):
    #checks description for links and will identify if they are valid connections or not
    desc = row["description"]
    try:
        mentioned_websites = re.findall("(?P<url>https?:[^\s]+)", desc)
        for site in mentioned_websites:
            try:    
                website_status = requests.head(site, timeout=2).status_code
            except:
                website_status = 0

            if (website_status == 200):
                score+=0
                comments.append("{0} connection successful. ".format(site))
            else:
                score+=1
                comments.append("{0} unable to be reached. ".format(site))
    except:
        score+=1
        comments.append("No external links found in description.")

    return comments, score;


def app_analysis(json_app_file):
    df = pd.read_json(json_app_file).T
    result_data = {'grant_id' : []
                , 'title' : []
                , 'review_level' : []
                , 'address' : []
                , 'description' : []
                , 'comments': []}

    for index, row in df.iterrows():
        comments = []
        comments, score = valid_wallet(row, 0, comments)
        comments, score = check_links_in_desc(row, score, comments)

        result_data['grant_id'].append(row['grant_id'])
        result_data['title'].append(row['title'])
        result_data['review_level'].append(score)
        result_data['address'].append(row['address'])
        result_data['description'].append(row['description'])
        result_data['comments'].append(''.join(comments))

    filename_noext = os.path.splitext(json_app_file)[0]
    project_rating = pd.DataFrame(result_data)
    project_rating.sort_values(by='review_level', ascending=False).to_csv('{0}_analysis.csv'.format(filename_noext), index=False)

app_analysis("grants_applications_gr15.json")
