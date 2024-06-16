# -*- coding: utf-8 -*-
"""
Created on Wed May 17 19:15:49 2023

@author: marca
"""

import os
import chardet
import pandas as pd
from docx import Document
from pdfminer.high_level import extract_text
from PIL import Image, ImageFile
import pytesseract
import tiktoken
from pdfminer.high_level import extract_text_to_fp
from pdfminer.pdfpage import PDFPage
from pypdf import PdfReader
import fitz
import io
import re




class Ingester:
    
    
    def __init__(self):
        
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        self.chunks = []
        self.full_text = """"""
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        ImageFile.LOAD_TRUNCATED_IMAGES = True

    def _count_tokens(self, text):
        tokens = len(self.encoding.encode(text))
        return tokens

    def _process_table_file(self, file_path):
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == ".csv":
            file_name, df = self.read_csv_file(file_path)
        elif file_ext == ".xlsx":
            file_name, df = self.read_xlsx_file(file_path)
        else:
            raise ValueError(
                "Unsupported file extension. Please provide a CSV or XLSX file."
            )

        if df is None:
            return None

        plain_csv_text = df.to_csv(index=False)
        rows = plain_csv_text.split("\n")

        chunk_tokens = 0
        chunks = []
        chunk = ""

        for row in rows:
            row_tokens = self.count_tokens(row)
            chunk_tokens += row_tokens

            if chunk_tokens >= 1000:
                chunks.append(chunk)
                chunk = ""
                chunk_tokens = row_tokens

            chunk += "\n" + row

        # Add the remaining chunk, if any
        if chunk:
            chunks.append(chunk)

        chunks = [f"{file_name}\n{chunk}" for chunk in chunks]

        return chunks
    
    def ingest(self, file_path):
        extension = file_path.split(".")[-1].lower()
        if extension == "pdf":
            text = self._read_pdf(file_path)
        elif extension in ["doc", "docx"]:
            text = self._read_docx(file_path)
        elif extension in ["csv", "xlsx"]:
            return self._process_table_file(file_path)
        elif extension == "txt":
            text = self._read_txt(file_path)
        elif extension in ["jpg", "jpeg", "png", "bmp", "tiff"]:
            text = self._ocr_read_image(file_path)
        else:
            print(f"Unsupported file type: {extension}")
            return ""
    
        chunks = self._chunk_text(text)
        
        self.chunks.extend(chunks)
        
        return chunks

    
    def ingest_pages(self, file_path):
        extension = file_path.split(".")[-1].lower()
        if extension == "pdf":
            text_array = self.extract_text_to_pages(file_path)
            print(len(text_array))
            
        elif extension in ["doc", "docx"]:
            text = self._read_docx(file_path)
        elif extension in ["csv", "xlsx"]:
            return self._process_table_file(file_path)
        elif extension == "txt":
            text = self._read_txt(file_path)
        elif extension in ["jpg", "jpeg", "png", "bmp", "tiff"]:
            text = self._ocr_read_image(file_path)
        else:
            print(f"Unsupported file type: {extension}")
            return ""
        if extension == "pdf":
            chunks = text_array
        else:
            chunks = self._chunk_text(text)
        
        self.chunks = chunks
        
        return chunks
    
    def vomit(self):
        
        vomit_chunks = self.chunks.copy()
        
        self.chunks = []
        
        return vomit_chunks
    
    def vomit_whole(self):
        
        vomit = self.full_text
        
        self.full_text = []
        
        return vomit


    def _chunk_text(self, text, chunk_size=1000):
        words = text.split()
        chunks = []
        current_chunk = ""

        for word in words:
            # Check if adding the word to the current chunk would exceed the chunk size
            if len(current_chunk) + len(word) + 1 > chunk_size:
                # If so, add the current chunk to the chunks list and start a new chunk with the current word
                chunks.append(current_chunk.strip())
                current_chunk = word
            else:
                # Otherwise, add the word to the current chunk
                current_chunk += f" {word}"

        # Add the last chunk to the chunks list
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _ocr_read_image(self, image_path):
        # Check if the file exists
        if not os.path.exists(image_path):
            raise ValueError("The file does not exist.")

        # Check if the file has a supported image extension
        supported_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext not in supported_extensions:
            raise ValueError(
                "Unsupported file extension. Please provide a supported image file."
            )

        # Open the image file
        image = Image.open(image_path)

        # Perform OCR on the image
        text = pytesseract.image_to_string(image)

        return text

    def _read_pdf(self, file_path):
        try:
            text = extract_text(file_path)
        except Exception as e:
            print(f"Error reading PDF file {file_path}: {str(e)}")
            text = ""
        return text
    
    
    def extract_text_to_pages(self, pdf_file_path):
        pages = []
        # Open the PDF file using PyPDF
        reader = PdfReader(pdf_file_path)
        # Iterate through each page and extract text
        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            page_text = page_text.replace('\n', ' ').replace('\r', ' ').strip() if page_text else ""
            #print(f"Page {page_number}: {page_text[:100]}...")  # Print the first 100 characters for debugging
            if page_text:
                pages.append(page_text)
        return pages
    
    def pdf_to_dataframe(self, pdf_file_path):
        pages = self.extract_text_to_pages(pdf_file_path)
        data = {
            'page_number': list(range(1, len(pages) + 1)),
            'page_chapter': [''] * len(pages),
            'page_text': pages,
            'page_wordcount': [0] * len(pages)
        }
        df = pd.DataFrame(data)
        return df

    def _read_docx(self, file_path):
        try:
            doc = Document(file_path)
            text = " ".join([p.text for p in doc.paragraphs])
        except Exception as e:
            print(f"Error reading DOCX file {file_path}: {str(e)}")
            text = ""
        return text

    def _read_xlsx_file(self, file_path):
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            print(f"Error reading XLSX file {file_path}: {str(e)}")
            df = None

        file_name = os.path.basename(file_path)
        return file_name, df

    def _read_csv_file(self, file_path):
        try:
            with open(file_path, "rb") as f:
                encoding = chardet.detect(f.read())["encoding"]
            df = pd.read_csv(file_path, encoding=encoding)
        except Exception as e:
            print(f"Error reading CSV file {file_path}: {str(e)}")
            df = None

        file_name = os.path.basename(file_path)
        return file_name, df

    def _read_txt(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading TXT file {file_path}: {str(e)}")
            text = ""
        return text
    

# =============================================================================
# ingester = Ingester()
# 
# ingester.extract_text_to_pages(r"C:\Users\marca\Desktop\Coding\AI\Librarian\gpt_workspace\Bryant_R__O_39_Hallaron_D_-_Computer_Systems_A_Programmer_39_s_Perspective_-_2010.pdf")
# 
# =============================================================================
