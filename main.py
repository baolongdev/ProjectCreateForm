from pathlib import Path
import streamlit as st
from modules import *
from utils import *


def App(current_dir):
    css__custom = current_dir / "assets" / "styles" / "custom.css"
    Custom_CSS(st, css__custom)
    Sidebar(current_dir)
    pass


if __name__ == '__main__':
    # add path main
    current_dir = Path(".")
    InitPageSetting(st, current_dir, "Create Form", "⚙️")
    App(current_dir)