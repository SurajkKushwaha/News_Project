import streamlit as st
import requests

# 1. Page Config
st.set_page_config(page_title="LIVE NEWS ", layout="centered")
st.markdown("<h1 style='text-align: center;'> LIVE NEWS </h1>", unsafe_allow_html=True)
st.markdown("---")





# Streamlit ka ek rule hai—jab bhi aap koi button dabate ho, pura code starting se run hota hai. Iska matlab saare variables delete ho jate hain.
# Hamein 'Next Page' ka token yaad rakhna hai taaki agla page load kar sakein. Isliye hum st.session_state use karte hain.


# --- SESSION STATE SETUP ---
# We use this to remember the "next page" token from the API
if 'next_page_id' not in st.session_state:
    st.session_state.next_page_id = None
# Yeh condition if 'next_page_id' not in...
# sirf ye ensure karti hai ki hum variable ko pehli baar define karein, aur baar-baar overwrite na karein."




# 2. Sidebar Filters
# We move the controls to a sidebar to keep the main view clean
with st.sidebar:
    st.header("⚙️ Settings")

    # Filter: Category
    # The API expects lowercase strings like 'health', but we show 'Health' to user
    category = st.selectbox(
        "Choose a Category:",
        options=["education", "entertainment", "health", "food", "crime", "technology", "sports", "business"],
        index=5  # Default to 'health' (0=education, 1=entertainment, 2=health)
    )

    # Filter: Country
    # Dictionary to map readable names to API codes
    country_map = {
        "India": "in",
        "United States": "us",
        "Japan": "jp",
        "United Kingdom": "gb"
    }
    country_name = st.selectbox("Choose a Country:", list(country_map.keys()))
    country_code = country_map[country_name]  # Get the code (e.g., "in")

    # Button to reset the pagination when filters change
    # ("Is code ka matlab simple hai: Jab bhi hum Category ya Country change karein, toh hum purane page number par na atke rahein. "
    #  "Hum chahte hain ki naya topic hamesha Page 1 se shuru ho, isliye hum ID ko reset karke app ko refresh kar rahe hain.")
    if st.button("Apply Filters"):
        st.session_state.next_page_id = None  # Reset to first page
        st.rerun()


# 3. Function to fetch data
def fetch_news(page_id=None):
    # Base URL
    base_url = "https://newsdata.io/api/1/latest"

    # Your API Key (Ideally, keep this safe, but for learning it's okay here)
    api_key = "pub_a2a77ae0275040b89a657a4695df8b0c"

    # Construct the parameters dynamically based on user selection
    params = {
        "apikey": api_key,
        "country": country_code,
        "category": category,
        "language": "en",  # Keeping it English for simplicity
        "removeduplicate": "1"
    }

    # If we have a page_id (for next page), add it to params
    if page_id:
        params["page"] = page_id

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None


# 4. Main UI
st.title(f"{category.capitalize()} News in {country_name}")

# Fetch the news using the current session state page ID
news_data = fetch_news(st.session_state.next_page_id)

if news_data and 'results' in news_data:
    articles = news_data['results']

    # Display articles
    for article in articles:
        title = article.get('title', 'No Title')
        description = article.get('description')
        link = article.get('link', '#')
        image_url = article.get('image_url')
        source_id = article.get('source_id', 'Unknown')

        with st.container():
            st.subheader(title)
            st.caption(f"Source: {source_id}")

            if image_url:

                col1, col2 = st.columns([3, 1])
                with col1:
                    if description:
                        st.write(description[:300] + "...")  # Limit text length
                    else:
                        st.write("_No description available._")
                    st.link_button("Read Full Article 🔗", link)
                with col2:
                    st.image(image_url, use_container_width=True)
            else:
                if description:
                    st.write(description)
                st.link_button("Read Full Article 🔗", link)
            st.divider()

    # --- PAGINATION LOGIC ---
    # The API returns a 'nextPage' token if there are more results.
    next_page_token = news_data.get('nextPage')

    if next_page_token:
        # We create a button to go to next page
        if st.button("Load Next Batch ➡️"):
            # Update the session state with the new token
            st.session_state.next_page_id = next_page_token
            # Rerun the app to fetch the new data
            st.rerun()
    else:
        st.info("No more news available for this category.")

elif news_data:
    st.warning("No news found for these filters.")