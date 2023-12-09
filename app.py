import streamlit as st
import json
import os

# Function to load JSON data
def load_json(path):
    with open(path, 'r') as file:
        return json.load(file)

# Function to save JSON data
def save_json(data, path):
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)

def home_page(annotation_res_path):
    # Home page message
    st.title("Let's Annotate!")
    st.write("Please select a dataset to begin annotation.")

    st.session_state.model_selection = st.selectbox('Generated image dataset', models)
    if st.button('Begin Annotation'):
            st.session_state.model_selected = True
            print("Begin Annotation")
            st.rerun()
    
    st.write("You can return to this page at any time by clicking the 'Return home' button or refreshing the page. Your annotation progress will be saved.")

    if st.session_state.model_selection is not None:
        path = os.path.join(annotation_res_path, st.session_state.model_selection+'-res.json')
    else:
        path = os.path.join(annotation_res_path, '<chosen dataset>-res.json')
    st.write(f"View and download your annotation results in the path:")
    st.code(path, language='python')
    
    st.write("Once you are finished annotating, please upload your entire annotation results folder to the following Google Drive folder and rename it to 'annotation_res-<your_name>'.")
    st.code(annotation_res_path, language='python')
    st.link_button("Go to google drive folder", "https://drive.google.com/drive/folders/1nHC7DwReQnypWBM3lYR1QtPfXmZaSRRQ?usp=sharing")

    st.write("Thank you for you help!")
    st.write("written by: @emilyli")


# Load data
@st.cache_data
def load_cached_json(json_file_path):
    return load_json(json_file_path)

def reset():
    st.session_state.current_sample = 0
    st.session_state.model_selected = False
    st.session_state.model_selection = None
    st.session_state.annotation_finished = False


# Streamlit App for annotation
def annotate_app(model_annotation_res_path):
    # Check if all samples are annotated
    if st.session_state.current_sample >= len(data):
        st.session_state.annotation_finished = True
        st.write("Annotation finished")

        if st.button("Return home"):
            reset()
            st.rerun()
        return

    # Try to load annotation results
    if os.path.exists(model_annotation_res_path):
        annotation_res = load_json(model_annotation_res_path)
    else:
        annotation_res = {}

    # Print progress bar
    progress_status = f": {st.session_state.current_sample}/{len(data)} -> {st.session_state.current_sample/len(data)*100:.2f}%"
    progress_bar = st.progress(st.session_state.current_sample/len(data), text="Annotation in progress"+progress_status)

    # Display current sample
    current_key = list(data.keys())[st.session_state.current_sample]
    if current_key not in annotation_res:
        sample = data[current_key]

        # Display the data in sample
        st.subheader(f"Sample ID: {current_key}")
        st.image(os.path.join(root_path, sample['image_path']))
        st.subheader("Caption: " + sample['text'])

        # Score buttons
        score = st.radio("Rate the image:", range(1, 6))

        # Save annotation and go to next sample
        if st.button("Submit Rating", key="enter"):
            annotation_res[current_key] = score
            save_json(annotation_res, model_annotation_res_path)
            st.session_state.current_sample += 1
            st.rerun()

        if st.button("Return home"):
            reset()
            st.rerun()
    else:
        st.session_state.current_sample += 1
        st.rerun()


######## Main App ########
configs = load_cached_json("./configs.json")
root_path = configs['root_path']
results_folder_path = os.path.join(root_path, 'results/')
annotation_res_path = './annotation_res/'

# Get folders under results folder
models = os.listdir(results_folder_path) #e.g models = ['sdxl-turbo_wg', 'dalle3_wg']
models = [model for model in models if not model.startswith('.')] # remove hidden files


# Initialize session state variables
if 'current_sample' not in st.session_state:
    st.session_state.current_sample = 0
if 'model_selected' not in st.session_state:
    st.session_state.model_selected = False
if 'model_selection' not in st.session_state:
    st.session_state.model_selection = None
if 'annotation_finished' not in st.session_state:
    st.session_state.annotation_finished = False


if st.session_state.annotation_finished:
    st.write("Annotation process stopped. Your progress has been saved.")
    if st.button('Reset'):
        reset()
else:  # Annotation state
    if not st.session_state.model_selected: # Model selection screen
        home_page(annotation_res_path)
    else: # Annotation screen
        # Prepare save directory
        json_file_path = os.path.join(results_folder_path, st.session_state.model_selection)
        json_file_path = os.path.join(json_file_path, st.session_state.model_selection+'-metadata.json')
        data = load_cached_json(json_file_path=json_file_path)

        model_annotation_res_path = os.path.join(annotation_res_path, st.session_state.model_selection+'-res.json')
        # Create results directory if it doesn't exist
        if not os.path.exists(annotation_res_path):
            os.makedirs(annotation_res_path)
        annotate_app(model_annotation_res_path)