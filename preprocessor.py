# First we imported regex(regular expression)-
# Basically it is used to define search patterns to efficiently search, analyze,
# extract, or validate text which follows a specific format.
# Here in this code we used it for the timing, date and sender format to separate
# the actual text and the text sending information.
import re

# We imported pandas for data manipulation, cleaning and analysis like
# making tables for messages and dates etc

import pandas as pd

def preprocess(data):

    # This right here is the pattern we are looking for. we got it from
    # the actual pattern which we saw in the exported chats of whatsapp
    # "\d" looks for a digit code between 0-9
    # "{2}" looks for exactly two of them(them-d)
    # "/" is the forward slash literally
    # ","   ,   "\s" -  a comma(literally) and a space
    # "\d{1,2}" for hours because time can be both 1 digit and 2 digits
    # ":" is a colon literally
    # "\d{2}" is for minutes(always two digits)
    # "\s" - space
    # "[ap]m" looks for either 'a' or 'p' followed by a 'm'
    # "\s-\s" - space, hyphen, space
    pattern = r'\d{2}/\d{2}/\d{2},\s\d{1,2}:\d{2}\s[ap]m\s-\s'

    # This line splits the data with the help of pattern we just created and save it
    # in messages. [1:] basically skips the empty chunk before the time stamp
    messages = re.split(pattern , data)[1:]

    # This means find all the data which matches the pattern and save it into
    # dates.
    dates = re.findall(pattern , data)

    # Here with the help of Pandas we create two columns in tabular form
    # where user_message(column -1) has all the texts and message_date(column -2)
    # has all the dates.
    df = pd.DataFrame({'user_message': messages , 'message_date': dates})

    # These lines tell the Pandas to convert the message_date string
    # into actual datetime objects. We achieve this by giving the format to it.
    df['message_date'] = pd.to_datetime(df['message_date'] , format= '%d/%m/%y, %I:%M %p - ')

    # Here we are extracting the components from datetime-

    # 1. extracting the year as in- 2024
    df['year'] = df['message_date'].dt.year

    # 2. extracting month num as in 12 for sorting 
    df['month_num'] = df['message_date'].dt.month

    # 3. extracting the month name
    df['month'] = df['message_date'].dt.month_name()

    # 4. extracting the day as in 25
    df['day'] = df['message_date'].dt.day

    # 5. extracting the day name as in Sunday for weekly patterns
    df['day_name'] = df['message_date'].dt.day_name()

    # 6. this removes the time part from the date part
    df['only_date'] = df['message_date'].dt.date

    # 7. extracting the hours as in 3
    df['hour'] = df['message_date'].dt.hour

    # 8. extracting the minutes as in 45
    df['minute'] = df['message_date'].dt.minute


    # creating an empty list to store the extracted usernames
    users = []

    # creating an empty list to store the cleaned messages text
    cleaned_messages = []

    # loop through the entire column of user_message(where all the texts with the username are)
    # Each message looks like: "Alice: Hey how are you?"
    for message in df['user_message']:

        # now here, we split the username and the message - How?---
        # look for the colon. everything after the colon is the text!
        # Result- Result: ["", "Alice", " Hey how are you?"]
        # Index [0] = empty (before colon)
        # Index [1] = username ("Alice")
        # Index [2] = message text (" Hey how are you?")
        entry = re.split('([\w\W]+?):\s' , message)

        # this is to check if the split worked- if there is anything after the index 1:
        # if yes- then it is a regular user message
        # if not- then it is a system notification(no colon found)
        if entry[1:]:

            # Add Alice(the username) in the users list 
            # [1] because the usernames are saved at index 1
            users.append(entry[1])

            # Add message text to the cleaned_messages list
            # [2] because the texts are saved at index 2
            cleaned_messages.append(entry[2])

        # if there is no colon     
        else:

            # add the "group notification" as the user and save it in the users column itself
            users.append('group_notification')
            
            # add the whole thing as a message as split didnt occur
            cleaned_messages.append(entry[0])
    
    # now add the extracted usernames and cleaned messages list as new columns in the data frame
    df['user'] = users
    df['message'] = cleaned_messages

    # Delete the older user message column as we have extracted what we needed
    df.drop(columns=['user_message'], inplace=True)
    

    # return this entire structured dataframe to "app.py"
    return df

        
    


