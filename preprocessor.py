import re
import pandas as pd

def preprocess(data):
    pattern = r'\d{2}/\d{2}/\d{2},\s\d{1,2}:\d{2}\s[ap]m\s-\s'

    messages = re.split(pattern , data)[1:]
    dates = re.findall(pattern , data)

    df = pd.DataFrame({'user_message': messages , 'message_date': dates})

    df['message_date'] = pd.to_datetime(df['message_date'] , format= '%d/%m/%y, %I:%M %p - ')


    df['year'] = df['message_date'].dt.year
    df['month_num'] = df['message_date'].dt.month  # <--- NEW: For sorting (1, 2, 3...)
    df['month'] = df['message_date'].dt.month_name()
    df['day'] = df['message_date'].dt.day
    df['day_name'] = df['message_date'].dt.day_name() # <--- NEW: For "Busy Days" later (Mon, Tue...)
    df['only_date'] = df['message_date'].dt.date
    df['hour'] = df['message_date'].dt.hour
    df['minute'] = df['message_date'].dt.minute

    users = []
    cleaned_messages = []


    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s' , message)
        if entry[1:]:
            users.append(entry[1])
            cleaned_messages.append(entry[2])
        else:
            users.append('group_notification')
            cleaned_messages.append(entry[0])
    df['user'] = users
    df['message'] = cleaned_messages
    df.drop(columns=['user_message'], inplace=True)
    
    return df

# --- TEST AREA ---
if __name__ == "__main__":
    try:
        with open('_chat.txt', 'r', encoding='utf-8') as f:
            data = f.read()
        
        df = preprocess(data)
        
        print(f"Total Messages: {df.shape[0]}")
        print("\n--- Sample Data ---")
        print(df[['user', 'message']].head())
        
    except FileNotFoundError:
        print("Error: _chat.txt not found.")
        
    


