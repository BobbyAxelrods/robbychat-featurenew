import streamlit as st
from zipfile import ZipFile
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import base64
#------- OCR ------------
import pdf2image
import pytesseract
from pytesseract import Output, TesseractError

class PDFProcessor:
    def __init__(self):
        pass

    @st.cache_data
    def images_to_txt(_self, path, language):
        images = pdf2image.convert_from_bytes(path)
        all_text = []
        for i, page in enumerate(images):
            text = pytesseract.image_to_string(page, lang=language)
            all_text.append(text)
        return all_text, len(all_text)

    @st.cache_data
    def convert_pdf_to_txt_pages(_self, path):
        texts = []
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        # fp = open(path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        size = 0
        c = 0
        file_pages = PDFPage.get_pages(path)
        nbPages = len(list(file_pages))
        for page in PDFPage.get_pages(path):
            interpreter.process_page(page)
            t = retstr.getvalue()
            if c == 0:
                texts.append(t)
            else:
                texts.append(t[size:])
            c = c + 1
            size = len(t)
        # text = retstr.getvalue()

        # fp.close()
        device.close()
        retstr.close()
        return texts, nbPages

    @st.cache_data
    def convert_pdf_to_txt_file(_self, path):
        texts = []
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        # fp = open(path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        file_pages = PDFPage.get_pages(path)
        nbPages = len(list(file_pages))
        for page in PDFPage.get_pages(path):
            interpreter.process_page(page)
            t = retstr.getvalue()
        # text = retstr.getvalue()

        # fp.close()
        device.close()
        retstr.close()
        return t, nbPages

    @st.cache_data
    def save_pages(self, pages):
        files = []
        for page in range(len(pages)):
            filename = "page_" + str(page) + ".txt"
            with open("./file_pages/" + filename, 'w', encoding="utf-8") as file:
                file.write(pages[page])
                files.append(file.name)

        # create zipfile object
        zipPath = './file_pages/pdf_to_txt.zip'
        zipObj = ZipFile(zipPath, 'w')
        for f in files:
            zipObj.write(f)
        zipObj.close()

        return zipPath

    def displayPDF(_self, file):
        # Opening file from file path
        # with open(file, "rb") as f:
        base64_pdf = base64.b64encode(file).decode('utf-8')

        # Embedding PDF in HTML
        pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        # Displaying File
        st.markdown(pdf_display, unsafe_allow_html=True)
