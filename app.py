
import streamlit as st
import preprocessor
import pandas as pd

st.sidebar.title("WhatsApp Chat Analyzer")

# 1. Create a File Uploader
uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    # To read the file as string, we need to decode the byte stream
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    
    # 2. Process the data using our script
    # This calls the 'preprocess' function we wrote in the other file
    df = preprocessor.preprocess(data)

    # 3. Show the Dataframe
    st.dataframe(df)