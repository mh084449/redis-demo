import streamlit as st
import time
import redis

# Access Redis credentials from the secrets file
redis_host = st.secrets["redis"]["host"]
redis_port = st.secrets["redis"]["port"]
redis_username="default"
redis_password = st.secrets["redis"]["password"]

# Connect to Redis
redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    decode_responses=True,
    username=redis_username,
    password=redis_password,
)


# Simulated "slow backend" function
def fetch_data_from_backend():
    time.sleep(2)  # Simulate a delay (e.g., querying a slow database)
    return "This is the data from the backend"


# Fetch data with caching (Cache-aside strategy)
def fetch_data_with_cache(key):
    # Check if the data is already in Redis
    cached_data = redis_client.get(key)
    if cached_data:
        st.write("[CACHE HIT] Returning data from cache.")
        return cached_data

    st.write("[CACHE MISS] Fetching data from backend...")
    data = fetch_data_from_backend()

    # Store the data in Redis for future use
    redis_client.setex(key, 30, data)  # Cache for 30 seconds
    return data


# Show Caching Demo Page
def show_caching_page():
    st.title("Redis Caching Demo")

    # Button to fetch data
    if st.button("Fetch Data"):
        key = "my_data_key"

        # First fetch - should be a cache miss
        start_time = time.time()
        data = fetch_data_with_cache(key)
        st.write(f"Data: {data}")
        st.write(f"Time taken: {time.time() - start_time:.2f} seconds")
