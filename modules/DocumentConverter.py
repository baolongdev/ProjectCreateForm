import shutil
from docx2txt import process
from PIL import Image
import fitz
import os
import io


class DocumentConverter:
    def __init__(self):
        self.images = []
        self.output_dir = "./images"
        pass
            

    def convert_pdf_to_images(self, pdf_path, dpi=300):
        zoom = dpi / 72
        magnify = fitz.Matrix(zoom, zoom)
        self.images = []

        try:
            doc = fitz.open(stream=pdf_path, filetype="pdf")

            for count, page in enumerate(doc):
                page_number = count + 1
                pix = page.get_pixmap(matrix=magnify)
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                self.images.append([f"page_{count}",image])

            doc.close()
            return self.images

        except Exception as e:
            print(f"An error occurred: {str(e)}")
        