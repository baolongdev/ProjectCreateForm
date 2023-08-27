import json
import math
import streamlit as st
from modules import *
from pathlib import Path
from PIL import Image
from streamlit_img_label import st_img_label

def sidebarConfig(sidebar):
    with sidebar:
        pass

def customsGroup(current_dir):
    css__custom = f'{current_dir}/assets/styles/custom.css'
    Custom_CSS(st, css__custom)
    Custom_Code(st, """
            <div class="main__title"> 
                <h3> Documentation <h3>
            <div/>        
        """)


def main(sidebar):
    DataReview().view(DataReview.Model(), sidebar)

def Documentation(sidebar):
    current_dir = Path(".")
    sidebarConfig(sidebar)
    customsGroup(current_dir)
    main(sidebar)