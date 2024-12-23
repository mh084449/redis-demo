import streamlit as st
import redis
import time

# Connect to Redis
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Constants
PASSWORDS = ["duck", "cat", "dog", "rabbit", "parrot"]  # List of passwords
LEADERBOARD_KEY = "leaderboard"
GUESSES_KEY_PREFIX = "guesses_for_password"  # Key prefix for tracking guesses per password
MAX_WINNERS = 5  # Limit the number of winners per password
REFRESH_INTERVAL = 2  # Refresh interval for leaderboard in seconds

# Functions
def reset_game():
    """Reset the leaderboard and guesses for all passwords."""
    redis_client.delete(LEADERBOARD_KEY)
    for i in range(len(PASSWORDS)):
        redis_client.delete(f"{GUESSES_KEY_PREFIX}_{i}")

def add_point(username):
    """Increment the user's score on the leaderboard."""
    redis_client.zincrby(LEADERBOARD_KEY, 1, username)

def record_guess(password_index, username):
    """Record a guess for a specific password."""
    redis_client.rpush(f"{GUESSES_KEY_PREFIX}_{password_index}", username)

def get_guess_count(password_index):
    """Get the count of unique guesses for a specific password."""
    guesses = redis_client.lrange(f"{GUESSES_KEY_PREFIX}_{password_index}", 0, -1)
    return len(set(guesses))

def is_eligible_for_points(password_index, username):
    """Check if the user is eligible to earn points for a specific password."""
    guesses = redis_client.lrange(f"{GUESSES_KEY_PREFIX}_{password_index}", 0, -1)
    return username not in guesses and get_guess_count(password_index) < MAX_WINNERS

def get_leaderboard():
    """Fetch the top users from the leaderboard."""
    return redis_client.zrevrange(LEADERBOARD_KEY, 0, -1, withscores=True)

def update_leaderboard_placeholder(placeholder):
    """Update the leaderboard within the provided placeholder."""
    with placeholder.container():
        st.subheader("Real-Time Leaderboard")
        leaderboard = get_leaderboard()
        if leaderboard:
            for i, (user, score) in enumerate(leaderboard, start=1):
                st.write(f"**{i}. {user}: {int(score)} points**")
        else:
            st.write("No entries yet!")

# Main app logic
def show_leaderboard_page():
    st.title("Distributed Locks Demo - Leaderboard Game")

    # Username input
    username = st.text_input("Enter your username:", key="username").strip()

    if not username:
        st.warning("Please enter a username to participate.")
        return

    # Reset button for the game
    if st.button("Reset Game"):
        reset_game()
        st.success("Game has been reset!")

    # Display instructions
    st.write("Guess the password for each round. Only the first 5 correct guesses for each password earn points.")

    # Leaderboard placeholder
    leaderboard_placeholder = st.empty()

    # Password guessing
    for i, password in enumerate(PASSWORDS):
        st.write(f"### Password Box {i+1}")
        guess = st.text_input(f"Enter the password for Box {i+1}:", key=f"guess_{i}")

        if st.button(f"Submit for Box {i+1}", key=f"submit_{i}"):
            if is_eligible_for_points(i, username):
                if guess == password:
                    add_point(username)
                    record_guess(i, username)
                    st.success(f"Correct! {username} earned a point!")
                else:
                    st.warning("Incorrect password!")
            else:
                st.warning("Sorry, the limit of 5 winners for this password has been reached or you've already guessed.")

    # Continuously update the leaderboard in the placeholder
    while True:
        update_leaderboard_placeholder(leaderboard_placeholder)
        time.sleep(REFRESH_INTERVAL)