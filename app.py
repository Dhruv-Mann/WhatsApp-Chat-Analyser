import streamlit as st
import preprocessor

# Set page title
st.set_page_config(page_title="WhatsApp Analyzer")

st.sidebar.title("WhatsApp Chat Analyzer")

# 1. File Uploader
uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    # Read the file as a byte stream and decode to string
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")

    # 2. Call our Preprocessor logic
    df = preprocessor.preprocess(data)

    # 3. Sidebar stats (The "At a Glance" view)
    st.title("Top Statistics")
    
    # Let's count basic things to show on the screen
    num_messages = df.shape[0] # Total rows = Total messages
    # We use 'words' by splitting the message strings
    words = []
    for message in df['message']:
        words.extend(message.split())
    
    # Display stats in 2 columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Total Messages")
        st.title(num_messages)
    with col2:
        st.header("Total Words")
        st.title(len(words))

    # 4. Display the Dataframe (to verify it works)
    st.dataframe(df)

    # 5. Finding the busiest users (The Activity Map)
    st.title("Most Busy Users")
    
    # Get the top 5 users
    top_users = df['user'].value_counts().head()
    
    import matplotlib.pyplot as plt

    # Create the figure (the canvas) and the axes (the chart)
    fig, ax = plt.subplots()
    
    # Create a bar chart
    ax.bar(top_users.index, top_users.values, color='#25D366') # WhatsApp Green!
    
    # Rotate labels so they don't overlap
    plt.xticks(rotation='vertical')

    # Display the plot in Streamlit
    st.pyplot(fig)