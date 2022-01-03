
# In order to extract data from Github, we are going to leverage the Github REST API v3
# In `config.py` file we need to define the following configuration variables, that are going to be accessed by the current notebook:
# - `GITHUB_USERNAME`
# - `GITHUB_TOKEN`

import json
import requests
from pandas.io.json import json_normalize
from sqlalchemy import create_engine, engine, text, types, MetaData, Table, String
import pandas as pd
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
import numpy as np
from datetime import datetime

#get_ipython().run_line_magic('load_ext', 'autotime')
import config
import os
# function that converts all object columns to strings, in order to store them efficiently into the database
def objects_to_strings(table):
    measurer = np.vectorize(len)
    df_object = table.select_dtypes(include=[object])
    string_columns = dict(zip(df_object, measurer(
        df_object.values.astype(str)).max(axis=0)))
    string_columns = {key: String(length=value) if value > 0 else String(length=1)
                      for key, value in string_columns.items() }
    return string_columns

engine = create_engine(config.SQL_ALCHEMY_STRING)

github_api = "https://api.github.com"
gh_session = requests.Session()
gh_session.auth = (config.GITHUB_USERNAME, config.GITHUB_TOKEN)

def branches_of_repo(repo, owner, api):
    branches = []
    next = True
    i = 1
    while next == True:
        url = api + '/repos/{}/{}/branches?page={}&per_page=100'.format(owner, repo, i)
        branch_pg = gh_session.get(url = url)
        branch_pg_list = [dict(item, **{'repo_name':'{}'.format(repo)}) for item in branch_pg.json()]    
        branch_pg_list = [dict(item, **{'owner':'{}'.format(owner)}) for item in branch_pg_list]
        branches = branches + branch_pg_list
        if 'Link' in branch_pg.headers:
            if 'rel="next"' not in branch_pg.headers['Link']:
                next = False
        i = i + 1
    return branches

branches = json_normalize(branches_of_repo('spark', 'apache', github_api))
branches.to_csv('data/branches.csv')

def commits_of_repo_github(repo, owner, api):
    commits = []
    next = True
    i = 1
    while next == True:
        url = api + '/repos/{}/{}/commits?page={}&per_page=100'.format(owner, repo, i)
        commit_pg = gh_session.get(url = url)
        commit_pg_list = [dict(item, **{'repo_name':'{}'.format(repo)}) for item in commit_pg.json()]    
        commit_pg_list = [dict(item, **{'owner':'{}'.format(owner)}) for item in commit_pg_list]
        commits = commits + commit_pg_list
        if 'Link' in commit_pg.headers:
            if 'rel="next"' not in commit_pg.headers['Link']:
                next = False
        i = i + 1
    return commits

def create_commits_df(repo, owner, api):
    commits_list = commits_of_repo_github(repo, owner, api)
    return json_normalize(commits_list)


commits = create_commits_df('spark', 'apache', github_api)
commits.to_csv('data/commits.csv')


# ## 3. Pull Requests

def pulls_of_repo(repo, owner, api):
    pulls = []
    next = True
    i = 1
    while next == True:
        url = api + '/repos/{}/{}/pulls?page={}&per_page=100'.format(owner, repo, i)
        pull_pg = gh_session.get(url = url)
        pull_pg_list = [dict(item, **{'repo_name':'{}'.format(repo)}) for item in pull_pg.json()]    
        pull_pg_list = [dict(item, **{'owner':'{}'.format(owner)}) for item in pull_pg_list]
        pulls = pulls + pull_pg_list
        if 'Link' in pull_pg.headers:
            if 'rel="next"' not in pull_pg.headers['Link']:
                next = False
        i = i + 1
    return pulls

pulls = json_normalize(pulls_of_repo('spark', 'apache', github_api))
pulls.to_csv('data/pulls.csv')

# ## 4. Issues

def issues_of_repo(repo, owner, api):
    issues = []
    next = True
    i = 1
    while next == True:
        url = api + '/repos/{}/{}/issues?page={}&per_page=100'.format(owner, repo, i)
        issue_pg = gh_session.get(url = url)
        issue_pg_list = [dict(item, **{'repo_name':'{}'.format(repo)}) for item in issue_pg.json()]    
        issue_pg_list = [dict(item, **{'owner':'{}'.format(owner)}) for item in issue_pg_list]
        issues = issues + issue_pg_list
        if 'Link' in issue_pg.headers:
            if 'rel="next"' not in issue_pg.headers['Link']:
                next = False
        i = i + 1
    return issues

issues = json_normalize(issues_of_repo('spark', 'apache', github_api))
issues.to_csv('data/issues.csv')


# ## Generating All Repo Data
# The following function is used for generating all the previously disscussed data in a single operation.

def generate_repo_data(repo, owner, api):
    branches = json_normalize(branches_of_repo(repo, owner, api))
    commits = create_commits_df(repo, owner, api)
    pulls = json_normalize(pulls_of_repo(repo, owner, api))
    issues = json_normalize(issues_of_repo(repo, owner, api))
    branches.to_csv('data/branches.csv')
    commits.to_csv('data/commits.csv')
    pulls.to_csv('data/pulls.csv')
    issues.to_csv('data/issues.csv')

generate_repo_data('spark', 'apache', github_api)

# ## Contribution Statistics

def statistics_of_repo(repo, owner, api):
    contributors = []
    next = True
    i = 1
    while next == True:
        url = api + '/repos/{}/{}/stats/contributors?page={}&per_page=100'.format(owner, repo, i)
        contrib_pg = gh_session.get(url = url)
        contrib_pg_list = [dict(item, **{'repo_name':'{}'.format(repo)}) for item in contrib_pg.json()]    
        contrib_pg_list = [dict(item, **{'owner':'{}'.format(owner)}) for item in contrib_pg_list]
        contributors = contributors + contrib_pg_list
        if 'Link' in contrib_pg.headers:
            if 'rel="next"' not in contrib_pg.headers['Link']:
                next = False
        i = i + 1
    return contributors

contribs = statistics_of_repo('spark', 'apache', github_api)

weeks_list = []
for i in (weeks_list):
    for j in i['weeks']:
        j['author'] = i['author']['login']
weeks_list.append(j)
weeks_df = json_normalize(weeks_list)
weeks_df['date'] = pd.to_datetime(weeks_df['w'],unit='s')
weeks_df['week'] = weeks_df['date'].dt.week

weeks_df.to_sql(con=engine, name='contributions',
                 if_exists='replace', dtype=objects_to_strings(weeks_df))