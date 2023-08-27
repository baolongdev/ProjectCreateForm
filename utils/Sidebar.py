import streamlit as st
from utils.Dashboard import *
from utils.Informations import *
from utils.Documentation import *
from PIL import Image

def Sidebar(current_dir):
    banner = current_dir / "assets" / "img" / "logoDoan_Truong.png"
    banner = Image.open(banner)
    with st.sidebar:
        st.image(banner)
        st.title("Tool Create Form")
        selected_page = st.empty()
        
        st.divider()
        sidebar_container = st.container()

        st.title("Support")
        st.success(
            """
            For any issues using the app, contact: 
            longle12042006a@gmail.com
            """
        )
           
    page_names_to_funcs = {
        "🔥Documentation": Documentation,
        "⚙️Dashboard": Dashboard, 
        "🎉Additional informations": Informations,
    }
    with selected_page:
        st.selectbox("Select a page", page_names_to_funcs.keys(), key ="select_page")
    
    page_names_to_funcs[st.session_state.select_page](sidebar_container)