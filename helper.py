from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

def fetch_stats(selected_user, df):
    # If a specific user is selected, filter the data. 
    # If "Overall" is selected, use the whole dataframe.
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # 1. Total Messages
    num_messages = df.shape[0]

    # 2. Total Words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # 3. Media Files (Looking for that specific "Media omitted" phrase)
    num_media_messages = df[df['message'] == 'Media omitted\n'].shape[0]

    # 4. Links (Using the urlextract library)
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    
    # Calculate percentages for a cleaner data table
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    
    return x, df

def create_wordcloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Filter out "Media omitted" so it doesn't dominate the cloud
    temp_df = df[df['message'] != 'Media omitted\n']

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    df_wc = wc.generate(temp_df['message'].str.cat(sep=" "))
    return df_wc

def most_common_emoji(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    # THIS was the missing line:
    emoji_df = emoji_df.rename(columns={0: 'Emoji', 1: 'Count'}) 
    
    return emoji_df

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    
    timeline['time'] = time
    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline

def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()