from streamlit_sparrow_labeling import st_sparrow_labeling as st_labeling
from streamlit_sparrow_labeling import DataProcessor
from streamlit_elements import elements, mui, html
from modules.GoogleForm import GoogleFormGenerator
from modules.agstyler import PINLEFT
from streamlit_elements import *
from modules import agstyler
from paddleocr import PaddleOCR
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import math
import json
import os
# =========================
from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools


class DataReview: 
    class Model:
        img_file = None
        rects_file = None
        labels_file = "assets/data/labels.json"
        # groups_file = "docs/groups.json"

        assign_labels_text = "Assign Labels"
        text_caption_1 = "Check 'Assign Labels' to enable editing of labels and values, move and resize the boxes to annotate the document."
        text_caption_2 = "Add annotations by clicking and dragging on the document, when 'Assign Labels' is unchecked."

        labels = ["", "item_title", "item_question", "item_answer", "item_right_answer","item_ignore"]

        # groups = ["", "items_row1", "items_row2", "items_row3", "items_row4", "items_row5", "items_row6", "items_row7",
        #           "items_row8", "items_row9", "items_row10", "summary"]

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
        
        def set_image_file(self, img_file):
            st.session_state['img_file'] = img_file

        def get_image_file(self):
            if 'img_file' not in st.session_state:
                return None
            return st.session_state['img_file']

        data_result = None

        def set_data_result(self, data_result):
            st.session_state['data_result'] = data_result

        def get_data_result(self):
            if 'data_result' not in st.session_state:
                return None
            return st.session_state['data_result']
        
        def set_data_ret(self, data_ret):
            st.session_state['data_ret'] = data_ret

        def get_data_ret(self):
            if 'data_ret' not in st.session_state:
                return None
            return st.session_state['data_ret']
        
        rects_file = None

        def set_rects_file(self, rects_file):
            if 'rects_file' not in st.session_state:
                st.session_state['rects_file'] = []
            st.session_state['rects_file'].append(rects_file)

        def get_rects_file(self):
            if 'rects_file' not in st.session_state:
                return []
            return st.session_state['rects_file']
        
        file_name = None
        
        def set_file_name(self, file_name):
            st.session_state['file_name'] = file_name

        def get_file_name(self):
            if 'file_name' not in st.session_state:
                return None
            return st.session_state['file_name']

        check = None
        def set_check(self, check):
            st.session_state['check'] = check

        def get_check(self):
            if 'check' not in st.session_state:
                return None
            return st.session_state['check']
        
        index_select = 0
        def set_index_select(self, index_select):
            st.session_state['index_select'] = index_select

        def get_index_select(self):
            if 'index_select' not in st.session_state:
                return 0
            return st.session_state['index_select']
    
    
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
            with st.form("upload-form", clear_on_submit=True):
                uploaded_file = st.file_uploader(model.upload_button_text_desc, accept_multiple_files=True,
                                                 type=['png', 'jpg', 'jpeg'],
                                                 help=model.upload_help,
                                                 key="uploaded_file" 
                                                )
                submitted = st.form_submit_button(model.upload_button_text)
                
                if submitted and uploaded_file is not None:
                    with st.spinner('Wait for it...'):
                        ret = self.upload_file(model, uploaded_file)
                    
                    if ret is not None:
                        index = model.get_index_select()
                        file_names = self.get_existing_file_names(uploaded_file[index])
                        model.set_data_ret(ret)
                        model.set_file_name(file_names)
                        model.set_image_file(uploaded_file[index])
                        model.set_data_result(model.get_data_ret()[index])
                        
                        
        if model.get_image_file() is not None:
            docImg = Image.open(model.get_image_file())
            data_processor = DataProcessor()
            saved_state = model.get_data_result()            
            doc_height = docImg.height
            doc_width = docImg.width
                

        
            with placeholder_show.container():
                assign_labels = st.checkbox(model.assign_labels_text, True, help=model.assign_labels_help)
                self.render_button(model, len(uploaded_file))                
                mode = "transform" if assign_labels else "rect"
                col1, col2 = st.columns([1, 1])
                with col1:
                    result_rects = self.render_doc(docImg, saved_state, mode)
                with col2:
                    self.render_btn_createForm(model, createform)
                    tab = st.radio("Select", ["Mapping", "Grouping"], horizontal=True,
                        label_visibility="collapsed")

                    if tab == "Mapping":
                        self.render_form(model, result_rects, data_processor)
                    elif tab == "Grouping":
                        self.group_annotations(model, result_rects)
    
    def render_btn_createForm(self, model, sidebar):
        with sidebar:
            with st.form("create-form", clear_on_submit=True):
                link_form = st.empty()
                form_documentTitle = st.text_input(
                    "documentTitle",
                    placeholder="Nhập tên file",
                )
                title_form = st.text_input(
                    "TitleForm",
                    placeholder="Nhập tiêu đề",
                )
                form_description = st.text_area(
                    "description",
                    placeholder="Nhập thông tin miêu tả",
                )
                # quiz_toggle = st.toggle('Activate quiz')
                # required_toggle = st.toggle('Activate required')
                # shuffle_toggle = st.toggle('Activate shuffle')
                
                submitted = st.form_submit_button(model.upload_button_text)
                if submitted:
                    data = {"words": []}
                    arr_link = np.sort(model.get_rects_file())
                    for json_file in arr_link:
                        with open(json_file) as json_data:
                            file_data = json.load(json_data)
                            data["words"].extend(file_data.get("words", []))
                    
                    
                    form_generator = GoogleFormGenerator()
                    form_generator.authenticate()
                    form_generator.create_google_form(title_form, form_description, form_documentTitle)
                    form_generator.setting_configure(is_quiz=True)
                    with st.spinner("Wait for it..."):
                        form_generator.read_data_from_json(data)
                    with link_form:
                        st.markdown(f"Link form: [Link 😘]({form_generator.get_link_form()})" )

    
    
    def handChange(self, event, page, model):
        uploaded_file = st.session_state.uploaded_file
        model.set_index_select(page - 1)        
        index = model.get_index_select()
        file_names = self.get_existing_file_names(uploaded_file[index])
        model.set_file_name(file_names)
        model.set_image_file(uploaded_file[index])
        model.set_data_result(model.get_data_ret()[index])
        # st.experimental_rerun()
   
    def render_button(self, model, count):
        with elements("endpage"):
            mui.Pagination(
                count=count, 
                onChange=lambda event, page: self.handChange(event, page, model),
                shape="rounded" ,
                color="primary",
                defaultPage=model.get_index_select()+1
            )
            # page = 0
            # mui.Typography(f"Page {page}")
        
        
    def render_doc(self, docImg, saved_state, mode, height = 905, width = 640):
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
                # doc_height=3509,
                # doc_width=2480,
                doc_height=height+100,
                doc_width=width+370,
                # image_rescale = True,
                key="doc_annotation",               
            )
            return result_rects
        
    
    def render_form(self, model, result_rects, data_processor):
        with st.container():
            if result_rects is not None:
                with st.form(key="fields_form"):
                    toolbar = st.empty()
                    
                    self.render_form_view(result_rects.rects_data['words'], model.labels, result_rects,
                                          data_processor)
                    
                    with toolbar:
                        submit = st.form_submit_button(model.save_text, type="primary")
                        if submit:
                            for word in result_rects.rects_data['words']:
                                if len(word['value']) > 1000:
                                    st.error(model.error_text)
                                    return
                            
                            with open(model.get_rects_file()[model.get_index_select()], "w") as f:
                                json.dump(result_rects.rects_data, f, indent=2)
                                st.session_state[model.get_rects_file()[model.get_index_select()]] = result_rects.rects_data
                                model.set_data_result(result_rects.rects_data)
                                st.experimental_rerun()
                if len(result_rects.rects_data['words']) == 0:
                    st.toast(model.no_annotation_mapping)
                    return
                else:
                    with open(model.get_rects_file()[model.get_index_select()], 'rb') as file:
                        st.download_button(label=model.download_text,
                                           data=file,
                                           file_name=model.get_file_name() + ".json",
                                           mime='application/json',
                                           help=model.download_hint)


    def render_form_view(self, words, labels, result_rects, data_processor):
        data = []
        for i, rect in enumerate(words):
            group, label = rect['label'].split(":", 1) if ":" in rect['label'] else (None, rect['label'])
            data.append({'id': i, 'value': rect['value'], 'label': label})
        df = pd.DataFrame(data)
        
        formatter = {
            'id': ('ID', {**PINLEFT, 'hide': True}),
            'value': ('Value', {**PINLEFT, 'editable': True}),
            'label': ('Label', {**PINLEFT,
                                'width': 80,
                                'editable': True,
                                'cellEditor': 'agSelectCellEditor',
                                'cellEditorParams': {
                                    'values': labels
                                }})
        }
        go = {
            'rowClassRules': {
                'row-selected': 'data.id === ' + str(result_rects.current_rect_index),
                'item-title': 'data.label === "item_title"',
                'item-question': 'data.label === "item_question"',
                'item-answer': 'data.label === "item_answer"',
                'item-right-answer': 'data.label === "item_right_answer"',
                'item-ignore': 'data.label === "item_ignore"'
            }
        }
        
        green_light = "#abf7b1"
        css = {
            '.row-selected': {
                'background-color': f'{green_light} !important'
            },
            '.item-title': {
                'background-color': '#A26EA1 !important' 
            },
            '.item-question': {
                'background-color': '#FEA5AD !important'  
            },
            '.item-answer': {
                'background-color': '#AFEEEE !important'  
            },
            '.item-right-answer': {
                'background-color': '#CBFFA9 !important'  
            },
            '.item-ignore': {
                'background-color': '#FDFDFD !important'  
            }
        }
        
        response = agstyler.draw_grid(
            df,
            formatter=formatter,
            fit_columns=True,
            pagination_size=25,
            grid_options=go,
            css=css
        )

        data = response['data'].values.tolist()

        for i, rect in enumerate(words):
            value = data[i][1]
            label = data[i][2]
            data_processor.update_rect_data(result_rects.rects_data, i, value, label)
            

    def group_annotations(self, model, result_rects):
        labels = model.labels
        with st.form(key="grouping_form"):
            if result_rects is not None:
                words = result_rects.rects_data['words']
                data = []
                for i, rect in enumerate(words):
                    group, label = rect['label'].split(":", 1) if ":" in rect['label'] else (None, rect['label'])
                    data.append({'id': i, 'value': rect['value'], 'label': label})
                df = pd.DataFrame(data)
                
                formatter = {
                    'id': ('ID', {**PINLEFT, 'width': 50}),
                    'value': ('Value', PINLEFT),
                    'label': ('Label', {**PINLEFT, 'hide': True,
                                'width': 80,
                                'editable': True,
                                'cellEditor': 'agSelectCellEditor',
                                'cellEditorParams': {
                                    'values': labels
                                }})
                }

                go = {
                    'rowClassRules': {
                        'row-selected': 'data.id === ' + str(result_rects.current_rect_index),
                        'item-title': 'data.label === "item_title"',
                        'item-question': 'data.label === "item_question"',
                        'item-answer': 'data.label === "item_answer"',
                        'item-right-answer': 'data.label === "item_right_answer"',
                        'item-ignore': 'data.label === "item_ignore"'
                    }
                }
                
                green_light = "#abf7b1"
                css = {
                    '.row-selected': {
                        'background-color': f'{green_light} !important'
                    },
                    '.item-title': {
                        'background-color': '#A26EA1 !important' 
                    },
                    '.item-question': {
                        'background-color': '#FEA5AD !important'  
                    },
                    '.item-answer': {
                        'background-color': '#AFEEEE !important'  
                    },
                    '.item-right-answer': {
                        'background-color': '#CBFFA9 !important'  
                    },
                    '.item-ignore': {
                        'background-color': '#FDFDFD !important'  
                    }
                }

                toolbar = st.empty()

                response = agstyler.draw_grid(
                    df,
                    formatter=formatter,
                    fit_columns=True,
                    selection='multiple',
                    use_checkbox='True',
                    pagination_size=25,
                    grid_options=go,
                    css=css,
                )
                
                rows = response['selected_rows']
                
                with toolbar:
                    submit = st.form_submit_button(model.save_text, type="primary")
                    if submit and len(rows) > 0:
                        # check if there are gaps in the selected rows
                        if len(rows) > 1:
                            for i in range(len(rows) - 1):
                                if rows[i]['id'] + 1 != rows[i + 1]['id']:
                                    st.error(model.selection_must_be_continuous)
                                    return

                        words = result_rects.rects_data['words']
                        new_words_list = []
                        coords = []
                        for row in rows:
                            word_value = words[row['id']]['value']
                            rect = words[row['id']]['rect']
                            coords.append(rect)
                            new_words_list.append(word_value)
                        # convert array to string
                        new_word = " ".join(new_words_list)

                        # Get min x1 value from coords array
                        x1_min = min([coord['x1'] for coord in coords])
                        y1_min = min([coord['y1'] for coord in coords])
                        x2_max = max([coord['x2'] for coord in coords])
                        y2_max = max([coord['y2'] for coord in coords])


                        words[rows[0]['id']]['value'] = new_word
                        words[rows[0]['id']]['rect'] = {
                            "x1": x1_min,
                            "y1": y1_min,
                            "x2": x2_max,
                            "y2": y2_max
                        }

                        # loop array in reverse order and remove selected entries
                        i = 0
                        for row in rows[::-1]:
                            if i == len(rows) - 1:
                                break
                            del words[row['id']]
                            i += 1

                        result_rects.rects_data['words'] = words

                        with open(model.get_rects_file()[model.get_index_select()], "w") as f:
                            json.dump(result_rects.rects_data, f, indent=2)
                        st.session_state[model.get_rects_file()[model.get_index_select()]] = result_rects.rects_data
                        model.set_data_result(result_rects.rects_data)
                        st.experimental_rerun()


    def convert_image_to_label_json(self, model, image_data):
        output_json = {}

        img = Image.open(image_data)
        img = np.asarray(img)
        image_height, image_width = img.shape[:2]
        orc_config = PaddleOCR(use_angle_cls=False, lang='en', rec=False)
        result = orc_config.ocr(img, cls=False)    
        words = []

        for output in result:
            for item in output:
                coordinates = item[0]
                text = item[1][0]

                if not text:
                    continue

                bounding_box = {
                    "x1": (coordinates[0][0] / image_width)  *1000,
                    "y1": (coordinates[1][1] / image_height) *1000,
                    "x2": (coordinates[2][0] / image_width)  *1000,
                    "y2": (coordinates[2][1] / image_height) *1000,
                }
                
                
                # id=1 | item_title
                # id=2 | item_question
                # id=3 | item_answer
                # id=4 | item_right_answer
                # id=5 | item_ignore
                # model.labels[]
                if "Cau" in text:
                    label = model.labels[2]
                    model.set_check(True)
                elif model.get_check() is None:
                    label = model.labels[1]
                elif model.get_check():
                    label = model.labels[3]
                    model.set_check(1)
                else:
                    label = model.labels[5]
                    
                word = {
                    "rect": bounding_box,
                    "value": text,
                    "label": label
                }

                words.append(word)

        output_json['meta'] = {
            "version": "v1.0",
            "split": "-",
            "image_id": 0,
            "image_size": {
                "width": image_width,
                "height": image_height
            }
        }
        output_json['words'] = words

        return output_json

                        
    def upload_file(self, model, uploaded_file):
        data_return = []
        for file in uploaded_file:
            if file is not None:
                file_name = file.name.split(".")[0]
                output_dir = os.path.join("assets", "data", "output")
                os.makedirs(output_dir, exist_ok=True)
                output_path_file = os.path.join(output_dir, f"{file_name}.json")
                output_json = self.convert_image_to_label_json(model, file)
                
                with open(output_path_file, "w") as f:
                    json.dump(output_json, f, indent=4)
                    data_return.append(output_json)
                    st.toast(f"Done {file_name}")
                    print("Done " + file_name)
                    model.set_rects_file(output_path_file)
                    
        return data_return

            # st.success("File uploaded successfully")
            
    
    def get_existing_file_names(self, uploaded_file):
        return uploaded_file.name.split(".")[0]
 
    
    def get_file_extension(self, uploaded_file):
        return uploaded_file.name.split(".")[-1]