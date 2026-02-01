"""Helper Functions for WhatsApp Chat Analysis

This module contains pure functions that perform statistical calculations and data transformations.
Each function follows a consistent pattern: filter by user (if applicable), then compute metrics.

Design Principles:
- Functions are stateless and side-effect free for predictability
- User filtering logic is replicated across functions to maintain encapsulation
- Returns processed data rather than rendering, maintaining separation of concerns
"""

from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

# Initialize URL extractor once at module level for performance
# Why: Avoid repeated initialization overhead across multiple function calls
extract = URLExtract()

def fetch_stats(selected_user, df):
    """Calculate core engagement metrics for the selected user or entire chat.
    
    Args:
        selected_user: Username string or 'Overall' for aggregate statistics
        df: Preprocessed DataFrame with message data
    
    Returns:
        tuple: (message_count, word_count, media_count, link_count)
    
    Why this matters: These four metrics provide a comprehensive engagement profile,
    balancing quantitative (messages/words) with qualitative (media/links) indicators.
    """
    # Conditional filtering pattern: reusable across all analysis functions
    # Why: Enables both group-wide and individual analysis from the same dataset
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # 1. Message count: Simple row count serves as baseline engagement metric
    num_messages = df.shape[0]

    # 2. Word count: Measures verbosity and conversation depth
    # Why split().extend(): More accurate than character count; handles multi-word messages
    words = []
    for message in df['message']:
        words.extend(message.split())

    # 3. Media detection: WhatsApp exports replace media with this specific placeholder text
    # Why explicit string match: Reliable identifier across all WhatsApp export versions
    num_media_messages = df[df['message'] == 'Media omitted\n'].shape[0]

    # 4. Link extraction: URLExtract library handles various URL formats robustly
    # Why external library: Regex patterns for URLs are complex; this handles edge cases
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    """Identify top contributors in group chats.
    
    Returns both absolute counts and percentage contributions for context.
    Why: Percentage view normalizes for chat size, making comparisons meaningful.
    """
    x = df['user'].value_counts().head()  # Top 5 users by message volume
    
    # Percentage calculation provides relative contribution context
    # Why round to 2 decimals: Balance between precision and readability
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    
    return x, df

def create_wordcloud(selected_user, df):
    """Generate visual word frequency representation.
    
    Why remove 'Media omitted': This phrase appears frequently but provides no
    semantic value. Filtering prevents it from dominating the visualization.
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Data cleaning step: remove noise that would distort word frequency analysis
    temp_df = df[df['message'] != 'Media omitted\n']

    # WordCloud parameters chosen for optimal readability at typical screen resolutions
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    # str.cat() concatenates all messages into single corpus for frequency analysis
    df_wc = wc.generate(temp_df['message'].str.cat(sep=" "))
    return df_wc

def most_common_emoji(selected_user, df):
    """Extract and rank emoji usage patterns.
    
    Why emojis matter: They convey emotional tone and can reveal sentiment patterns
    that raw text analysis might miss.
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Character-level iteration to identify emojis using official emoji dataset
    # Why list comprehension: Efficient filtering of Unicode emoji characters
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    # Counter provides frequency ranking automatically
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    # Descriptive column names improve DataFrame readability for end users
    emoji_df = emoji_df.rename(columns={0: 'Emoji', 1: 'Count'}) 
    
    return emoji_df

def monthly_timeline(selected_user, df):
    """Aggregate messages by month for trend analysis.
    
    Why group by year AND month: Prevents collapsing data from same months in different years.
    The month_num field ensures proper chronological ordering.
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Multi-level grouping maintains temporal hierarchy
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    # Construct human-readable time labels for x-axis
    # Format: "January-2024" provides clear temporal context
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    
    timeline['time'] = time
    return timeline

def daily_timeline(selected_user, df):
    """Create day-by-day message count timeline.
    
    Why daily granularity: Reveals micro-patterns like conversation spikes that
    monthly aggregation would smooth out.
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Group by date (time component stripped) for daily totals
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline

def week_activity_map(selected_user, df):
    """Analyze which days of the week are most active.
    
    Why: Reveals weekly behavioral patterns (e.g., weekday vs weekend activity).
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # value_counts() naturally ranks days by message frequency
    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    """Identify seasonally busy months across all years.
    
    Why aggregate across years: Reveals recurring seasonal patterns
    (e.g., holiday period activity spikes).
    """
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Month name grouping collapses all instances of "January", "February", etc.
    return df['month'].value_counts()