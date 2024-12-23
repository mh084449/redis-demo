import streamlit as st
import redis
import threading
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

# List to store received messages
messages = []


def subscribe_to_channel():
    """Subscribe to the Redis demo_channel and listen for messages."""
    pubsub = redis_client.pubsub()
    pubsub.subscribe("demo_channel")

    for message in pubsub.listen():
        if message["type"] == "message":
            messages.append(message["data"])


def start_subscriber():
    """Start the subscriber thread to listen to the demo_channel."""
    st.session_state.subscribed = True
    # Start the subscriber in a new thread
    threading.Thread(target=subscribe_to_channel, daemon=True).start()
    st.write("Subscribed to demo_channel.")


def show_subscriber_page():
    st.title("Redis Subscriber Page")

    # Ensure we have a session state to track subscription status
    if "subscribed" not in st.session_state:
        st.session_state.subscribed = False

    # Display the button to subscribe to demo_channel only if not already subscribed
    if not st.session_state.subscribed:
        st.button("Subscribe to demo_channel", on_click=start_subscriber)
    else:
        # Create a placeholder for the messages section
        message_placeholder = st.empty()

        while True:
            # Display received messages inside the placeholder
            with message_placeholder.container():
                st.write("Messages:")
                if messages:
                    for msg in messages:
                        st.write(msg)
                else:
                    st.write("Waiting for messages...")

            # Sleep briefly before refreshing the message list
            time.sleep(1)  # Sleep briefly to allow time for new messages to come in
