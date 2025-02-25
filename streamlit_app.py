import streamlit as st
import pandas as pd
import plotly.express as px  # For interactive charts
from fetch_news import *



st.title("News Sentiment Analysis Dashboard")
st.write("Explore sentiment analysis of pre-fetched news articles.")

# Sample DataFrame (replace this with your actual pre-fetched df)
# Assuming df comes from your earlier NYT fetch + sentiment analysis
sample_data = {
    "Title": ["Tech Stocks Surge", "Fed Raises Rates", "Crypto Falls", "AI Boom Continues", "Market Dips"],
    "Abstract": ["AI drives gains", "Higher costs expected", "Market dips", "Tech advances", "Economic slowdown"],
    "URL": ["nytimes.com/1", "nytimes.com/2", "nytimes.com/3", "nytimes.com/4", "nytimes.com/5"],
    "Author": ["Jane Doe", "John Smith", "Bob Clark", "Alice Lee", "Eve Brown"],
    "Published Date": ["2025-02-24", "2025-02-23", "2025-02-22", "2025-02-21", "2025-02-20"],
    "sentiment": [0.3182, 0.0000, -0.5106, 0.4404, -0.2732]
}
df = pd.DataFrame(sample_data)  # Replace this line with your actual df

# Sidebar for filters
st.sidebar.header("Filters")
sentiment_range = st.sidebar.slider(
    "Sentiment Range", min_value=-1.0, max_value=1.0, value=(-1.0, 1.0), step=0.1
)
filtered_df = df[(df["sentiment"] >= sentiment_range[0]) & (df["sentiment"] <= sentiment_range[1])]

# Main content
st.subheader("News Articles")
st.write(f"Showing {len(filtered_df)} articles")
st.dataframe(filtered_df[["Title", "Abstract", "sentiment", "URL", "Author", "Published Date"]])

# Average Sentiment
avg_sentiment = calculate_average_sentiment(filtered_df)
if avg_sentiment is not None:
    st.subheader("Average Sentiment Score")
    sentiment_label = "Positive" if avg_sentiment > 0 else "Negative" if avg_sentiment < 0 else "Neutral"
    st.metric(label="Average Sentiment", value=f"{avg_sentiment:.4f}", delta=sentiment_label)

# Sentiment Distribution (Bar Chart with Plotly)
st.subheader("Sentiment Distribution")
fig = px.histogram(filtered_df, x="sentiment", nbins=20, range_x=[-1, 1],
                    title="Distribution of Sentiment Scores",
                    labels={"sentiment": "Sentiment Score"})
st.plotly_chart(fig)

# Sentiment Breakdown (Pie Chart)
st.subheader("Sentiment Breakdown")
breakdown = pd.cut(filtered_df["sentiment"], bins=[-1, -0.05, 0.05, 1],
                    labels=["Negative", "Neutral", "Positive"])
breakdown_counts = breakdown.value_counts()
fig_pie = px.pie(names=breakdown_counts.index, values=breakdown_counts.values,
                    title="Positive vs Neutral vs Negative")
st.plotly_chart(fig_pie)

# Download Button
csv = filtered_df.to_csv(index=False)
st.download_button(label="Download Filtered Data as CSV", data=csv,
                    file_name="news_sentiment_filtered.csv", mime="text/csv")
