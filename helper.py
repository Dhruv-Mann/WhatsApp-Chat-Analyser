# This is the library to find URLs in messages
from urlextract import URLExtract

# This is the library to create word cloud visualizations
from wordcloud import WordCloud

# For data manipulation
import pandas as pd

# This is the tool to count frequencies of items
from collections import Counter

# This is the library to detect and work with emojis
import emoji

# Created the URLExtract object once at the top for efficiency , and it will be used later
# to find links in messages
extract = URLExtract()

# Basically this is a feature and once the user selects one of these options-
# [Overall / username 1 / username 2] on the app, only then the rest of the calculation
# block runs. 
def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
 
    # If filtered to let's say Alice, it counts Alice's messages,
    # if selected overall, it counts everyone's messages.
    num_messages = df.shape[0]


    # Create an empty list called words.
    words = []

    # Now loop through every message in the 'message' column, and split it into words.
    # Save these words in 'words' list.
    for message in df['message']:
        words.extend(message.split())


    # This counts how many messages say "Media omitted\n" - WhatsApp's placeholder for media
    num_media_messages = df[df['message'] == 'Media omitted\n'].shape[0]


    # Create a new list called 'links'
    links = []

    # Loop through each message, and find all the urls with the help of the URLExtract tool
    # Save these in 'links'. 
    for message in df['message']:
        links.extend(extract.find_urls(message))
    
    # Return all the results- (returns 4 numbers)
    # 1. Total messages
    # 2. Total words
    # 3. Media count
    # 4. Links count
    return num_messages, len(words), num_media_messages, len(links)


# This is the feature to calculate the most busy user in the chat.
# Basically this entire block will check who messaged the most and what percentage of total
# messages they sent
def most_busy_users(df):

    # value_counts() - this counts how many messages each user sent
    # head() - this gets the top 5 users
    # Result - A list showing Alice: 150 messages , Bob: 120 , etc.
    # Store in variable x
    x = df['user'].value_counts().head()
    
    # This is percentage calculation
    # df['user'].value_counts() --- Message count per user
    # / df.shape[0] --- Divide by total messages (to get the ratio)
    # * 100 --- To convert to percentage
    # , 2) --- Round to 2 decimal places(e.g., 45.23%)
    # .reset_index() --- Convert it to a proper table
    # .rename(columns={'index': 'name', 'user': 'percent'}) --- Rename columns to "name" and "percent"
    # Example result:
    #  name	    percent

    #  Alice	45.23
    #  Bob	    32.10
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    
    # Return both the raw counts(x) and the percentage table(df)
    return x, df

# This function creates a word cloud visualization, takes a username and the dataframe
# What this block does-
# Takes all messages , removes media placeholders, converts into strings, combines into one text,
# and generates a visual word cloud where popular words are bigger
def create_wordcloud(selected_user, df):

    # Filter by the selected user
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # Here we remove all media messages (because WordCloud can't visualize "Media Omitted")
    # and create a copy(.copy()) so we don't mess with the original dataframe(df)
    temp_df = df[df['message'] != 'Media omitted\n'].copy()

    # Convert all messages to text format(handles any weird data like NaN)
    # .astype(str) --- Ensures everything is a string before processing
    temp_df['message'] = temp_df['message'].astype(str)

    # Create a WordCloud with these settings:
    # Size: 500x500 pixels
    # Min font size: 10(smallest words)
    # Background: white
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    
    # .str.cat(sep=" ") --- Combines all messages into ONE giant string with spaces 
    # between them. Example: "hello world this is fun great chat"
    # .generate() -- Create the word cloud(bigger words = more frequent)
    df_wc = wc.generate(temp_df['message'].str.cat(sep=" "))

    # Returns the word cloud image to app.py for display
    return df_wc

# Define a function to find the most common emojis
def most_common_emoji(selected_user, df):

    # Filter by selected user
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # Creates an empty list called 'emojis'
    emojis = []

    # Loop through each message, extract every character that is an emoji(using the official emoji dataset)
    # Store all the emojis in list
    # Example: ['😂', '😂', '❤️', '😂', '😍']
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])


    # Counter(emojis) --- This counts the frequency of each emoji
    # .most_common() --- Rank by frequency(most used first)
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    # Rename the columns to human - readable names: "Emoji" and "Count"
    emoji_df = emoji_df.rename(columns={0: 'Emoji', 1: 'Count'}) 
    

    # Returns the ranked emoji table to app.py
    return emoji_df

# This is a function to compute the message counts per month(month-wise timeline)
def monthly_timeline(selected_user, df):

    # Filter by selected user
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # Group the messages by year + month and counts how many messages are in each group
    # turns the result back to clean table
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
     
    # Creating a list called time
    # Example: "January-2024", "February-2024".
    # These labels are easier to show on charts.
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    
    # Adds the time list as a new column in the timeline dataframe
    # Now the dataframe has a clean x-axis label for plotting
    timeline['time'] = time

    # Returns the final monthly timeline to app.py
    return timeline


# Function defined to compute message counts per day
def daily_timeline(selected_user, df):

    # Filter by selected user
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Groups by only_date (date without time).
    # Counts how many messages happened each day.
    # .reset_index() --- converts the grouped result into a clean dataframe
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    #return the daily timeline to app.py
    return daily_timeline

# Function defined to compute message activity by day of the week
def week_activity_map(selected_user, df):

    #Filter by selected user
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # ['day_name'] --- this is a column like - Monday, Tuesday, Wednesday etc.
    # .value_counts() --- counts how many messages happened on each day
    # returns a series like -- Monday: 120, Tuesday: 95, etc.
    return df['day_name'].value_counts()

# Function defined to compute message activity by month name
def month_activity_map(selected_user, df):

    # Filter by selected user
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    
    # month column contains names like January, February, etc
    # .value_counts() --- counts messages per month.
    # returns a series like: January: 320, February: 210, etc
    return df['month'].value_counts()