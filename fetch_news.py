import requests
import pandas as pd
import nltk
import streamlit as st 
from nltk.sentiment.vader import SentimentIntensityAnalyzer

api_key = st.secrets["NYT_API_TOKEN"]

def fetch_nyt_business_news_df(api_key=api_key):
    """
    Fetches top business news stories from the New York Times API and returns them in a pandas DataFrame.
    
    Args:
        api_key (str): Your NYT API key.
    
    Returns:
        pandas.DataFrame: A DataFrame containing news articles, or None if the request fails.
    
    Raises:
        ValueError: If the API key is not provided.
    """
    # Check if API key is provided
    if not api_key:
        raise ValueError("API key is required to fetch news.")

    # Construct the URL
    url = f"https://api.nytimes.com/svc/topstories/v2/business.json?api-key={api_key}"
    
    try:
        # Send GET request to the API
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the JSON response
        data = response.json()
        
        # Extract the 'results' list containing articles
        articles = data.get("results", [])
        
        if not articles:
            print("No articles found in the response.")
            return None
        
        # Create a DataFrame from the articles
        df = pd.DataFrame(articles)
        
        # Select and rename key columns (optional, adjust as needed)
        columns_to_keep = {
            "title": "Title",
            "abstract": "Abstract",
            "url": "URL",
            "byline": "Author",
            "published_date": "Published Date",
            "multimedia": "Multimedia"
        }
        
        # Filter to desired columns if they exist, and rename them
        available_columns = [col for col in columns_to_keep.keys() if col in df.columns]
        df = df[available_columns].rename(columns=columns_to_keep)
        
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return None
    except pd.errors.EmptyDataError:
        print("No data available to create a DataFrame.")
        return None


def calculate_sentiment_score(df_news, text_column="headline"):
    """
    Calculate sentiment scores for text in a DataFrame using NLTK's VADER sentiment analyzer.

    Args:
        df_news (pandas.DataFrame): Input DataFrame containing news data.
        text_column (str, optional): Name of the column with text to analyze. Defaults to "headline".

    Returns:
        pandas.DataFrame: A new DataFrame with an added 'sentiment' column containing compound scores,
                         or None if the operation fails.

    Notes:
        - Requires NLTK's VADER lexicon. Run `nltk.download('vader_lexicon')` once beforehand.
        - Preserves the original DataFrame by working on a copy.
    """
    # Ensure VADER lexicon is available (run this once outside the function ideally)
    try:
        nltk.data.find("sentiment/vader_lexicon")
    except LookupError:
        print("Downloading VADER lexicon for the first time...")
        nltk.download("vader_lexicon")

    # Initialize the sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    # Validate input
    if not isinstance(df_news, pd.DataFrame):
        print("Error: Input must be a pandas DataFrame.")
        return None
    
    if text_column not in df_news.columns:
        print(f"Error: Column '{text_column}' not found in DataFrame.")
        return None
    
    if df_news.empty:
        print("Warning: Input DataFrame is empty.")
        return None

    # Work on a copy to avoid modifying the original DataFrame
    df = df_news.copy()

    # Drop rows where the text column is NaN and convert to string
    df = df.dropna(subset=[text_column])
    df[text_column] = df[text_column].astype(str)

    # Calculate sentiment scores (compound score from VADER)
    df["sentiment"] = df[text_column].apply(lambda x: analyzer.polarity_scores(x)["compound"])

    return df


def calculate_average_sentiment(df, sentiment_column="sentiment"):
    try:
        # Calculate the mean sentiment score, ignoring NaN values
        avg_sentiment = df[sentiment_column].mean()
        return avg_sentiment
    
    except (TypeError, ValueError) as e:
        print(f"Error calculating average sentiment: {e}")
        return None



def get_image_url(multimedia):
    """
    Extract the preferred image URL from the multimedia list.
    Returns None if no suitable image is found.
    """
    if not multimedia or not isinstance(multimedia, list):
        return None
    # Prefer 'threeByTwoSmallAt2X' or fallback to first available URL
    for item in multimedia:
        if "url" in item and item.get("format") == "threeByTwoSmallAt2X":
            return item["url"]
    return multimedia[0].get("url") if multimedia and "url" in multimedia[0] else None