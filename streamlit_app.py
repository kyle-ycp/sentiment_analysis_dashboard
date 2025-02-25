import streamlit as st
import pandas as pd
import plotly.express as px  # For interactive charts
from fetch_news import *

# Set app icon and title
st.set_page_config(page_title="News Sentiment Dashboard", page_icon="📰", 
                   menu_items=
                   {
                        'Get Help': 'https://www.extremelycoolapp.com/help',
                        'Report a bug': "https://www.extremelycoolapp.com/bug",
                        'About': "# This is a header. This is an *extremely* cool app!"
                    }
)


st.title("News Sentiment Dashboard")
st.write("Browse business news from The New York Times with sentiment analysis.")

df = fetch_nyt_business_news_df(st.secrets["NYT_API_TOKEN"])
df = calculate_sentiment_score(df, "Title")


# Filters
st.subheader("Filters")
col1, col2 = st.columns(2)  # Two columns for filters

with col1:
    sentiment_range = st.slider("Sentiment Range", min_value=-1.0, max_value=1.0, value=(-1.0, 1.0), step=0.1)

with col2:
    keyword = st.text_input("Search Keywords in Title", placeholder="e.g., Tech, Crypto").strip().lower()

# Apply filters
if not df.empty:
    filtered_df = df.copy()
else:
    st.error("There is not data from the datasoure.")
    df = pd.DataFrame(columns=['sentiment'])

if keyword:
    filtered_df = filtered_df[filtered_df["Title"].str.lower().str.contains(keyword, na=False)]
filtered_df = filtered_df[(filtered_df["sentiment"] >= sentiment_range[0]) & 
                            (filtered_df["sentiment"] <= sentiment_range[1])].dropna(subset=["sentiment"])



# Sentiment Visualizations
col1, col2 = st.columns(2)

with col1:
    st.subheader("Sentiment Metrics")
    # Average Sentiment
    avg_sentiment = calculate_average_sentiment(filtered_df)
    if avg_sentiment is not None:
        sentiment_label = "Positive" if avg_sentiment > 0 else "Negative" if avg_sentiment < 0 else "Neutral"
        st.metric(label="Average Sentiment", value=f"{avg_sentiment:.4f}", delta=sentiment_label)

    # Positive Sentiment Percentage
    positive_count = len(filtered_df[filtered_df["sentiment"] > 0.05])
    positive_pct = (positive_count / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
    st.metric(label="Positive Articles", value=f"{positive_pct:.1f}%", delta=f"{positive_count} articles")
    
    # Negative Sentiment Percentage
    negative_count = len(filtered_df[filtered_df["sentiment"] < -0.05])
    negative_pct = (negative_count / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
    st.metric(label="Negative Articles", value=f"{negative_pct:.1f}%", delta=f"{negative_count} articles")
    
    # Most Positive Score
    max_sentiment = filtered_df["sentiment"].max()
    st.metric(label="Most Positive Score", value=f"{max_sentiment:.4f}")

with col2:
    st.subheader("Sentiment Breakdown")
    breakdown = pd.cut(filtered_df["sentiment"], bins=[-1, -0.05, 0.05, 1],
                        labels=["Negative", "Neutral", "Positive"])
    breakdown_counts = breakdown.value_counts()
    fig_pie = px.pie(names=breakdown_counts.index, values=breakdown_counts.values)
    st.plotly_chart(fig_pie, use_container_width=True)



# Pagination for News Feed
st.subheader("Latest News")
articles_per_page = 5
total_articles = len(filtered_df)
total_pages = (total_articles + articles_per_page - 1) // articles_per_page  # Ceiling division

if total_articles == 0:
    st.write("No articles match the current filters.")
else:
    # Page selection
    page = st.selectbox("Select Page", range(1, total_pages + 1), key="page_selector")
    start_idx = (page - 1) * articles_per_page
    end_idx = min(start_idx + articles_per_page, total_articles)
    
    st.write(f"Showing articles {start_idx + 1} to {end_idx} of {total_articles}")
    page_df = filtered_df.iloc[start_idx:end_idx]
    
    # Display news feed
    for index, row in page_df.iterrows():
        col1, col2 = st.columns([1, 3])
        image_url = get_image_url(row["Multimedia"])
        if image_url:
            with col1:
                st.image(image_url, width=150, caption="News Image")
        else:
            with col1:
                st.write("No image available")
        with col2:
            st.markdown(f"### [{row['Title']}]({row['URL']})")
            st.write(f"**Abstract**: {row['Abstract']}")
            st.write(f"**Author**: {row['Author']} | **Date**: {row['Published Date']}")
            sentiment_color = "green" if row["sentiment"] > 0 else "red" if row["sentiment"] < 0 else "gray"
            st.markdown(f"**Sentiment**: <span style='color:{sentiment_color}'>{row['sentiment']:.4f}</span>", unsafe_allow_html=True)
        st.markdown("---")



# Download Button
csv = filtered_df.to_csv(index=False)
st.download_button(label="Download Data as CSV", data=csv,
                    file_name="news_sentiment.csv", mime="text/csv")



# Additional UI Elements
st.markdown("---")
st.write("Created by [Kyle Yeung](https://github.com/kyle-ycp)")