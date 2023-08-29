from streamlit_sparrow_labeling import st_sparrow_labeling as st_labeling
from streamlit_sparrow_labeling import DataProcessor
from streamlit_elements import elements, mui, html
from modules.agstyler import PINLEFT
from streamlit_elements import *
from modules import agstyler
from paddleocr import PaddleOCR
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import shutil
import json
import os
# =========================
from modules.ExtractionDocument import ExtractionDocument
from modules.GoogleForm import GoogleFormGenerator
from modules.DocumentConverter import DocumentConverter


class DocumentProcess:
    class Model:
        img_file = None
        rects_file = None
        labels_file = "assets/data/labels.json"

        assign_labels_text = "Assign Labels"
        text_caption_1 = "Check 'Assign Labels' to enable editing of labels and values, move and resize the boxes to annotate the document."
        text_caption_2 = "Add annotations by clicking and dragging on the document, when 'Assign Labels' is unchecked."

        labels = ["", "item_title", "item_question", "item_answer", "item_right_answer","item_ignore"]

        selected_field = "Selected Field: "
        save_text = "Save"
        saved_text = "Saved!"

        subheader_1 = "Select"
        subheader_2 = "Upload"
        subheader_3 = "Create form"
        annotation_text = "Annotation"
        no_annotation_file = "No annotation file selected"
        no_annotation_mapping = "Please annotate the document. Uncheck 'Assign Labels' and draw new annotations"

        download_text = "Download"
        download_hint = "Download the annotated structure in JSON format"

        annotation_selection_help = "Select an annotation file to load"
        upload_help = "Upload a file to annotate"
        upload_button_text = "Upload"
        upload_button_text_desc = "Choose a file"

        assign_labels_text = "Assign Labels"
        assign_labels_help = "Check to enable editing of labels and values"

        export_labels_text = "Export Labels"
        export_labels_help = "Create key-value pairs for the labels in JSON format"
        done_text = "Done"

        grouping_id = "ID"
        grouping_value = "Value"

        completed_text = "Completed"
        completed_help = "Check to mark the annotation as completed"

        error_text = "Value is too long. Please shorten it."
        selection_must_be_continuous = "Please select continuous rows"
        
        def set_uploaded_file_images(self, uploaded_file_image):
            if 'uploaded_file_image' not in st.session_state:
                st.session_state['uploaded_file_image'] = []
            st.session_state['uploaded_file_image'].append(uploaded_file_image)

        def get_uploaded_file_images(self):
            if 'uploaded_file_image' not in st.session_state:
                return []
            return st.session_state['uploaded_file_image']
        
        def set_rects_file(self, rects_file):
            if 'rects_file' not in st.session_state:
                st.session_state['rects_file'] = []
            st.session_state['rects_file'].append(rects_file)

        def get_rects_file(self):
            if 'rects_file' not in st.session_state:
                return []
            return st.session_state['rects_file']
        
        def set_index_select(self, index_select):
            st.session_state['index_select'] = index_select

        def get_index_select(self):
            if 'index_select' not in st.session_state:
                return 0
            return st.session_state['index_select']
        
        def set_data_result(self, data_result):
            with open(data_result, "r") as f:
                result = json.load(f)
            st.session_state['data_result'] = result

        def get_data_result(self):
            if 'data_result' not in st.session_state:
                return None
            return st.session_state['data_result']
        
        def set_image_file(self, img_file):
            st.session_state['img_file'] = img_file

        def get_image_file(self):
            if 'img_file' not in st.session_state:
                return None
            return st.session_state['img_file']
        
    
    def __init__(self) -> None:
        self.convert_to_label = None
    
    def view(self, model, sidebar):
        with open(model.labels_file, "r") as f:
            labels_json = json.load(f)
        labels_list = labels_json["labels"]
        labels = ['']
        for label in labels_list:
            labels.append(label['name'])
        model.labels = labels
        
        placeholder_show = st.empty()
        
        with sidebar:
            createform = st.empty()
            st.subheader(model.subheader_1)
            name_group = st.text_input("name group")
            with st.expander("Option"):
                language_select = st.selectbox(
                    "Select Language",
                    ("English", "Vietnamese"),
                )
            with st.form("upload-form", clear_on_submit=True):
                uploaded_file = st.file_uploader(model.upload_button_text_desc, accept_multiple_files=True,
                                                 type=['png', 'jpg', 'jpeg', 'pdf'],
                                                 help=model.upload_help,
                                                 key="uploaded_file" 
                                                )
                submitted = st.form_submit_button(model.upload_button_text)
                
                if submitted and uploaded_file is not None:
                    with st.spinner('Wait for it...'):
                        self.upload_file(model, uploaded_file, name_group, language_select)
                    
                    index = model.get_index_select()
                    model.set_image_file(model.get_uploaded_file_images()[index])
                    model.set_data_result(model.get_rects_file()[index])
            
        if model.get_image_file() is not None:
            docImg = model.get_image_file()
            data_processor = DataProcessor()
            saved_state = model.get_data_result()   
            print(model.get_rects_file())
            with placeholder_show.container():
                assign_labels = st.checkbox(model.assign_labels_text, True, help=model.assign_labels_help)
                self.render_button(model, len(model.get_uploaded_file_images()))
                mode = "transform" if assign_labels else "rect"
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    result_rects = self.render_doc(model, docImg, saved_state, mode)
    
    
    
    def render_doc(self, model, docImg, saved_state, mode, height = 905, width = 640):
        with st.container():
            result_rects = st_labeling(
                fill_color = "rgba(0, 151, 255, 0.3)",
                stroke_width = 2,
                stroke_color = "rgba(0, 50, 255, 0.7)",
                background_image = docImg,
                initial_rects = saved_state,
                height = height,
                width = width,
                drawing_mode = mode,
                display_toolbar = True,
                update_streamlit = True,
                doc_height=3509,
                doc_width=2480,
                # image_rescale = True,
                key="doc_annotation",               
            )
            return result_rects
    

    def handChange(self, event, page, model):
        uploaded_file = st.session_state.uploaded_file
        if model.get_index_select() != (page-1):
            model.set_index_select(page - 1)        
            index = model.get_index_select()
            model.set_image_file(model.get_uploaded_file_images()[index])
            model.set_data_result(model.get_rects_file()[index])
    
    
    def render_button(self, model, count):
        with elements("endpage"):
            mui.Pagination(
                count=count, 
                onChange=lambda event, page: self.handChange(event, page, model),
                shape="rounded" ,
                color="primary",
                defaultPage=model.get_index_select()+1
            )
                
            
    def upload_file(self, model, uploaded_file, name_group = None, language_select = 'en'):
        language = {
            "Vietnamese":"vi",
            "English":"en"    
        }
        self.convert_to_label = ExtractionDocument(
            output="assets/data/output",
            lang=language[language_select]
        )
        if name_group is None:
            name_group = "demo"
        _return = []
        count = 0
        for file in uploaded_file:
            self.convert_to_label.set_save_folder_group(name_group)
            self.convert_to_label.set_save_folder_element(count)
            if file is not None:
                file_name, extension = file.name.split(".")
                extension = extension.lower()
                output_json = None
                if file.type == 'application/pdf':
                    doc = DocumentConverter()
                    datas = doc.convert_pdf_to_images(file.read())
                    for doc_name, doc_image in datas:
                        self.convert_to_label.add_label_with_PaddleOCR(image_data=doc_image)
                        image = self.convert_to_label.get_data()["image_raw"]
                        datafile = self.convert_to_label.get_data()["datafile"]
                        # res_0 = self.convert_to_label.get_data()["res_0"]
                        model.set_uploaded_file_images(image)
                        model.set_rects_file(datafile)
                        st.toast(f"Done {count}")
                        print("Done {count}")
                        count+=1
                if extension in ('png', 'jpg', 'jpeg'):
                    self.convert_to_label.add_label_with_PaddleOCR(image_data=file)
                    image = self.convert_to_label.get_data()["image_raw"]
                    datafile = self.convert_to_label.get_data()["datafile"]
                    # res_0 = self.convert_to_label.get_data()["res_0"]
                    model.set_uploaded_file_images(image)
                    model.set_rects_file(datafile)
                    st.toast(f"Done {count}")
                    print(f"Done {count}")
            count += 1
            
                        
                        