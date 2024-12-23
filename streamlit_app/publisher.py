import streamlit as st
import redis
import time

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

# List of pre-defined messages
messages = [
    "Did you know ducks are secretly plotting world domination? Quack!",
    "Anime is fine... but I think ducks have a much more compelling storyline.",
    "If you ask me, ducks should get their own anime series. *A Quack Story*, anyone?",
    "Imagine if ducks were the main characters in anime. Better than the current ones, right?",
    "Why settle for anime when you could be watching a duck swim gracefully through life?",
    "A wise duck once said, 'The secret to success is to stay calm and never stop waddling.'",
]


def publish_message(channel, message):
    """Publish a message to the specified Redis channel"""
    redis_client.publish(channel, message)


def show_publisher_page():
    st.title("Redis Publisher Page")

    # Set channel name statically to 'demo_channel'
    channel_name = "demo_channel"

    # Text area to input the message
    message = st.text_area("Enter the message to publish", "")

    # Button to publish the message
    if st.button("Publish Message"):
        if message:  # Ensure message is not empty
            publish_message(channel_name, message)
            st.success(f"Message '{message}' published to channel '{channel_name}'")
        else:
            st.warning("Please enter a message to publish.")

    # Button to publish the pre-defined messages
    if st.button("DO NOT TOUCH unless you are ready to summon Redis!"):
        for msg in messages:
            publish_message(channel_name, msg)
            time.sleep(0.5)
        st.success(
            f"Messages have been published to the channel. And just to clarify, those messages weren't my idea... Ducks? Anime? I'm just the messenger!"
        )
