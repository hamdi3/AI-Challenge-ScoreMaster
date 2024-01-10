import streamlit as st

def show():
    # Loading session state variables
    if 'users' not in st.session_state:
        st.error("Couldn't connect to database.")

    else:
        users = st.session_state["users"]

    # Initialize the login state if not already present
    if 'login_page' and 'Logged_in' not in st.session_state:
        st.session_state.login_page = True
        st.session_state.Logged_in = False


    if 'Logged_in' not in st.session_state or st.session_state.Logged_in == False:
        if st.session_state.login_page:
            # Login form
            st.title("Login Page")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.button("Login")
            register_button = st.button("Don't have an account yet?")

            # Switching to Registration form
            if register_button:
                st.session_state.login_page = False
                st.experimental_rerun() # causes the app to rerun and apply the updated login_page value.

            # Verify credentials
            if login_button:
                user = users.find_one({"username": username})
                if user and user["password"] == password:
                    st.success("Login successful!")
                    if 'Logged_in' and 'userName' not in st.session_state:
                        st.session_state.Logged_in = True
                        st.session_state.userName = username
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password.")

        else:
            # Registration form
            st.title("Registration Page")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_button = st.button("Register")
            Login_button = st.button("Already have an account?")

            # Switching to Login form
            if Login_button:
                st.session_state.login_page = True
                st.experimental_rerun()

            # Store user information in the database
            if register_button:
                if password == confirm_password:
                    user = users.find_one({"username": username})
                    if user:
                        st.error("Username already exists. Please choose a different username.")
                    else:
                        user_data = {"username": username, "password": password}
                        users.insert_one(user_data)
                        st.success("Registration successful! You can now login.")
                else:
                    st.error("Passwords do not match.")

    else:
        st.title("Log out?")
        st.text(f"Hi {st.session_state.userName} looks like you're already logged in, do you want to log out?")
        Logout = st.button("Log me out")

        if Logout:
            del st.session_state.Logged_in
            del st.session_state.userName
            st.success("You have been logged out.")
            st.experimental_rerun()

show()