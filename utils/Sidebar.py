import streamlit as st
from utils.Dashboard import *
from utils.Informations import *
from utils.Documentation import *
from utils.ExtractDocument import *
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
        "🔥Documentation": {"func":Documentation, "id": 0},
        "✨ExtractDocument": {"func":ExtractDocument, "id": 1},
        "⚙️Dashboard": {"func":Dashboard, "id": 2}, 
        "🎉Additional informations": {"func":Informations, "id": 3},
    }
    def select_page():
        st.experimental_set_query_params(
            page=st.session_state.select_page
        )
        st.toast(f"Welcom to {st.session_state.select_page}")
        st.balloons()
        pass
    
    if "index_page" not in st.session_state:
        st.session_state["index_page"] = 0
    
    if "page" in st.experimental_get_query_params():
        page = str(st.experimental_get_query_params()["page"][0])
        if page in page_names_to_funcs:
            st.session_state.index_page = page_names_to_funcs[page]["id"]
            page_names_to_funcs[page]["func"](sidebar_container)
            with selected_page:
                st.selectbox(
                    "Select a page", 
                    page_names_to_funcs.keys(), 
                    key ="select_page", 
                    on_change=select_page,
                    index=st.session_state.index_page
                )
        else:
            st.warning(f"Page Not Found {st.experimental_get_query_params()['page'][0]}! ")
            with selected_page:
                if st.button("Go home!"):
                    st.experimental_set_query_params(
                        page="🔥Documentation"
                    )
    else:
        st.experimental_set_query_params(page="🔥Documentation")
        st.experimental_rerun()