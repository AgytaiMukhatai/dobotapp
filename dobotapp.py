import streamlit as st
import requests
import io
from PIL import Image
import serial
import tempfile
import image_preprocessing
import time
import dobot_controller
from huggingface_hub import InferenceClient
import os


st.set_page_config(
    page_title="Dobot Draw Studio",
    layout="wide",  # Ensures the layout allows space for a sidebar
    initial_sidebar_state="expanded",  # Sidebar is expanded by default
)

# Hugging Face API token
headers = {"Authorization": "Bearer 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"}

client = InferenceClient(
    provider="fal-ai",
    api_key=os.environ.get("HF_TOKEN", "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")
)


# Query Hugging Face API for image generation
def query_huggingface(prompt, model_id, retries=3):
    modified_prompt = f"{prompt}, sketched, outlined"
    attempt = 0
    while attempt < retries:
        try:
            # Use the InferenceClient to generate image
            image = client.text_to_image(
                modified_prompt,
                model=model_id
            )
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue(), None
        except Exception as e:
            attempt += 1
            if attempt < retries:
                st.warning(f"Error occurred. Retrying... ({attempt}/{retries})")
                time.sleep(5)
            else:
                return None, {"error": str(e)}

# Model URLs with descriptions
model_urls = {
    "Doodle Redmond (Hand Drawing Style)": {
        "model_id": "artificialguybr/doodle-redmond-doodle-hand-drawing-style-lora-for-sd-xl",
        "description": "Generates sketched, hand-drawn style images."
    },
    "FLUX (Children Simple Sketch)": {
        "model_id": "Shakker-Labs/FLUX.1-dev-LoRA-Children-Simple-Sketch",
        "description": "Produces simple childlike sketches with playful themes."
    },
    "Gesture Draw": {
        "model_id": "glif/Gesture-Draw",
        "description": "Specializes in capturing dynamic gestures in drawings."
    }
}

# Save image to a temporary file
def save_image_to_tempfile(image_bytes):
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            with Image.open(io.BytesIO(image_bytes)) as img:
                img.save(temp_file.name)
            return temp_file.name
    except Exception as e:
        raise RuntimeError(f"Error saving image to temporary file: {e}")

# Process image through the pipeline
def process_image(temp_image_path):
    try:
        output_path = image_preprocessing.pipeline(temp_image_path, True)
        return output_path
    except Exception as e:
        raise RuntimeError(f"Error during image processing: {e}")

# Check robot connection
def check_robot_connection(port):
    try:
        ser = serial.Serial(port, baudrate=115200, timeout=0.5)
        ser.close()
        return True
    except Exception:
        return False

# Handle image generation and display
def handle_image_generation(prompt, model_name, model_id):
    if prompt.strip() == "":
        st.warning("Please enter a prompt.")
        return None

    image_bytes, error = query_huggingface(prompt, model_id)
    if error:
        st.error(f"Error: {error.get('error', 'An unknown error occurred')}")
        return None
    if not image_bytes:
        st.warning("No image received from the API.")
        return None

    try:
        temp_image_path = save_image_to_tempfile(image_bytes)
        st.image(Image.open(temp_image_path), caption=f"Generated Image ({model_name})", width="stretch")
        st.session_state["generated_image_path"] = temp_image_path
        return temp_image_path
    except Exception as e:
        st.error(f"Error saving image: {e}")
        return None

# Handle sending image to robot for drawing
def handle_drawing(temp_image_path):
    try:
        st.success("🎨 Sending image to the robot for drawing...")
        #print(f"Type of temp_image_path: {type(temp_image_path)}")  # Debugging line
        output_path = process_image(temp_image_path)
        st.image(Image.open(output_path), caption="Processed Image for Robot", width="stretch")
        # Ensure temp_image_path is a string (a single path), not a list
        if isinstance(temp_image_path, list):
            # Handle the case where temp_image_path is a list
            
            output_path = process_image(temp_image_path)
            st.image(Image.open(output_path), caption="Processed Image for Robot", use_container_width=True)
                # Send coordinates to the robot for each image if needed
            output_image = image_preprocessing.pipeline(output_path, False)
            print(output_image)
            if not output_image:
                raise ValueError("Image preprocessing returned empty data.")
            dobot = dobot_controller.DobotController("COM4")
            dobot.draw_paths([output_image])
        else:
            # Process a single image if temp_image_path is not a list
            output_path = process_image(temp_image_path)
            st.image(Image.open(output_path), caption="Processed Image for Robot", use_container_width=True)
            # Send coordinates to the robot if necessary
            output_image = image_preprocessing.pipeline(output_path, False)
            if not output_image:
                raise ValueError("Image preprocessing returned empty data.")
            dobot = dobot_controller.DobotController("COM4")
            dobot.draw_paths(output_image)

    except Exception as e:
        print(f"An error occurred while processing the image: {e}")

# Main Streamlit app
def main():
    st.title("Dobot Draw Studio")
    st.write("Choose whether to upload your own image or generate one using a model.")
    with st.sidebar:
        st.header("Robot Connection")
        port = st.text_input("Enter the COM port for the robot (e.g., COM4):", "COM4")
        
        if st.button("Check Connection", key="check_connection"):
            is_connected = check_robot_connection(port)
            if is_connected:
                st.success(f"Robot connected successfully on port {port}.")
            else:
                st.error(f"Failed to connect to the robot on port {port}. Please check the connection or port.")
    # User choice: upload or generate
    choice = st.radio("What would you like to do?", ["Upload an Image", "Generate an Image"])
    if "temp_image_path" not in st.session_state:
        st.session_state["temp_image_path"] = None
    # Upload Section
    if choice == "Upload an Image":
        st.header("Upload Your Image")
        uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "png", "jpeg"])
        if uploaded_file is not None:
            try:
                uploaded_image = Image.open(uploaded_file)
                st.image(uploaded_image, caption="Uploaded Image", width="stretch")

                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                    uploaded_image.save(temp_file.name)
                    temp_image_path = temp_file.name
                    st.session_state["temp_image_path"] = temp_image_path
                    #st.write(f"Uploaded image saved at: {temp_image_path}")


            except Exception as e:
                st.error(f"Error handling uploaded image: {e}")
        

    else:
        # Image Generation Section
        st.header("Generate an Image")
        prompt = st.text_input("Enter your prompt:", "Astronaut riding a horse")

        # Select model
        model_name = st.selectbox(
            "Select a model:",
            options=list(model_urls.keys()),
            format_func=lambda x: f"{x} - {model_urls[x]['description']}"
        )

        if st.button("Generate Image"):
            model_id = model_urls[model_name]["model_id"]
            
            temp_image_path = handle_image_generation(prompt, model_name, model_id)
            if temp_image_path:
                st.session_state["temp_image_path"] = temp_image_path
           
    if st.session_state["temp_image_path"]:
        if st.button("Process and Draw Image"):
            handle_drawing(st.session_state["temp_image_path"])
    else:
        st.info("Please upload or generate an image first to enable drawing.")
    

if __name__ == "__main__":
    main()
