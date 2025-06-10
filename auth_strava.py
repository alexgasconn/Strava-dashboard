import streamlit as st
import requests
import time

import streamlit as st

CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]

def get_auth_url():
    return (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"
        f"&approval_prompt=auto&scope=read,activity:read_all"
    )

def exchange_token(code):
    response = requests.post("https://www.strava.com/oauth/token", data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    })
    return response.json()

def refresh_token(refresh_token):
    response = requests.post("https://www.strava.com/oauth/token", data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    })
    return response.json()

def authenticate():
    query_params = st.experimental_get_query_params()

    if "access_token" not in st.session_state:
        if "code" in query_params:
            tokens = exchange_token(query_params["code"][0])
            if "access_token" in tokens:
                st.session_state["access_token"] = tokens["access_token"]
                st.session_state["refresh_token"] = tokens["refresh_token"]
                st.session_state["expires_at"] = tokens["expires_at"]
                st.experimental_rerun()
            else:
                st.error("Error during authentication.")
        else:
            st.markdown("### Connect your Strava account")
            st.link_button("🔗 Connect with Strava", get_auth_url())
            st.stop()
    else:
        # Check expiration
        if time.time() > st.session_state["expires_at"]:
            tokens = refresh_token(st.session_state["refresh_token"])
            st.session_state["access_token"] = tokens["access_token"]
            st.session_state["refresh_token"] = tokens["refresh_token"]
            st.session_state["expires_at"] = tokens["expires_at"]

    return st.session_state["access_token"]
