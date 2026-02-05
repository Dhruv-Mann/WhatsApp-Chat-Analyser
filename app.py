import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="WhatsApp Analyzer", layout="wide", page_icon="⚡")

st.markdown("""
    <style>
    .stApp {
        background-color: #08090A;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #E3E3E3;
    }
    h1, h2, h3 {
        color: #F7F8F8;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    div[data-testid="stMetric"] {
        background-color: #121417;
        border: 1px solid #22252B;
        padding: 16px;
        border-radius: 6px;
        color: #E3E3E3;
    }
    div[data-testid="stMetricLabel"] {
        color: #8A8F98;
        font-size: 14px;
    }
    div[data-testid="stMetricValue"] {
        color: #F7F8F8;
        font-size: 24px;
        font-weight: 600;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #0E1013;
        border-right: 1px solid #22252B;
    }
    
    div[data-testid="stMarkdownContainer"] p {
        color: #8A8F98;
    }
    
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.markdown("### Workspace")
st.sidebar.markdown("Analytics Dashboard")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader("Import Export")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    
    df = preprocessor.preprocess(data)

    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Filter View", user_list)

    if st.sidebar.button("Generate Report", type="primary"): 
        st.markdown(f"# Project: {selected_user} Analysis")
        st.markdown(f"**Status:** Active • **File:** `_chat.txt`")
        st.markdown("---")

        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Messages", num_messages, delta="All time")
        c2.metric("Word Count", words)
        c3.metric("Media Files", num_media_messages)
        c4.metric("Links Shared", num_links)
        
        st.markdown("### Activity Timeline")
        col1, col2 = st.columns(2)
        
        def linear_plot_style(ax, fig):
            ax.set_facecolor('#08090A')
            fig.patch.set_facecolor('#08090A')
            ax.tick_params(axis='x', colors='#8A8F98')
            ax.tick_params(axis='y', colors='#8A8F98')
            ax.spines['bottom'].set_color('#22252B')
            ax.spines['left'].set_color('#22252B')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(color='#22252B', linestyle='--', linewidth=0.5)

        with col1:
            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='#5E6AD2', linewidth=2, marker='o')
            ax.fill_between(timeline['time'], timeline['message'], color='#5E6AD2', alpha=0.1)
            linear_plot_style(ax, fig)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='#5E6AD2', linewidth=2, marker='o')
            linear_plot_style(ax, fig)
            plt.xticks(rotation=45)
            st.pyplot(fig)

        st.markdown("### Engagement Patterns")
        c1, c2 = st.columns(2)

        with c1:
            st.caption("Weekly Activity")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='#C5C9D1')
            linear_plot_style(ax, fig)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with c2:
            st.caption("Monthly Activity")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='#5E6AD2')
            linear_plot_style(ax, fig)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.markdown("### Content Analysis")
        c1, c2 = st.columns([2, 1])

        with c1:
            st.caption("Word Frequency")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis("off")
            fig.patch.set_facecolor('#08090A')
            st.pyplot(fig)

        with c2:
            st.caption("Top Emojis")
            emoji_df = helper.most_common_emoji(selected_user, df)
            st.dataframe(emoji_df, use_container_width=True, hide_index=True)