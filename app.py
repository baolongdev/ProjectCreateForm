from pathlib import Path
import streamlit as st
from modules import *
from utils import *


def App(current_dir):
    Sidebar(current_dir)
    pass

if __name__ == '__main__':
    current_dir = Path(".")
    InitPageSetting(st, current_dir, "Create Form", "⚙️")
    App(current_dir)