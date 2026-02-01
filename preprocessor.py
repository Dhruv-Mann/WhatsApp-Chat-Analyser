"""WhatsApp Chat Data Preprocessing Module

This module transforms raw WhatsApp chat exports into structured DataFrames suitable for analysis.
The preprocessing pipeline handles:
1. Regex-based message parsing from unstructured text
2. Datetime extraction and normalization
3. User identification and message separation
4. Temporal feature engineering (year, month, day, hour extraction)

Challenges addressed:
- WhatsApp export format varies slightly by region (date format, time format)
- Group notifications must be separated from user messages
- Multi-line messages need to be associated with correct timestamps

Design rationale: Using regex patterns provides flexibility to handle format variations
without hardcoding specific positions or delimiters.
"""

import re
import pandas as pd

def preprocess(data):
    """Parse raw WhatsApp chat text into structured DataFrame.
    
    Args:
        data: Raw string content from WhatsApp .txt export
    
    Returns:
        DataFrame with columns: user, message, message_date, and temporal features
    
    Why regex pattern: WhatsApp's timestamp format is consistent but needs pattern matching
    to handle variable message lengths and multi-line content.
    """
    # Regex pattern breakdown: \d{2}/\d{2}/\d{2} (date), \d{1,2}:\d{2} (time), [ap]m (AM/PM)
    # Why this pattern: Matches WhatsApp's export format while being flexible about spacing
    pattern = r'\d{2}/\d{2}/\d{2},\s\d{1,2}:\d{2}\s[ap]m\s-\s'

    # Split on timestamps to extract message content; [1:] skips empty first element
    messages = re.split(pattern , data)[1:]
    # Find all timestamps to pair with messages
    dates = re.findall(pattern , data)

    # Parallel arrays converted to DataFrame for structured processing
    df = pd.DataFrame({'user_message': messages , 'message_date': dates})

    # Convert string timestamps to datetime objects for temporal operations
    # Why pd.to_datetime: Enables date arithmetic and extract operations
    df['message_date'] = pd.to_datetime(df['message_date'] , format= '%d/%m/%y, %I:%M %p - ')


    # Feature engineering: Extract temporal components for multi-dimensional analysis
    # Why both month_num and month: Numeric for sorting, name for display readability
    df['year'] = df['message_date'].dt.year
    df['month_num'] = df['message_date'].dt.month  # Integer (1-12) for chronological ordering
    df['month'] = df['message_date'].dt.month_name()  # String ("January") for visualization
    df['day'] = df['message_date'].dt.day
    df['day_name'] = df['message_date'].dt.day_name()  # "Monday", "Tuesday" for weekly patterns
    df['only_date'] = df['message_date'].dt.date  # Date without time for daily aggregation
    df['hour'] = df['message_date'].dt.hour  # Future-proof: enables hourly activity analysis
    df['minute'] = df['message_date'].dt.minute

    users = []
    cleaned_messages = []

    # Parse username and message content from combined string
    # Format: "Username: message text" vs "System notification text"
    for message in df['user_message']:
        # Regex splits at first colon, separating username from message
        entry = re.split('([\w\W]+?):\s' , message)
        if entry[1:]:  # If split successful (user message format)
            users.append(entry[1])  # Username
            cleaned_messages.append(entry[2])  # Message content
        else:  # No colon found (system notification format)
            # Why 'group_notification': Standardized label for filtering system messages
            users.append('group_notification')
            cleaned_messages.append(entry[0])
    
    df['user'] = users
    df['message'] = cleaned_messages
    df.drop(columns=['user_message'], inplace=True)  # Remove intermediate column
    
    return df

# --- TEST HARNESS ---
# Enables standalone module testing without running full Streamlit app
# Why: Faster development iteration when debugging preprocessing logic
if __name__ == "__main__":
    try:
        with open('_chat.txt', 'r', encoding='utf-8') as f:
            data = f.read()
        
        df = preprocess(data)
        
        # Basic validation output to verify parsing correctness
        print(f"Total Messages: {df.shape[0]}")
        print("\n--- Sample Data ---")
        print(df[['user', 'message']].head())
        
    except FileNotFoundError:
        print("Error: _chat.txt not found.")
        
    


