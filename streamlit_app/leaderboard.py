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

# Constants
PASSWORDS = ["duck", "cat", "dog", "rabbit", "parrot"]  # List of passwords
LEADERBOARD_KEY = "leaderboard"
GUESSES_KEY_PREFIX = "guesses_for_password"  # Key prefix for tracking guesses per password
MAX_WINNERS = 5  # Only five VIPs can crack each password
REFRESH_INTERVAL = 2  # How often the leaderboard updates (because everyone loves suspense)

# Functions
def reset_game():
    """Reset the leaderboard and guesses for all passwords."""
    redis_client.delete(LEADERBOARD_KEY)
    for i in range(len(PASSWORDS)):
        redis_client.delete(f"{GUESSES_KEY_PREFIX}_{i}")

def add_point(username):
    """Give the player a glorious point!"""
    redis_client.zincrby(LEADERBOARD_KEY, 1, username)

def record_guess(password_index, username):
    """Keep a record of who cracked the code (and who didn’t)."""
    redis_client.rpush(f"{GUESSES_KEY_PREFIX}_{password_index}", username)

def get_guess_count(password_index):
    """Check how many brave souls have attempted this password."""
    guesses = redis_client.lrange(f"{GUESSES_KEY_PREFIX}_{password_index}", 0, -1)
    return len(set(guesses))

def is_eligible_for_points(password_index, username):
    """Only allow fresh thinkers to earn points."""
    guesses = redis_client.lrange(f"{GUESSES_KEY_PREFIX}_{password_index}", 0, -1)
    return username not in guesses and get_guess_count(password_index) < MAX_WINNERS

def get_leaderboard():
    """Fetch the ultimate ranking of codebreakers."""
    return redis_client.zrevrange(LEADERBOARD_KEY, 0, -1, withscores=True)

def update_leaderboard_placeholder(placeholder):
    """Keep the leaderboard shiny and up to date."""
    with placeholder.container():
        st.subheader("Real-Time Leaderboard 🏆")
        leaderboard = get_leaderboard()
        if leaderboard:
            for i, (user, score) in enumerate(leaderboard, start=1):
                st.write(f"**{i}. {user}: {int(score)} points** 🥳")
        else:
            st.write("No entries yet! Be the first to crack a password! 🚀")

# Main app logic
def show_leaderboard_page():
    st.title("🔐 Distributed Locks Demo - Leaderboard Game")

    # Username input
    username = st.text_input("Enter your secret agent codename:", key="username").strip()

    if not username:
        st.warning("Please enter a codename! No codename, no game. 😢")
        return

    # Reset button for the game
    if st.button("Reset Game 🔄"):
        reset_game()
        st.success("The game has been reset! All scores wiped. Fresh start, folks. 🌟")

    # Display instructions
    st.write("### Instructions")
    st.write(
        "🚀 Your mission, should you choose to accept it: guess the passwords for each box below. "
        "Only the first **5 codebreakers** for each password earn points. Good luck, agent! 🕵️"
    )

    # Leaderboard placeholder
    leaderboard_placeholder = st.empty()

    # Password guessing
    for i, password in enumerate(PASSWORDS):
        st.write(f"### 🗄️ Password Box {i+1}")
        guess = st.text_input(f"Enter the password for Box {i+1}:", key=f"guess_{i}")

        if st.button(f"Submit Guess for Box {i+1} 🚪", key=f"submit_{i}"):
            if is_eligible_for_points(i, username):
                if guess == password:
                    add_point(username)
                    record_guess(i, username)
                    st.success(f"🎉 Correct! {username}, you’ve cracked the code for Box {i+1}!")
                else:
                    st.warning("❌ Oops, wrong password. Better luck next time!")
            else:
                st.warning(
                    "⛔ Sorry, either the limit of 5 winners has been reached or you've already tried this one."
                )

    # Continuously update the leaderboard in the placeholder
    while True:
        update_leaderboard_placeholder(leaderboard_placeholder)
        time.sleep(REFRESH_INTERVAL)
