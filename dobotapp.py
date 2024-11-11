import streamlit as st
import requests
import io
from PIL import Image
import svgwrite
import base64
from io import BytesIO

# Hugging Face API token
headers = {"Authorization": "Bearer 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"}

# Model URLs
model_urls = {
    "Doodle Redmond (Hand Drawing Style)": "https://api-inference.huggingface.co/models/artificialguybr/doodle-redmond-doodle-hand-drawing-style-lora-for-sd-xl",
    "FLUX (Children Simple Sketch)": "https://api-inference.huggingface.co/models/Shakker-Labs/FLUX.1-dev-LoRA-Children-Simple-Sketch",
    "Gesture Draw" : "https://api-inference.huggingface.co/models/glif/Gesture-Draw"
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

# Function to convert PNG to SVG
def png_to_svg(image_bytes):
    # Open the PNG image from bytes
    image = Image.open(io.BytesIO(image_bytes))
    width, height = image.size

    # Create an SVG drawing
    dwg = svgwrite.Drawing("output_image.svg", profile='tiny', size=(width, height))

    # Convert the image to base64 to embed in SVG
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Add the image to the SVG
    dwg.add(dwg.image(f"data:image/png;base64,{img_str}", insert=(0, 0), size=(width, height)))

    # Save the SVG file
    dwg.save()

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
                png_to_svg(image_bytes)
                st.success("Image converted to SVG and saved as 'output_image.svg'.")
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
                png_to_svg(image_bytes)
                st.success("Image converted to SVG and saved as 'output_image.svg'.")
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
                png_to_svg(image_bytes)
                st.success("Image converted to SVG and saved as 'output_image.svg'.")
            else:
                st.warning("No image received from the API.")