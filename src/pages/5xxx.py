import os
import streamlit as st
import re
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar
from modules.functions import PDFProcessor
import sys
from io import StringIO
import os
import streamlit as st
from io import StringIO
import re
import sys
from modules.history import ChatHistory
from modules.layout import Layout
from modules.utils import Utilities
from modules.sidebar import Sidebar


st.set_page_config(layout="wide", page_icon="💬", page_title="Robby | Chat-Bot 🤖")

# Instantiate the main components
layout, sidebar, utils, process = Layout(), Sidebar(), Utilities(), PDFProcessor()

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
st.title(":outbox_tray: Begin uploading your file to initiate ")

textOutput = st.selectbox(
    "Take note that your conversion will be stored in txt & in a variable",
    ('One text file (.txt)', 'Text file per page (ZIP)')
)
ocr_box = st.checkbox('Enable OCR (scanned document)')

pdf_file = st.file_uploader("Upload your scanned pdf", type=['pdf', 'png', 'jpg'])

# ... (Rest of your code)

if pdf_file:
    # Read the path 
    path = pdf_file.read()
    # Get the file name extension to identify file types 
    file_extension = pdf_file.name.split(".")[-1]

    # Condition A (PDF)

    if file_extension == "pdf":

        # show documents uploaded 
        with st.expander("Display content "):
            process.displayPDF(path)
        # use other than OCR 
        if ocr_box:
            option = st.selectbox('Select your document language base', list(languages.keys()))
        if textOutput == 'One text file (.txt)':
            if ocr_box:
                texts, nbPages = process.images_to_txt(path, languages[option])
                totalPages = "Pages: " + str(nbPages) + " in total"
                text_data_f = "\n\n".join(texts)
            else:
                text_data_f, nbPages = process.convert_pdf_to_txt_file(path)
                totalPages = "Pages: " + str(nbPages) + " in total"

            extracted_text = "\n".join(text_data_f)
            st.info(totalPages)
            st.write(text_data_f)
            st.download_button("Download converted file for review", text_data_f)

            history = ChatHistory()

            if pdf_file:

                # Configure the sidebar
                sidebar.show_options()
                sidebar.about()

                # Initialize chat history
                history = ChatHistory()
                try:
                    chatbot = utils.setup_chatbot(
                        pdf_file, st.session_state["model"], st.session_state["temperature"]
                    )
                    st.session_state["chatbot"] = chatbot

                    if st.session_state["ready"]:
                        # Create containers for chat responses and user prompts
                        response_container, prompt_container = st.container(), st.container()

                        with prompt_container:
                            # Display the prompt form
                            is_ready, user_input = layout.prompt_form()

                            # Initialize the chat history
                            history.initialize(pdf_file)

                            # Reset the chat history if the button is clicked
                            if st.session_state["reset_chat"]:
                                history.reset(pdf_file)

                            if is_ready:
                                # Update the chat history and display the chat messages
                                history.append("user", user_input)

                                old_stdout = sys.stdout
                                sys.stdout = captured_output = StringIO()

                                output = st.session_state["chatbot"].conversational_chat(user_input)

                                sys.stdout = old_stdout

                                history.append("assistant", output)

                                # Clean up the agent's thoughts to remove unwanted characters
                                thoughts = captured_output.getvalue()
                                cleaned_thoughts = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', thoughts)
                                cleaned_thoughts = re.sub(r'\[1m>', '', cleaned_thoughts)

                                # Display the agent's thoughts
                                with st.expander("Display the agent's thoughts"):
                                    st.write(cleaned_thoughts)

                except Exception as e:
                    st.error(f"Error: {str(e)}")

