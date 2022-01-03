import re
from datetime import datetime

import numpy as np
import pandas as pd
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', -1)
from pandas.io.json import json_normalize
import json
import ast

#get_ipython().run_line_magic('load_ext', 'autotime')

import plotly
import chart_studio.plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)

commits = pd.read_csv('data/commits.csv', parse_dates=True)
commits.info()


# ## Data Preprocessing
commits['date'] =  pd.to_datetime(commits['commit.committer.date'])
commits['date'] =  pd.to_datetime(commits['date'], utc=True)
commits['commit_date'] = commits['date'].dt.date
commits['commit_week'] = commits['date'].dt.week
commits['commit_hour'] = commits['date'].dt.hour
commits['commit_month'] = commits['date'].dt.month
commits['commit_year'] = commits['date'].dt.year
# drop unnecessary columns
commits = commits[['sha', 'author.login', 'commit_date', 'commit_hour', 'commit_month', 'commit_year']]
commits.head()
# ## Data Analysis
## number of contributors
commits['author.login'].unique().size
commits_by_hour = commits.groupby('commit_hour')[['sha']].count()
commits_by_hour = commits_by_hour.rename(columns = {'sha': 'commit_count'})

fig = go.Figure([go.Bar(
    x=commits_by_hour.index, 
    y=commits_by_hour.commit_count, 
    text=commits_by_hour.commit_count, 
    textposition='auto')])
fig.update_layout(
    title = 'Commits by Hour', 
    xaxis_title = 'Hour', 
    yaxis_title = 'Commits Count', 
    xaxis_tickmode = 'linear')
fig.show()

commits_by_day = commits.groupby('commit_date')[['sha']].count()
commits_by_day = commits_by_day.rename(columns = {'sha': 'commit_count'})

fig = go.Figure([go.Scatter(
    x=commits_by_day.index, 
    y=commits_by_day.commit_count, 
    text=commits_by_day.commit_count, 
    fill='user')])
fig.update_layout(
    title = 'Commits by Date', 
    xaxis_title = 'Date', 
    yaxis_title = 'Commits Count')
fig.show()

commits_by_author = commits.groupby('author.login')[['sha']].count()
commits_by_author = commits_by_author.rename(columns = {'sha': 'commit_count'})
commits_by_author = commits_by_author.sort_values(by='commit_count', ascending=False)
top_authors = commits_by_author.head(30)


fig = go.Figure([go.Bar(
    x=top_authors.index, 
    y=top_authors.commit_count)])
fig.update_layout(
    title = 'Top Committers', 
    xaxis_title = 'Author', 
    yaxis_title = 'Commits Count', 
    xaxis_tickmode = 'linear',
    xaxis_tickangle=-40)
fig.show()


# ## Open Pull Requests
pulls = pd.read_csv('data/pulls.csv', parse_dates=True)
pulls.info()
pulls['date'] = pd.to_datetime(pulls['created_at'])
pulls['date'] = pd.to_datetime(pulls['date'], utc=True)
pulls['pull_date'] = pulls['date'].dt.date
pulls_by_date = pulls.groupby('pull_date')[['id']].count()
pulls_by_date = pulls_by_date.rename(columns = {'id': 'commit_count'})

fig = go.Figure([go.Scatter(
    x=pulls_by_date.index, 
    y=pulls_by_date.commit_count, 
    text=pulls_by_date.commit_count)])
fig.update_layout(
    title = 'Open Pull Requests by Date', 
    xaxis_title = 'Date', 
    yaxis_title = 'Pulls Count')
fig.show()


# ### Pull Request Labels

# **NOTES**:  
# - ast.literal_eval converts string to list.
# - The following two lines convert a Pandas column that contains list of dictionaries into a Pandas Dataframe where each dictionary corresponds to a dataframe row.

labels_list = [ast.literal_eval(i) for i in pulls['labels'].tolist() if i != '[]']
labels = [j for i in labels_list for j in i]

labels_df = pd.DataFrame(labels)

labels_by_name = labels_df.groupby('name')[['id']].count()
labels_by_name = labels_by_name.rename(columns = {'id': 'label_count'})
labels_by_name = labels_by_name.sort_values(by=['label_count'], ascending=False)

fig = go.Figure([go.Bar(
    x=labels_by_name.index, 
    y=labels_by_name.label_count)])
fig.update_layout(
    title = 'Pull Requests by Label', 
    xaxis_title = 'Labels', 
    yaxis_title = 'PR Count', 
    xaxis_tickmode = 'linear',
    xaxis_tickangle=-40)
fig.show()