#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import pandas as pd
import numpy as np
import regex as re
import pymongo
from pymongo import MongoClient


# In[15]:


url='https://api.clashofclans.com/v1/clans/%232LC9VR0JC/currentwar/leaguegroup'
token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjFkNWFjNGM5LWNhYWQtNGJhZS05MDIxLTg4NGU1ZmY1MmY2MCIsImlhdCI6MTY4MDcxNzM5Nywic3ViIjoiZGV2ZWxvcGVyL2ZkNTYwNjViLWU0YjctN2YwNC02YTNiLWRlNDFlMWQ0ZTRlNyIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjQ5LjM3LjI1MS44MCIsIjEyMi4xNzEuMjIuMTA1Il0sInR5cGUiOiJjbGllbnQifV19.LB3bNyu-gRo3ZK9LCQ4lPIAkHgfyOzz8pGE-9UiXY6C6jRzW-dTF0o2r_xNCU6HFavZnfjUfO4BAFJOs3KnE4A'

response=requests.get(url,headers={'Accept':'application/json' ,'authorization': 'Bearer ' + token})
cwl=response.json()
cwl


# In[41]:


cwl_df=pd.DataFrame()
cwl_season=cwl['season']
for i in cwl['clans']:
    temp=pd.DataFrame(data=i['members'])
    temp['clantag']=i['tag']
    temp['clanname']=i['name']
    temp['clanlevel']=i['clanLevel']
    temp['clanbadge']=i['badgeUrls']['large']
    temp['clanseason']=cwl_season
    cwl_df=pd.concat([cwl_df,temp])
cwl_df.reset_index(drop=True,inplace=True)
cwl_df.sort_values(by=['clantag','tag'],inplace=True,ignore_index=True)
cwl_df


# In[18]:


war_df=pd.DataFrame()
for x in cwl['rounds']:
    for y in x['warTags']:
        warTag=re.sub('#','',y)
        url2='https://api.clashofclans.com/v1/clanwarleagues/wars/%23'+warTag
        response=requests.get(url2,headers={'Accept':'application/json' ,'authorization': 'Bearer ' + token})
        cwl_war=response.json() 
        if cwl_war['state']=='inWar' or cwl_war['state']=='warEnded':
            for i in ['clan','opponent']:
                for j in cwl_war[i]['members']:
                    try:
                        attacks=pd.DataFrame(data=j['attacks'])
                        attacks['clanTag']=cwl_war[i]['tag']
                        attacks['teamSize']=cwl_war['teamSize']
                        attacks['preparationStartTime']=cwl_war['preparationStartTime']
                        attacks['startTime']=cwl_war['startTime']
                        attacks['endTime']=cwl_war['endTime']
                        attacks['warTag']=warTag
                    except KeyError:
                        attacks=pd.DataFrame()
                    war_df=pd.concat([war_df,attacks])
war_df.reset_index(drop=True,inplace=True)
war_df['preparationStartTime']=pd.to_datetime(war_df['preparationStartTime'])
war_df['startTime']=pd.to_datetime(war_df['startTime'])
war_df['endTime']=pd.to_datetime(war_df['endTime'])
war_df


# In[ ]:


url3='https://api.clashofclans.com/v1/clans/%232LC9VR0JC/warlog'
response=requests.get(url,headers={'Accept':'application/json' ,'authorization': 'Bearer ' + token})
wl=response.json()


# In[22]:


connection_string='mongodb+srv://flash238116:238116flash@activewarriors.1jmpfkt.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(connection_string)


# In[23]:


db=client['cwl']
collection1 = db['seasoninfo']
collection2 = db['warinfo']


# In[42]:


seasoninfo=pd.DataFrame(data=collection1.find())
seasoninfo=seasoninfo.iloc[:,1:]
seasoninfo.sort_values(by=['clantag','tag'],inplace=True,ignore_index=True)
seasoninfo


# In[46]:


warinfo=pd.DataFrame(data=collection2.find())
warinfo=warinfo.iloc[:,1:]
warinfo.sort_values(by=['clanTag','attackerTag'],inplace=True,ignore_index=True)
warinfo


# In[83]:


check1=cwl_df.merge(seasoninfo,how='left',on=['tag','clantag','clanseason'],suffixes=['','_y'])
check1=check1.loc[check1.name_y.isna()][['tag', 'name', 'townHallLevel', 'clantag', 'clanname', 'clanlevel',
       'clanbadge', 'clanseason']]
check1.reset_index(inplace=True,drop=True)


check2=war_df.merge(warinfo,how='left',on=['warTag','attackerTag'],suffixes=['','_y'])
check2=check2.loc[check2.defenderTag_y.isna()][['attackerTag', 'defenderTag', 'stars', 'destructionPercentage', 'order',
       'duration', 'clanTag', 'teamSize', 'preparationStartTime', 'startTime',
       'endTime', 'warTag']]
check2.reset_index(inplace=True,drop=True)


# In[84]:


if check1.empty==False:
    check1=check1.to_dict('records')
    collection1.insert_many(check1)

if check2.empty==False:
    check2=check2.to_dict('records')
    collection2.insert_many(check2)


# In[109]:


war_df


# In[87]:


import sys
get_ipython().system('{sys.executable} -m pip freeze')

