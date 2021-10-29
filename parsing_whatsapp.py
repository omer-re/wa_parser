# source/inspired by: https://www.imrankhan.dev/pages/Exploring%20WhatsApp%20chats%20with%20Python.html
import datetime

from dateutil.parser import parse
import pandas as pd
import re
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

def hr_func(ts):
    return ts.hour

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

chat_file= "mob-ilai.txt"

def parse_file(text_file):
    senders = []; messages = []; dates=[];times = []; timestamps=[]; directions=[];minutes=[];

    word_list=['מעלית','חכו']
    f=open(chat_file,'r',encoding='utf8')
    lines=f.readlines()
    for i,line in enumerate(lines):
        if ('/' in line[:4]) and is_date(line.split('-',1)[0].split(',',1)[0]):
            date=line.split('-',1)[0].split(',',1)[0]
            try:
                time=line.split('-',1)[0].split(',',1)[1]
            except:
                print(line)
            sender_message=line.split('-',1)[1]
            separator=sender_message.find(':')
            if separator==(-1):
                continue
            timestamp= line.split('-',1)[0]
            sender=sender_message[:separator]
            message=sender_message[separator+1:]
            #print('date:|{}|\ttime: |{}|\tsender: {}\t message: {}'.format(date, time.strip(), sender, message))
            #print('line1:{} {}'.format(i,line))
            dates.append(date.strip())
            times.append(time.strip())
            mnt=time.strip().split(':')[1]
            minutes.append((mnt[:-3]))
            if 'AM' in time or time.strip().startswith('0'):
                direction='morning'
            else:
                direction='evening'
            directions.append(direction)
            #print(time, direction)
            senders.append(sender)
            messages.append(message.replace('\n',''))
            timestamps.append(timestamp[:-1])
            #print('{} {}'.format(timestamp[:-1], is_date(timestamp[:-1])))
            #print('date: {}\ttime: {}\tsender: {}\t message: {}'.format(date, time, sender, message))

        else: # it is not a new message but new line of previous message
            #print('line2:{} {}'.format(i,line))
            # print(len(messages))
            # print('old message: {}'.format(line))
            # print('prev message: {}'.format(message))
            new_msg=message+line
            messages[-1]=new_msg
            #print('line3:{} {}'.format(i,messages[-1]))


    df = pd.DataFrame(zip(timestamps, dates, times, minutes,directions, senders, messages), columns=['timestamps', 'date', 'time','minutes','direction','sender', 'message'])
    df['timestamps'] = pd.to_datetime(df.timestamps, format='%m/%d/%y, %I:%M %p')
    df['time'] = pd.to_datetime(df.time, format='%I:%M %p').dt.time
    df['date'] = pd.to_datetime(df.date, format='%m/%d/%y').dt.date
    #df.assign(minutes=pd.to_datetime(df.time, format='%H:%M:%S').dt.minute)
    #df['minutes']=pd.to_datetime(df.time, format='%H:%M:%S').dt.minute
    #df['minutes']=df['timestamps'].apply(hr_func)
    #df.insert(3,'minutes',pd.to_datetime(df.time, format='%H:%M:%S').dt.minute)
    #print(pd.to_datetime(df.time, format='%H:%M:%S').dt.minute)
    # remove events not associated with a sender
    #df = df[df.sender != ''].reset_index(drop=True)

    return df


# get date
# get number
df = parse_file(chat_file)

df.to_csv('chat_history.csv', encoding='utf8')
words = ['מעלית','חכו'] # לחכות, דקה, מתעכב

laters=df[df['message'].str.contains('לחכות|דקה|חכו|מעלית')]
#laters2=df[(df['message'].str.contains('לחכות|דקה|חכו|מעלית'))] & df[((df['minutes']<(10)) or (df['minutes']>(50)))]
print(len(df[df['message'].str.contains('חכו|מעלית')]))
pd.set_option("display.max_rows", None, "display.max_columns", 7)
laters.to_csv('laters.csv', encoding='utf8')
#laters.to_csv('laters2.csv', encoding='utf8')

print(laters['sender'].value_counts())
df['dt'] = pd.to_datetime(laters['timestamps'])

tal=df.groupby(['sender', 'direction'])['message'].agg('count')
tal.plot.bar()
