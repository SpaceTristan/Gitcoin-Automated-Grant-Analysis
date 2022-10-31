# This app performs analysis on the gitcoin application json files 
# The analysis includes reviews of offchain data to identify issues in submission validity
# A score is assigned based on checks made against the twitter acounts, github existence and website response
# A higher number means higher need of scrutiny. Lower number means less red flags

import pandas as pd
import requests
import os

def twitter_validation(row, score, comments):
    # This function checks if the twitter is verified or not and if twitter handle has been provided
    # points are given if a twitter account needs validation, does not exist or if only one account is provided
    twit1 = row['twitter_handle_1']
    twit2 = row['twitter_handle_2']
    twit_verified = row['twitter_verified']

    if (twit_verified is False):
        if(twit1 is None):
            score += 1
            comments.append("No primary twitter account. ")
        if (twit2 is None):
            score += 1
            comments.append("No secondary twitter account provided. ")
        if (twit1 is not None and twit1 == twit2):
            score = score + 1
            comments.append("Only one twitter account provided, needs validation. ")
        if (score == 0):
            score += 1
            comments.append("Twitter account needs validation. ")
    elif (twit_verified is True):
        if (twit1 is None and twit1 == twit2):
            score += 1
            comments.append("No twitter account provided. ")
    return comments, score;

def website_validation(row, score, comments):
    # This function checks if a website exists or not, timeout set to 2 because I don't want running this to take all day
    url = row['website']
    try:    
        website_status = requests.head(url, timeout=2).status_code
    except:
        website_status = 0
    # not including 301 because if redirecting that will need to be checked out at a 2 level
    if (website_status == 200):
        score+=0
        comments.append("Website connection successful. ")
    else:
        score+=2
        comments.append("Website unable to be reached." )

    return comments, score;

def github_validation(row, score, comments):
    # checking if the github path provided is responsive or not and if it redirects that will add a point
    gh = row['github_project_url']

    try:
        website_status = requests.head(gh).status_code
    except:
        website_status = 0

    if (website_status == 200):
        score+=0
        comments.append("Github is up and working. ")
    elif (website_status == 301):
        score+=1
        comments.append("Github page is different than listed. ")
    else:
        score+=2
        comments.append("Github page does not exist .")

    return comments, score;

def grant_analysis(json_app_file):
    df = pd.read_json(json_app_file).T
    result_data = {'grant_id' : []
                , 'title' : []
                , 'review_level' : []
                , 'website' : []
                , 'github_project_url' : []
                , 'twitter_handle_1' : []
                , 'twitter_handle_2' : []
                , 'comments': []}

    for index, row in df.iterrows():
        comments = []
        comments, score = twitter_validation(row, 0, comments)
        comments,score = website_validation(row, score, comments)
        comments,score = github_validation(row, score, comments)

        result_data['grant_id'].append(row['grant_id'])
        result_data['title'].append(row['title'])
        result_data['review_level'].append(score)
        result_data['website'].append(row['website'])
        result_data['github_project_url'].append(row['github_project_url'])
        result_data['twitter_handle_1'].append(row['twitter_handle_1'])
        result_data['twitter_handle_2'].append(row['twitter_handle_2'])
        result_data['comments'].append(''.join(comments))

        filename_noext = os.path.splitext(json_app_file)[0]
        project_rating = pd.DataFrame(result_data)
        project_rating.sort_values(by='review_level', ascending=False).to_csv('{0}_analysis.csv'.format(filename_noext), index=False)

grant_analysis("gr15_grants.json")
