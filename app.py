import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# --------------------------------------------------------------------------------
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide", page_icon="📊")

# Custom CSS to make the UI look professional (Dark Mode friendly)
st.markdown("""
    <style>
    /* Global Font */
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Metrics Cards Styling */
    div.css-1r6slb0.e1tzin5v2 {
        background-color: #0E1117;
        border: 1px solid #31333F;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00CC66; /* WhatsApp Green */
        font-weight: 700;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #171B26;
        border-right: 1px solid #31333F;
    }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------
# 2. SIDEBAR
# --------------------------------------------------------------------------------
st.sidebar.title("Analyze Your Chat 🚀")
st.sidebar.markdown("Upload your WhatsApp chat export (`.txt`) to get started.")

uploaded_file = st.sidebar.file_uploader("Choose a file")

# --------------------------------------------------------------------------------
# 3. MAIN DASHBOARD LOGIC
# --------------------------------------------------------------------------------
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    
    # Preprocessing
    df = preprocessor.preprocess(data)

    # User Selection Logic
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        # --- TOP METRICS SECTION ---
        st.title("Top Statistics")
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        
        # Use columns for a "Card" layout
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Messages", num_messages)
        with col2:
            st.metric("Total Words", words)
        with col3:
            st.metric("Media Shared", num_media_messages)
        with col4:
            st.metric("Links Shared", num_links)
            
        st.markdown("---") # Horizontal Line Separator

        # --- TIMELINE SECTION ---
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots()
            # Making the chart stylish
            ax.plot(timeline['time'], timeline['message'], color='#00CC66', linewidth=3)
            ax.set_facecolor('#0E1117') # Dark background for chart
            fig.patch.set_facecolor('#0E1117')
            ax.tick_params(axis='x', colors='white', rotation=90)
            ax.tick_params(axis='y', colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            st.pyplot(fig)

        with col2:
            st.subheader("Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='#ADFF2F', linewidth=3)
            ax.set_facecolor('#0E1117')
            fig.patch.set_facecolor('#0E1117')
            ax.tick_params(axis='x', colors='white', rotation=45)
            ax.tick_params(axis='y', colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            st.pyplot(fig)

        # --- ACTIVITY MAP SECTION ---
        st.markdown("---")
        st.title("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Busiest Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='#9932CC')
            ax.set_facecolor('#0E1117')
            fig.patch.set_facecolor('#0E1117')
            ax.tick_params(axis='x', colors='white', rotation=45)
            ax.tick_params(axis='y', colors='white')
            st.pyplot(fig)

        with col2:
            st.subheader("Busiest Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='#FF8C00')
            ax.set_facecolor('#0E1117')
            fig.patch.set_facecolor('#0E1117')
            ax.tick_params(axis='x', colors='white', rotation=45)
            ax.tick_params(axis='y', colors='white')
            st.pyplot(fig)

        # --- WORD CLOUD SECTION ---
        st.markdown("---")
        st.title("Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis("off")
        # Ensure the plot background matches the theme
        fig.patch.set_facecolor('#0E1117')
        st.pyplot(fig)

        # --- EMOJI & USERS SECTION ---
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Emoji Analysis")
            emoji_df = helper.most_common_emoji(selected_user, df)
            st.dataframe(emoji_df)

        with col2:
            # Only show "Most Busy Users" if Overall is selected
            if selected_user == 'Overall':
                st.subheader("Most Busy Users")
                x, new_df = helper.most_busy_users(df)
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values, color='#FF6347')
                ax.set_facecolor('#0E1117')
                fig.patch.set_facecolor('#0E1117')
                ax.tick_params(axis='x', colors='white', rotation=45)
                ax.tick_params(axis='y', colors='white')
                st.pyplot(fig)