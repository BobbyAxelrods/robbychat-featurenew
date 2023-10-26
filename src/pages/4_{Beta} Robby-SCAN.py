import os
import streamlit as st
import re
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar
import os
import streamlit as st
import pdf2image
from PIL import Image
import pytesseract
from pytesseract import Output, TesseractError
from modules.functions import PDFProcessor


st.set_page_config(layout="wide", page_icon="💬", page_title="Robby | Chat-Bot 🤖")

# Instantiate the main components
layout, sidebar, utils , process= Layout(), Sidebar(), Utilities(), PDFProcessor()

st.markdown(
    f"""
    <h1 style='text-align: center;'> BETA STAGE -- NEW FEATURE to summarize your scanned PDF/JPG/PNG ! 😁</h1>
    """,
    unsafe_allow_html=True,
)

languages = {
    'English': 'eng',
    'French': 'fra',
    'Arabic': 'ara',
    'Spanish': 'spa',
}


html_temp = """
            <div style="background-color:{};padding:1px">
            
            </div>
            """

user_api_key = utils.load_api_key()

sidebar.about()

if not user_api_key:
    layout.show_api_key_missing()

else:
    os.environ["OPENAI_API_KEY"] = user_api_key


# Start upload file logic 
st.title(":outbox_tray: Begin uploading your file to intitate ")

textOutput = st.selectbox(
    "Take note that your conversion will be stored in txt & in a variable",
    ('One text file (.txt)', 'Text file per page (ZIP)'))
ocr_box = st.checkbox('Enable OCR (scanned document)')

pdf_file = st.file_uploader("Upload your scanned pdf", type=['pdf','png','jpg'])

# allow css and html executed 

hide="""
<style>
footer{
	visibility: hidden;
    	position: relative;
}
.viewerBadge_container__1QSob{
  	visibility: hidden;
}
#MainMenu{
	visibility: hidden;
}
<style>
"""
st.markdown(hide, unsafe_allow_html=True)

# PDF process logic 

if pdf_file:
    # Read the path 
    path = pdf_file.read()
    # Get the file name extension to identify file types 
    file_extension = pdf_file.name.split(".")[-1]
    
    # Condition A (PDF)

    if file_extension == "pdf":
        
        #show documents uploaded 
        with st.expander("Display content "):
            process.displayPDF(path)
        # use other than OCR 
        if ocr_box:
            option = st.selectbox('Select your document language base', list(languages.keys()))
        if textOutput == 'One text file (.txt)':
            if ocr_box:
                texts,nbPages = process.images_to_txt(path, languages[option])
                totalPages = "Pages: "+str(nbPages)+" in total"
                text_data_f = "\n\n".join(texts)
            else:
                text_data_f, nbPages = process.convert_pdf_to_txt_file(path)
                totalPages = "Pages: "+str(nbPages)+" in total"
    
            extracted_text = "\n".join(text_data_f)
            st.info(totalPages)
            st.write(text_data_f)
            st.download_button("Download converted file for review", text_data_f)

            history = ChatHistory()
           

        #if required zip output 
        else:
            if ocr_box:
                text_data, nbPages = process.images_to_txt(path, languages[option])
                totalPages = "Pages: "+str(nbPages)+" in total"
            else:
                text_data, nbPages = process.convert_pdf_to_txt_pages(pdf_file)
                totalPages = "Pages: "+str(nbPages)+" in total"
            st.info(totalPages)
            zipPath = process.save_pages(text_data)
            # download text data   
            with open(zipPath, "rb") as fp:
                btn = st.download_button(
                    label="Download ZIP (txt)",
                    data=fp,
                    file_name="pdf_to_txt.zip",
                    mime="application/zip"
                )

# Condition B (Other than png or jpg)

    else:
        option = st.selectbox("What's the language of the text in the image?", list(languages.keys()))
        pil_image = Image.open(pdf_file)
        text = pytesseract.image_to_string(pil_image, lang=languages[option])
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("Display Image"):
                st.image(pdf_file)
        with col2:
            with st.expander("Display Text"):
                st.info(text)
        
        extracted_text = "\n".join(text)
        st.write(text)
        st.download_button("Download txt file", text)

    st.markdown('''
        <a target="_blank" style="color: black" href="">
            <button class="btn">
                Spread the word!
            </button>
        </a>
        <style>
        .btn{
            display: inline-flex;
            -moz-box-align: center;
            align-items: center;
            -moz-box-pack: center;
            justify-content: center;
            font-weight: 400;
            padding: 0.25rem 0.75rem;
            border-radius: 0.25rem;
            margin: 0px;
            line-height: 1.6;
            color: rgb(49, 51, 63);
            background-color: #fff;
            width: auto;
            user-select: none;
            border: 1px solid rgba(49, 51, 63, 0.2);
            }
        .btn:hover{
            color: #00acee;
            background-color: #fff;
            border: 1px solid #00acee;
        }
        </style>
        ''',
        unsafe_allow_html=True
        )                                       