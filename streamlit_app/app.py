import streamlit as st
from caching import show_caching_page
from publisher import show_publisher_page
from subscriber import show_subscriber_page
from lock import show_promotion_page


def main():
    st.sidebar.title("Redis Live Demo")
    page = st.sidebar.radio(
        "Choose a use case", ("Caching", "Publisher", "Subscriber", "Lock")
    )

    if page == "Caching":
        show_caching_page()
    elif page == "Publisher":
        show_publisher_page()
    elif page == "Subscriber":
        show_subscriber_page()
    elif page == "Lock":
        show_promotion_page()


if __name__ == "__main__":
    main()
