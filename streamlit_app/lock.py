import streamlit as st
import redis
import time

# Access Redis credentials from the secrets file
redis_host = st.secrets["redis"]["host"]
redis_port = st.secrets["redis"]["port"]
redis_username = st.secrets["redis"]["username"]
redis_password = st.secrets["redis"]["password"]

# Connect to Redis
redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    decode_responses=True,
    username=redis_username,
    password=redis_password,
)

# Max number of promotions
MAX_PROMOTIONS = 5

# A key in Redis to track the number of promotions
PROMOTION_COUNT_KEY = "promotion_count"

# Distributed lock key
LOCK_KEY = "promotion_lock"

def get_promotion_count():
    """Get the current promotion count from Redis"""
    count = redis_client.get(PROMOTION_COUNT_KEY)
    return int(count) if count else 0

def increment_promotion_count():
    """Increment the promotion count in Redis"""
    redis_client.incr(PROMOTION_COUNT_KEY)

def reset_promotion_count():
    """Reset the promotion count to 0"""
    redis_client.set(PROMOTION_COUNT_KEY, 0)

def try_acquire_lock():
    """Try to acquire a distributed lock using Redis SETNX"""
    return redis_client.setnx(LOCK_KEY, 1)  # Set the lock if it doesn't exist

def release_lock():
    """Release the lock"""
    redis_client.delete(LOCK_KEY)

def promote_user_with_lock():
    """Promote a user with a lock to avoid race conditions"""
    if try_acquire_lock():
        # Check if there is space for more promotions
        if get_promotion_count() < MAX_PROMOTIONS:
            increment_promotion_count()
            st.success("Congratulations! You have been promoted to SDE 2!")
        else:
            st.warning("Sorry, the promotion limit of 5 has been reached. Hisham insists!")
        release_lock()  # Always release the lock after promotion attempt
    else:
        st.warning("Please wait, another promotion is in progress.")

def promote_user_without_lock():
    """Promote a user without using a lock (simulating race conditions)"""
    if get_promotion_count() < MAX_PROMOTIONS:
        time.sleep(10)
        increment_promotion_count()
        st.success("Congratulations! You have been promoted to SDE 2!")
    else:
        st.warning("Sorry, the promotion limit of 5 has been reached. Hisham insists!")

def show_with_lock_page():
    st.title("Distributed Locks Demo - With Lock")

    st.write("Try to promote to SDE 2! Hisham, the CTO, says only 5 promotions are allowed, not me!")

    if st.button("Promote with Lock"):
        promote_user_with_lock()

def show_without_lock_page():
    st.title("Distributed Locks Demo - Without Lock")

    st.write("Try to promote to SDE 2! Hisham, the CTO, says only 5 promotions are allowed, not me!")

    if st.button("Promote without Lock"):
        promote_user_without_lock()

def show_reset_button():
    """Display the reset button and reset the promotion count"""
    if st.button("Reset Promotion Count"):
        reset_promotion_count()
        st.success("The promotion count has been reset to 0.")

def show_promotion_page():
    # Navigation to switch between pages
    page = st.selectbox("Choose a demo:", ["With Lock", "Without Lock"])

    if page == "With Lock":
        show_with_lock_page()
    elif page == "Without Lock":
        show_without_lock_page()

    # Display the reset button on every page
    show_reset_button()

