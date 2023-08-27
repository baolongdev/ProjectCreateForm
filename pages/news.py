import streamlit as st
from modules import *
from streamlit_javascript import st_javascript



current_dir = get_from_control_reference("current_dir")
js__custom = current_dir / "assets" / "js" / "main.js"
print(js__custom)
with open(js__custom) as f:
    return_value = st_javascript(f"""{f}""")
    st.markdown(f"Return value was: {return_value}")
st.text("news")