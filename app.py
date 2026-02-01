"""Streamlit dashboard for WhatsApp chat analytics.

Why this structure:
- Streamlit provides fast iteration for data apps without a separate frontend stack.
- Preprocessing and analytics are separated into modules for clarity and reusability.
"""

import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------------------------------------------------------------
# 1. LINEAR THEME CONFIGURATION
# --------------------------------------------------------------------------------
# Page config must be set first in Streamlit to avoid runtime warnings.
st.set_page_config(page_title="WhatsApp Analyzer", layout="wide", page_icon="⚡")

# The "Linear" Design System (CSS Injection)
# Why: Streamlit's default theme is neutral; custom CSS aligns the UI with a modern product look.
st.markdown("""
    <style>
    /* 1. MAIN BACKGROUND: The 'Linear' Void Black */
    .stApp {
        background-color: #08090A;
    }
    
    /* 2. TYPOGRAPHY: Clean, Sans-Serif, High Contrast */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #E3E3E3;
    }
    h1, h2, h3 {
        color: #F7F8F8;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    /* 3. METRIC CARDS: Flat, Bordered, No Shadow */
    div[data-testid="stMetric"] {
        background-color: #121417;
        border: 1px solid #22252B;
        padding: 16px;
        border-radius: 6px; /* Linear uses slightly tighter radius */
        color: #E3E3E3;
    }
    div[data-testid="stMetricLabel"] {
        color: #8A8F98; /* Muted text for labels */
        font-size: 14px;
    }
    div[data-testid="stMetricValue"] {
        color: #F7F8F8;
        font-size: 24px;
        font-weight: 600;
    }
    
    /* 4. SIDEBAR: Slightly Lighter Dark */
    section[data-testid="stSidebar"] {
        background-color: #0E1013;
        border-right: 1px solid #22252B;
    }
    
    /* 5. PLOTS: Transparent backgrounds to blend in */
    div[data-testid="stMarkdownContainer"] p {
        color: #8A8F98;
    }
    
    /* Remove default top padding */
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------
# 2. SIDEBAR
# --------------------------------------------------------------------------------
# Sidebar establishes a clear entry point for input and keeps controls persistent.
st.sidebar.markdown("### Workspace")
st.sidebar.markdown("Analytics Dashboard")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader("Import Export")

# --------------------------------------------------------------------------------
# 3. DASHBOARD LOGIC
# --------------------------------------------------------------------------------
# Guard clause prevents running analytics without data and avoids empty-state errors.
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    
    # Preprocess raw text into a structured DataFrame for consistent downstream analysis.
    df = preprocessor.preprocess(data)

    # Filter Logic
    # Why: Group notifications are system events, not users; remove to keep stats meaningful.
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Filter View", user_list)

    # Button gate keeps heavier computation from running on every UI change.
    if st.sidebar.button("Generate Report", type="primary"): 
        # type="primary" gives it that nice button highlight
        
        # --- HEADER ---
        st.markdown(f"# Project: {selected_user} Analysis")
        st.markdown(f"**Status:** Active • **File:** `_chat.txt`")
        st.markdown("---")

        # --- KEY METRICS (The Linear Cards) ---
        # Why top-line metrics: Gives an immediate summary before deep dives.
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Messages", num_messages, delta="All time")
        c2.metric("Word Count", words)
        c3.metric("Media Files", num_media_messages)
        c4.metric("Links Shared", num_links)
        
        # --- TIMELINE (The "Glow" Charts) ---
        # Why dual timelines: Monthly trends show macro patterns; daily captures bursts.
        st.markdown("### Activity Timeline")
        col1, col2 = st.columns(2)
        
        # Helper function to style plots like Linear
        # Why: Consistent styling keeps charts readable against a dark UI.
        def linear_plot_style(ax, fig):
            ax.set_facecolor('#08090A') # Match main background
            fig.patch.set_facecolor('#08090A')
            ax.tick_params(axis='x', colors='#8A8F98')
            ax.tick_params(axis='y', colors='#8A8F98')
            ax.spines['bottom'].set_color('#22252B')
            ax.spines['left'].set_color('#22252B')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(color='#22252B', linestyle='--', linewidth=0.5) # Subtle grid

        with col1:
            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots()
            # Linear Purple/Blue Gradient feel using a specific hex
            ax.plot(timeline['time'], timeline['message'], color='#5E6AD2', linewidth=2, marker='o')
            ax.fill_between(timeline['time'], timeline['message'], color='#5E6AD2', alpha=0.1) # Subtle glow under line
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

        # --- ACTIVITY HEATMAP ---
        # Why: Day/month aggregates highlight behavioral rhythms at a glance.
        st.markdown("### Engagement Patterns")
        c1, c2 = st.columns(2)

        with c1:
            st.caption("Weekly Activity")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='#C5C9D1') # Muted white bars
            linear_plot_style(ax, fig)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with c2:
            st.caption("Monthly Activity")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='#5E6AD2') # Accent color bars
            linear_plot_style(ax, fig)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # --- VIBE CHECK ---
        # Why: Qualitative signals (words/emojis) add context beyond message counts.
        st.markdown("### Content Analysis")
        c1, c2 = st.columns([2, 1]) # Make WordCloud wider

        with c1:
            st.caption("Word Frequency")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis("off")
            fig.patch.set_facecolor('#08090A') # Seamless blend
            st.pyplot(fig)

        with c2:
            st.caption("Top Emojis")
            emoji_df = helper.most_common_emoji(selected_user, df)
            st.dataframe(emoji_df, use_container_width=True, hide_index=True)