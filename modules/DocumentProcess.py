import os
from streamlit_sparrow_labeling import st_sparrow_labeling as st_labeling
from streamlit_sparrow_labeling import DataProcessor
from streamlit_javascript import st_javascript 
from streamlit_elements import elements, mui, html
from modules.agstyler import PINLEFT
from streamlit_elements import *
from modules import agstyler
from unidecode import unidecode
import streamlit as st
import pandas as pd
import numpy as np
import json
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
        
        def set_check(self, check):
            st.session_state['check'] = check

        def get_check(self):
            if 'check' not in st.session_state:
                return None
            return st.session_state['check']
        
    
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
            name_group = st.text_input("group name")
            warning_name_group = st.empty()
            with st.expander("Option"):
                language_select = st.selectbox(
                    "Select Language",
                    ("English", "Vietnamese"),
                )
                st.title("Google Form")
                st.checkbox('Activate quiz', True, key="quiz_toggle")
                st.checkbox('Activate required', True, key="required_toggle")
                st.checkbox('Activate shuffle', True, key="shuffle_toggle")
            with st.form("upload-form", clear_on_submit=True):
                uploaded_file = st.file_uploader(model.upload_button_text_desc, accept_multiple_files=True,
                                                 type=['png', 'jpg', 'jpeg', 'pdf'],
                                                 help=model.upload_help,
                                                 key="uploaded_file" 
                                                )
                submitted = st.form_submit_button(model.upload_button_text)
                
                
                if submitted and uploaded_file is not None:
                    if name_group is "":
                        with warning_name_group:
                            st.warning("Please enter your group name")
                        return
                    with st.spinner('Wait for it...'):
                        self.upload_file(model, uploaded_file, name_group, language_select)
                    
                    index = model.get_index_select()
                    model.set_image_file(model.get_uploaded_file_images()[index])
                    model.set_data_result(model.get_rects_file()[index])
            
        if model.get_image_file() is not None:
            docImg = model.get_image_file()
            data_processor = DataProcessor()
            saved_state = model.get_data_result()   
            with placeholder_show.container():
                assign_labels = st.checkbox(model.assign_labels_text, True, help=model.assign_labels_help)
                self.render_button(model, len(model.get_uploaded_file_images()))
                mode = "transform" if assign_labels else "rect"
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    result_rects = self.render_doc(model, docImg, saved_state, mode)
                with col2:
                    self.render_btn_createForm(model, createform)
                    self.render_form(model, result_rects, data_processor)
                    
    
    def render_form(self, model, result_rects, data_processor):
        with st.container():
            if result_rects is not None:
                with st.form(key="fields_form"):   
                    toolbar = st.empty()               
                    with toolbar:
                        t_submit, t_group, t_swap, t_delete, t_auto_Label = st.columns(5, gap="small")
                    with t_submit:
                        submit = st.form_submit_button(model.save_text, type="primary")
                    with t_group:
                        grouping = st.form_submit_button("Group", type="primary")
                    with t_swap:
                        swap = st.form_submit_button("Swap", type="primary")
                    with t_delete:
                        delete = st.form_submit_button("Delete", type="primary")
                    with t_auto_Label:
                        auto_Label = st.form_submit_button("Auto Label", type="primary")
                    
                    self.render_form_view(model, result_rects, data_processor, (submit, grouping, swap, delete, auto_Label))                      
                    
                    
                if len(result_rects.rects_data['words']) == 0:
                    st.toast(model.no_annotation_mapping)
                    return
                else:
                    with open(model.get_rects_file()[model.get_index_select()], 'rb') as file:
                        st.download_button(label=model.download_text,
                            data=file,
                            file_name="datafile.json",
                            mime='application/json',
                            help=model.download_hint
                        )
            
    
    def render_form_view(self, model, result_rects, data_processor, btn_group):
        labels = model.labels
        if result_rects is not None:
            words = result_rects.rects_data['words']
            data = [{'id': i, 'value': rect['value'], 'label': rect['label'].split(":", 1)[-1]} for i, rect in enumerate(words)]
            df = pd.DataFrame(data)
            formatter = {
                'id': ('ID', {**PINLEFT, 'width': 35}),
                'value': ('Value', {**PINLEFT, 'editable': True}),
                'label': ('Label', {**PINLEFT, 'width': 80, 'editable': True, 'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': labels}})
            }
            go = {
                'rowClassRules': {
                    'row-selected': f'data.id === {result_rects.current_rect_index}',
                    'item-title': 'data.label === "item_title"',
                    'item-question': 'data.label === "item_question"',
                    'item-answer': 'data.label === "item_answer"',
                    'item-right-answer': 'data.label === "item_right_answer"',
                    'item-ignore': 'data.label === "item_ignore"'
                }
            }
            red_light = "red"
            css = {
                '.row-selected': {'background-color': f'{red_light} !important'},
                '.item-title': {'background-color': '#A26EA1 !important'},
                '.item-question': {'background-color': '#FEA5AD !important'},
                '.item-answer': {'background-color': '#AFEEEE !important'},
                '.item-right-answer': {'background-color': '#CBFFA9 !important'},
                '.item-ignore': {'background-color': '#FDFDFD !important'}
            }
        
            response = agstyler.draw_grid(
                df,
                formatter=formatter,
                fit_columns=True,
                selection='multiple',
                use_checkbox='True',
                pagination_size=25,
                grid_options=go,
                css=css
            )
            submit, grouping, swap, delete, auto_Label = btn_group
            
            if submit:
                data = response['data'].values.tolist()
                for i, rect in enumerate(words):
                    value = data[i][1]
                    label = data[i][2]
                    result_rects.rects_data['words'][i]['value'] = value
                    result_rects.rects_data['words'][i]['label'] = label
            elif grouping:
                rows = response['selected_rows']
                if len(rows) > 1:
                    for i in range(len(rows) - 1):
                        if rows[i]['id'] + 1 != rows[i + 1]['id']:
                            st.error(model.selection_must_be_continuous)
                            return
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
            elif swap:
                rows = response['selected_rows']
                if len(rows) == 2:
                    index1 = rows[0]['id']
                    index2 = rows[1]['id']
                    words[index1]['value'], words[index2]['value'] = words[index2]['value'], words[index1]['value']
                    result_rects.rects_data['words'] = words
                else:
                    st.error("Please select exactly two words to swap.")     
            elif delete:
                rows = response['selected_rows']
                if len(rows) > 0:
                    selected_ids = set(row['id'] for row in rows)
                    words = [word for i, word in enumerate(words) if i not in selected_ids]
                    result_rects.rects_data['words'] = words
                else:
                    st.error("Please select at least one word to delete.")
            elif auto_Label:
                model.set_check(None)
                for item in words:
                    text = unidecode(item["value"]).lower()
                    if "cau" in text:
                        item["label"] = model.labels[2]
                        model.set_check(True)
                    elif model.get_check() is None:
                        item["label"] = model.labels[1]
                    elif model.get_check():
                        item["label"] = model.labels[3]
                        model.set_check(1)
                    else:
                        item["label"] = model.labels[5]
                    pass
                
                result_rects.rects_data['words'] = words
                # id=1 | item_title
                # id=2 | item_question
                # id=3 | item_answer
                # id=4 | item_right_answer
                # id=5 | item_ignore
                # model.labels[]
            
            if submit or grouping or swap or delete or auto_Label:
                for word in result_rects.rects_data['words']:
                    if len(word['value']) > 1000:
                        st.error(model.error_text)
                        return

                with open(model.get_rects_file()[model.get_index_select()], "w") as f:
                    json.dump(result_rects.rects_data, f)
        
                model.set_data_result(model.get_rects_file()[model.get_index_select()])
                st.experimental_rerun()
        
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
                    form_generator.setting_configure(
                        is_quiz=st.session_state.quiz_toggle,
                        is_required=st.session_state.required_toggle,
                        is_shuffle=st.session_state.shuffle_toggle,
                    )
                    with st.spinner("Wait for it..."):
                        form_generator.read_data_from_json(data)
                    with link_form:
                        st.markdown(f"Link form: [Link 😘]({form_generator.get_link_form()})" )
    
    
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
            
                        
                        