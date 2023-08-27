import streamlit as st

def Authors():
    st.title("Authors")
    st.text("BLong longle12042006a@gmail.com")   

def Changelog():
    st.title("Changelog")
    st.text("Version: 1.0.0")   
    
    
def Resources():
    st.title("Resources")
    
    
def sidebarConfig(sidebar) -> None:
    with sidebar:
        pass


def Informations(sidebar):
    sidebarConfig(sidebar)
    
    Authors()
    st.markdown("#")
    st.divider()
    Changelog()
    st.markdown("#")
    st.divider()
    Resources()
    
    
    