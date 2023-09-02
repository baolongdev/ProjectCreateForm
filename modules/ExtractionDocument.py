from paddleocr import PaddleOCR
from paddleocr import PPStructure, save_structure_res
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from PIL import Image, ImageDraw
import streamlit as st
import numpy as np
import json
import os


class ExtractionDocument():
    def __init__(
        self,
        output="./output",
        group="",
        element="",
        ocr=False,
        table=False,
        recovery=False,
        image_orientation=False,
        lang='en',
    ):
        self.save_folder = output
        self.save_folder_group = group
        self.save_folder_element = element
        self.pathfile_result = os.path.join(self.save_folder, self.save_folder_group)
        self.datafile = {"words":[]}
        self.result = None
        self.image = None
        self.image_raw = None
        self.lang = lang
        if self.lang == "vi":
            self.detector_vietocr = self.load_vietocr()
        
        self.process = self.load_process(ocr, table, image_orientation)
                
        self.process_with_PaddleOCR = self.load_process_with_PaddleOCR(ocr, table, image_orientation)
        
    st.cache_data
    def load_vietocr(self):
        config_vietocr = Cfg.load_config_from_name('vgg_transformer')
        config_vietocr['cnn']['pretrained']=False
        config_vietocr['device'] = 'cpu'
        render = Predictor(config_vietocr)
        return render
    
    st.cache_data
    def load_process_with_PaddleOCR(self, ocr, table, image_orientation):
        render = PaddleOCR(
            show_log=False, 
            use_angle_cls=True,
            rec=False,
            use_gpu=False, 
            lang='en'
        )
        return render
    
    st.cache_data
    def load_process(self, ocr, table, image_orientation):
        render = PPStructure(
            show_log=False, 
            ocr=ocr, # Text
            table=table, # Table 
            image_orientation=image_orientation, # Image 
            recovery=True,
            lang='en'
        )
        return render
    
    
    def save_result(self):
        save_structure_res(self.result, self.pathfile_result, self.save_folder_element)
        self.image.save(os.path.join(self.pathfile_result, self.save_folder_element, "output_image.png"))
        

    def add_label(self, image_data=None):
        if type(image_data) != Image.Image:
            self.image = Image.open(image_data)
        else:
            self.image = image_data
        self.image_raw = self.image
        output_directory = os.path.join(self.pathfile_result, self.save_folder_element)
        os.makedirs(output_directory, exist_ok=True)
        self.image.save(os.path.join(output_directory, "raw.png"))
        self.image = np.asarray(self.image)
        self.result = self.process(self.image)
        self.read_result()
        self.convert_to_datafile()
        self.save_result()
        
    def add_label_with_PaddleOCR(self, image_data=None):
        if type(image_data) != Image.Image:
            self.image = Image.open(image_data)
        else:
            self.image = image_data
        self.image_raw = self.image
        output_directory = os.path.join(self.pathfile_result, self.save_folder_element)
        os.makedirs(output_directory, exist_ok=True)
        self.image.save(os.path.join(output_directory, "raw.png"))
        self.image = np.asarray(self.image)
        self.result = self.process_with_PaddleOCR.ocr(self.image, cls=True)
        self.read_result_with_PaddleOCR()
        self.image.save(os.path.join(self.pathfile_result, self.save_folder_element, "output_image.png"))
        
    def draw_bbox(self, bbox, color = "black"):
        if type(self.image) != Image.Image:
            self.image = Image.fromarray(self.image)
        draw = ImageDraw.Draw(self.image)
        x1, y1, x2, y2 = bbox
        expanded_bbox = [x1 - 3, y1 - 3, x2 + 3, y2 + 3]
        draw.rectangle(expanded_bbox, outline=color, width=3)
        
                
        
    def read_result(self) -> None:
        color = {
            "title": "red",
            "list": "green",
            "text": "yellow",
            "table": "blue",
            "figure": "orange",
        }

        for item in self.result:
            type = item["type"]
            bbox = item["bbox"]
            self.draw_bbox(bbox, color.get(type, "black"))  # Sử dụng màu mặc định nếu không xác định màu
            if type in ["text", "title", "list"]:
                self.read_result_child(item.get("res", []))
                
    def read_result_with_PaddleOCR(self) -> None:
        self.image = Image.fromarray(self.image)
        image_width, image_height = self.image.size
        self.datafile = {
            "meta": {
                "version": "v1.0",
                "split": "-",
                "image_id": 0,
                "image_size": {
                    "width": image_width,
                    "height": image_height
                }
            },   
        }
        words = []
        for items in self.result:
            for item in items:
                text_region = item[0]
                text = item[1][0]
                if not text:
                    continue
                bbox = self.convert_text_region_to_bbox(text_region)
                self.draw_bbox(bbox, "black")
                if self.lang == 'vi':
                    img_crop = self.crop_image(bbox)
                    text_vi = self.detector_vietocr.predict(img_crop)
                    text = text_vi
                word = {
                    "rect": {
                        "x1": int(bbox[0]),
                        "y1": int(bbox[1]),
                        "x2": int(bbox[2]),
                        "y2": int(bbox[3])
                    },
                    "value": text,
                    "label": "item_text"
                }
                words.append(word)
        self.datafile["words"] = words
        output_directory = os.path.join(self.pathfile_result, self.save_folder_element)
        os.makedirs(output_directory, exist_ok=True)
        with open(os.path.join(output_directory, "datafile.json"), 'w') as file:
            json.dump(self.datafile, file)
    
    def convert_to_datafile(self):
        image_width, image_height = self.image.size
        self.datafile = {
            "meta": {
                "version": "v1.0",
                "split": "-",
                "image_id": 0,
                "image_size": {
                    "width": image_width,
                    "height": image_height
                }
            },    
            "words":[]
        }
        for item in self.result:
            type = item["type"]
            bbox = item["bbox"]
            if type in ["text", "title", "list"]:
                for child in item["res"]:
                    if type in ["text", "list"]:
                        type = "text"
                    bbox = self.convert_text_region_to_bbox(child["text_region"])
                    self.datafile["words"].append(
                        {
                            "rect": {
                                "x1": int(bbox[0]),
                                "y1": int(bbox[1]),
                                "x2": int(bbox[2]),
                                "y2": int(bbox[3])
                            },
                            "value": child["text"],
                            "label": f"item_{type}",
                        }
                    )
            if type in ["table", "figure"]:
                if type == "table":
                    filename = f"{bbox}_0.xlsx"
                elif type == "figure":
                    filename = f"{bbox}_0.jpg"
                self.datafile["words"].append(
                    {
                        "rect": {
                            "x1": bbox[0],
                            "y1": bbox[1],
                            "x2": bbox[2],
                            "y2": bbox[3]
                        },
                        "value": type,
                        "label": f"item_{type}",
                        "link": os.path.join(self.pathfile_result, self.save_folder_element, filename),
                    }
                )
        output_directory = os.path.join(self.pathfile_result, self.save_folder_element)
        os.makedirs(output_directory, exist_ok=True)
        with open(os.path.join(output_directory, "datafile.json"), 'w') as file:
            json.dump(self.datafile, file)
             
    
    def convert_text_region_to_bbox(self, text_region):
        if len(text_region) >= 4:
            x_coords = [point[0] for point in text_region]
            y_coords = [point[1] for point in text_region]
            bbox = [
                min(x_coords),  # X của góc trái trên cùng
                min(y_coords),  # Y của góc trái trên cùng
                max(x_coords),  # X của góc dưới cùng bên phải
                max(y_coords)   # Y của góc dưới cùng bên phải
            ]
        else:
            bbox = [0, 0, 0, 0]  # Hoặc bạn có thể xác định một giá trị mặc định khác
        return bbox
    
    
    def crop_image(self, bbox):
        img = self.image
        cropped_img = img.crop(bbox)
        return cropped_img
        
    
    def read_result_child(self, data=None) -> None:
        color = {
            "title": "red",
            "list": "green",
            "text": "yellow",
            "table": "blue",
            "figure": "orange",
        }

        for item in data:
            bbox = self.convert_text_region_to_bbox(item["text_region"])
            self.draw_bbox(bbox, "black")  # Sử dụng màu mặc định nếu không xác định màu
            if self.lang == 'vi':
                img_crop = self.crop_image(bbox)
                text = self.detector_vietocr.predict(img_crop)
                item["text"] = text
    
    def get_data(self):
        _return = {
            "path": os.path.join(self.pathfile_result, self.save_folder_element),
            "image": self.image,
            "image_raw": self.image_raw,
            "datafile": os.path.join(self.pathfile_result, self.save_folder_element, "datafile.json"),
            "res_0": os.path.join(self.pathfile_result, self.save_folder_element, "res_0.txt"),
        }
        return _return


    def set_save_folder_group(self, group):
        self.save_folder_group = str(group)
        self.pathfile_result = os.path.join(self.save_folder, self.save_folder_group)
    def set_save_folder_element(self, element):
        self.save_folder_element = str(element)
        
# ExtractionDocument(
#     group="demo",
#     element="page_1",
#     lang="vi"
# ).add_label(image_data="main\paper-image.jpg")
# ExtractionDocument(lang="vi").add_label_with_PaddleOCR(image_data="page_1.png")