import streamlit as st
import requests
import io
from PIL import Image
import serial
import os
import subprocess


# Hugging Face API token
headers = {"Authorization": "Bearer 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"}

# Model URLs
model_urls = {
    "Doodle Redmond (Hand Drawing Style)": "https://api-inference.huggingface.co/models/artificialguybr/doodle-redmond-doodle-hand-drawing-style-lora-for-sd-xl",
    "FLUX (Children Simple Sketch)": "https://api-inference.huggingface.co/models/Shakker-Labs/FLUX.1-dev-LoRA-Children-Simple-Sketch",
    "Gesture Draw": "https://api-inference.huggingface.co/models/glif/Gesture-Draw"
}

# Define a function to make a request to the Hugging Face API
def query_huggingface(prompt, api_url):
    response = requests.post(api_url, headers=headers, json={"inputs": prompt})
    
    if response.headers["Content-Type"] == "application/json":
        return None, response.json()
    return response.content, None

# Function to check if the robot is connected
def check_robot_connection(port):
    try:
        ser = serial.Serial(port, baudrate=115200, timeout=0.5)
        ser.close()  
        return True
    except Exception as e:
        return False



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
        uploaded_image = Image.open(uploaded_file)
        st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)

        # Process the uploaded image
        with open("uploaded_image.jpg", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        

        # "Draw" button for uploaded image
        if st.button("Draw Uploaded Image"):
            st.success("🎨 Sending uploaded image to the robot for drawing...")
            # Here you would add the logic to send the processed paths to the robot.

    else:
        st.warning("Please upload an image file to view it here.")

else:
    # Image Generation Section
    st.header("Generate an Image")
    prompt = st.text_input("Enter your prompt:", "Astronaut riding a horse")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Generate with Doodle Redmond Model"):
            if prompt.strip() == "":
                st.warning("Please enter a prompt.")
            else:
                modified_prompt = f"{prompt}, sketched, outlined"
                image_bytes, error = query_huggingface(modified_prompt, model_urls["Doodle Redmond (Hand Drawing Style)"])
                
                if error:
                    st.error(f"Error: {error.get('error', 'An unknown error occurred')}")
                elif image_bytes:
                    generated_image = Image.open(io.BytesIO(image_bytes))
                    st.image(generated_image, caption="Generated Image", use_container_width=True)

                    # Process the generated image
                    with open("generated_image.jpg", "wb") as f:
                        f.write(image_bytes)

                    

                    # "Draw" button for generated image
                    if st.button("Draw Generated Image (Doodle Redmond)", key="draw_doodle_redmond"):
                        st.success("🎨 Sending generated image to the robot for drawing...")
                        # Here you would add the logic to send the processed paths to the robot.
                else:
                    st.warning("No image received from the API.")

    with col2:
        if st.button("Generate with FLUX Model"):
            if prompt.strip() == "":
                st.warning("Please enter a prompt.")
            else:
                modified_prompt = f"{prompt}, sketched, outlined, grayscale, not-complicated"
                image_bytes, error = query_huggingface(modified_prompt, model_urls["FLUX (Children Simple Sketch)"])
                
                if error:
                    st.error(f"Error: {error.get('error', 'An unknown error occurred')}")
                elif image_bytes:
                    generated_image = Image.open(io.BytesIO(image_bytes))
                    st.image(generated_image, caption="Generated Image", use_container_width=True)

                    # Process the generated image
                    with open("generated_image.jpg", "wb") as f:
                        f.write(image_bytes)

                    

                    # "Draw" button for generated image
                    if st.button("Draw Generated Image (FLUX)", key="draw_flux"):
                        st.success("🎨 Sending generated image to the robot for drawing...")
                        # Here you would add the logic to send the processed paths to the robot.
                else:
                    st.warning("No image received from the API.")

    with col3:
        if st.button("Generate with Gesture Draw model"):
            if prompt.strip() == "":
                st.warning("Please enter a prompt.")
            else:
                modified_prompt = f"{prompt}, sketched"
                image_bytes, error = query_huggingface(modified_prompt, model_urls["Gesture Draw"])
                
                if error:
                    st.error(f"Error: {error.get('error', 'An unknown error occurred')}")
                elif image_bytes:
                    generated_image = Image.open(io.BytesIO(image_bytes))
                    st.image(generated_image, caption="Generated Image", use_container_width=True)

                    # Process the generated image
                    with open("generated_image.jpg", "wb") as f:
                        f.write(image_bytes)

                    

                    # "Draw" button for generated image
                    if st.button("Draw Generated Image (Gesture Draw)", key="draw_gesture"):
                        st.success("🎨 Sending generated image to the robot for drawing...")
                        # Here you would add the logic to send the processed paths to the robot.
                else:
                    st.warning("No image received from the API.")
