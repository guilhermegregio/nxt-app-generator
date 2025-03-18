import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from dotenv import load_dotenv
import os

load_dotenv()

AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_REDIRECT_URI = os.getenv('AUTH0_REDIRECT_URI')

AUTH0_AUTHORIZE_URL = f"https://{AUTH0_DOMAIN}/authorize"
AUTH0_TOKEN_URL = f"https://{AUTH0_DOMAIN}/oauth/token"
AUTH0_USERINFO_URL = f"https://{AUTH0_DOMAIN}/userinfo"


def get_auth0_session(state=None, token=None):
    return OAuth2Session(
        AUTH0_CLIENT_ID,
        AUTH0_CLIENT_SECRET,
        scope='openid profile email',
        redirect_uri=AUTH0_REDIRECT_URI,
        state=state,
        token=token,
    )


def login():
    auth0 = get_auth0_session()
    uri, state = auth0.create_authorization_url(AUTH0_AUTHORIZE_URL)
    st.session_state['oauth_state'] = state
    st.link_button("🔐 Login com Auth0", uri)


def logout():
    st.session_state.clear()
    st.query_params.clear()
    st.rerun()


def callback():
    params = st.query_params.to_dict()

    if 'state' not in params or 'code' not in params:
        st.error("Parâmetros inválidos retornados na autenticação.")
        return

    state = params['state']
    code = params['code']

    auth0 = get_auth0_session(state=state)

    # reconstrói a URL completa para validação
    full_url = f"{AUTH0_REDIRECT_URI}&code={code}&state={state}"

    try:
        token = auth0.fetch_token(
            AUTH0_TOKEN_URL,
            authorization_response=full_url,
            include_client_id=True,
        )
        userinfo = auth0.get(AUTH0_USERINFO_URL).json()
        st.session_state['user'] = userinfo
        st.session_state['token'] = token
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Erro na autenticação: {e}")


def main_app():
    st.success(f"Bem-vindo(a), {st.session_state['user']['name']}!")
    st.json(st.session_state['user'])
    st.button("🚪 Logout", on_click=logout)


def main():
    st.title("🔐 Streamlit com Auth0")

    params = st.query_params

    if 'user' in st.session_state:
        main_app()
    elif 'callback' in params:
        callback()
    else:
        login()


if __name__ == "__main__":
    main()
