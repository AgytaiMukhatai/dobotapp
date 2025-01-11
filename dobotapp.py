import streamlit as st
import requests
import io
from PIL import Image
import serial




# Hugging Face API token
headers = {"Authorization": "Bearer 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"}

# Model URLs
model_urls = {
    "Doodle Redmond (Hand Drawing Style)": "https://api-inference.huggingface.co/models/artificialguybr/doodle-redmond-doodle-hand-drawing-style-lora-for-sd-xl",
    "FLUX (Children Simple Sketch)": "https://api-inference.huggingface.co/models/Shakker-Labs/FLUX.1-dev-LoRA-Children-Simple-Sketch",
    "Gesture Draw": "https://api-inference.huggingface.co/models/glif/Gesture-Draw"
}

# Streamlit App Layout
st.title("Image Generator App")
st.write("Choose a model and enter a text prompt to generate an image")

# Input for text prompt
prompt = st.text_input("Enter your prompt:", "Astronaut riding a horse")

# Define a function to make a request to the Hugging Face API
def query_huggingface(prompt, api_url):
    response = requests.post(api_url, headers=headers, json={"inputs": prompt})
    
    # Check for JSON error response or return image bytes
    if response.headers["Content-Type"] == "application/json":
        return None, response.json()  # Return the error message if JSON
    return response.content, None  # Return image bytes if successful

# Function to check if the robot is connected
def check_robot_connection(port):
    try:
        # Attempt to open a serial connection
        ser = serial.Serial(port, baudrate=115200, timeout=0.5)
        ser.close()  # If successful, close immediately
        return True
    except Exception as e:
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Robot connection check section
st.sidebar.header("Robot Connection")
robot_port = st.sidebar.text_input("Enter Robot Port:", "COM4")
if st.sidebar.button("Check Connection"):
    if check_robot_connection(robot_port):
        st.sidebar.success(f"✅ Robot is connected on {robot_port}")
    else:
        st.sidebar.error(f"❌ Failed to connect to the robot on {robot_port}")

# Streamlit App Layout
st.title("Dobot Draw Studio")
st.write("Choose whether to upload your own image or generate one using a model.")

# User choice: upload or generate
choice = st.radio("What would you like to do?", ["Upload an Image", "Generate an Image"])

if choice == "Upload an Image":
    # Image Upload Section
    st.header("Upload Your Image")
    uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        # Open and display the uploaded image
        uploaded_image = Image.open(uploaded_file)
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

        with open("uploaded_image.jpg", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        
        # "Draw" button for uploaded image
        if st.button("Draw Uploaded Image"):
            st.success("🎨 Sending uploaded image to the robot for drawing...")
            # Here you would add the logic to send the image to the robot.
    else:
        st.warning("Please upload an image file to view it here.")
else:
    # Image Generation Section
    st.header("Generate an Image")
    prompt = st.text_input("Enter your prompt:", "Astronaut riding a horse")

# Button for each model
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Generate with Doodle Redmond Model"):
        if prompt.strip() == "":  # Check if the input is empty
            st.warning("Please enter a prompt.")
        else:
            modified_prompt = f"{prompt}, sketched, outlined"
            image_bytes, error = query_huggingface(modified_prompt, model_urls["Doodle Redmond (Hand Drawing Style)"])
            
            if error:
                st.error(f"Error: {error.get('error', 'An unknown error occurred')}")
            elif image_bytes:
                image = Image.open(io.BytesIO(image_bytes))
                st.image(image, caption="Generated Image", use_column_width=True)
            else:
                st.warning("No image received from the API.")

with col2:
    if st.button("Generate with FLUX Model"):
        if prompt.strip() == "":  # Check if the input is empty
            st.warning("Please enter a prompt.")
        else:
            modified_prompt = f"{prompt}, sketched, outlined, grayscale, not-complicated"
            image_bytes, error = query_huggingface(modified_prompt, model_urls["FLUX (Children Simple Sketch)"])
            
            if error:
                st.error(f"Error: {error.get('error', 'An unknown error occurred')}")
            elif image_bytes:
                image = Image.open(io.BytesIO(image_bytes))
                st.image(image, caption="Generated Image", use_column_width=True)
            else:
                st.warning("No image received from the API.")

with col3:
    if st.button("Generate with Gesture Draw model"):
        if prompt.strip() == "":  # Check if the input is empty
            st.warning("Please enter a prompt.")
        else:
            modified_prompt = f"{prompt}, sketched"
            image_bytes, error = query_huggingface(modified_prompt, model_urls["Gesture Draw"])
            
            if error:
                st.error(f"Error: {error.get('error', 'An unknown error occurred')}")
            elif image_bytes:
                image = Image.open(io.BytesIO(image_bytes))
                st.image(image, caption="Generated Image", use_column_width=True)
            else:
                st.warning("No image received from the API.")
