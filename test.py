from etherscan import Etherscan
from dotenv import load_dotenv
import pandas as pd
import requests

load_dotenv()

YOUR_API_KEY  = os.getenv('YOUR_API_KEY')

eth = Etherscan(YOUR_API_KEY)

bal = eth.get_eth_balance(address="0xE7048aB8dFA7F7a80d79fD6c5AcF8B0C1d174fdF")

ether_bal = int(bal)/1000000000000000000
#349F3N32D4VNWP6E2XIQ7QH9TE5PR4S9UZ

df = df[:25]

df = pd.read_json("gr15_grants.json").T

for index, row in df.iterrows():
    print(row['grant_id'], row['address']
    , row['twitter_verified'], row['twitter_handle_1']
    , row['twitter_handle_2'])

result_data = {'grant_id' : []
                , 'title' : []
                , 'review_level' : []
                , 'website' : []
                , 'github_project_url' : []
                , 'twitter_handle_1' : []
                , 'twitter_handle_2' : []
                , 'comments': []}

# Check if project has twitter
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

project_rating = pd.DataFrame(result_data)
project_rating.sort_values(by='review_level', ascending=False)

def twitter_validation(row, score, comments):

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
    url = row['website']
    try:    
        website_status = requests.head(url, timeout=2).status_code
    except:
        website_status = 0
    # not including 301 because if redirecting that will need to be checked out
    if (website_status == 200):
        score+=0
        comments.append("Website connection successful. ")
    else:
        score+=2
        comments.append("Website unable to be reached." )

    return comments, score;

def github_validation(row, score, comments):
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


# Compile a review score 
# Higher number means higher need of scrutiny
# Lower number means less red flags 

# Website invalid or non-existent = 2
# No twitter = 2
# one unique twitter = 1
# Unverified twitter = 1 
# github project 404 not found = 1 (1 because could be private)
# github project unknown = 2
