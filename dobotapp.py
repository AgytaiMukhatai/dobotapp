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
import home
import circle
from lib.interface import Interface
from lib.dobot import Dobot 
import threading



st.set_page_config(
    page_title="Dobot Draw Studio",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Hugging Face API token

HF_TOKEN = os.getenv("HF_TOKEN")  # no default fallback

client = InferenceClient(
    provider="fal-ai",
    api_key=HF_TOKEN
)


# Query Hugging Face API for image generation
def query_huggingface(prompt, model_id, retries=3):
    modified_prompt = f"{prompt}, line drawing, simple sketch, black and white, minimalistic"
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
# Handle sending image to robot for drawing
def handle_drawing(coordinates, stop_event=None):
    try:
        if stop_event is not None and stop_event.is_set():
            print("[DRAW] Stop event set before drawing. Aborting.")
            return

        # Use the same port as the one used in "Check Connection"
        port = getattr(st.session_state, "robot_port", "/dev/tty.usbserial-0001")
        print(f"[DRAW] Starting drawing on port {port}")

        dobot = dobot_controller.DobotController(port)
        dobot.draw_paths(coordinates, stop_event=stop_event)

        print("[DRAW] Drawing finished.")

    except Exception as e:
        # This will show up in your terminal where you run `streamlit run`
        print(f"[DRAW ERROR] {e}")


    except Exception as e:
        st.error(f"An error occurred while processing the image: {e}")

def drawing_worker(coordinates, stop_event):
    try:
        handle_drawing(coordinates, stop_event)
    finally:
        stop_event.clear()
        # Signal completion with a simple flag
        st.session_state["drawing_done"] = True


# Main Streamlit app
def main():
    st.cache_data.clear()
    st.title("Dobot Draw Studio")
    st.write("Choose whether to upload your own image or generate one using a model.")
    
    # Initialize session state variables
    if 'bot' not in st.session_state:
        st.session_state.bot = None
    if 'dobot' not in st.session_state:
        st.session_state.dobot = None
    if 'emergency_stop' not in st.session_state:
        st.session_state.emergency_stop = False
    if 'drawing_thread' not in st.session_state:
        st.session_state.drawing_thread = None
    if 'stop_event' not in st.session_state:
        st.session_state.stop_event = threading.Event()

    
    with st.sidebar:
        # Emergency Stop Button - Prominent at the top
        st.markdown("### 🚨 Emergency Controls")
        if st.button("🛑 EMERGENCY STOP & HOME", 
                     key="emergency_stop_btn", 
                     type="primary",
                     use_container_width=True):
            try:
                # 1) Flip global flags
                st.session_state.emergency_stop = True

                if 'stop_event' in st.session_state and st.session_state.stop_event is not None:
                    st.session_state.stop_event.set()

                # 2) If we have a Dobot instance, call its low-level stop if available
                if st.session_state.dobot is not None:
                    try:
                        # Implement this in your Dobot class:
                        # - immediately stop all motors
                        # - clear buffer / queue
                        st.session_state.dobot.emergency_stop()
                    except AttributeError:
                        # If there's no emergency_stop() method yet, you can ignore this
                        pass

                # 3) Optionally move home AFTER stop is triggered
                if st.session_state.bot is None:
                    st.error("⚠️ Robot not connected! Please connect first.")
                else:
                    with st.spinner("Stopping all processes and returning to home..."):
                        home.move_to_home(st.session_state.bot)
                        st.success("✅ Emergency stop executed! Robot moved to home position.")

            except Exception as e:
                st.error(f"❌ Emergency stop failed: {e}")

        st.divider()
        
        st.header("Robot Connection")
        port = st.text_input("Enter the COM port for the robot (e.g., COM4):", "/dev/tty.usbserial-0001")
        
        if st.button("Check Connection", key="check_connection"):
            try:
                # Create or update bot connection
                st.session_state.robot_port = port
                st.session_state.bot = Interface(port)
                st.session_state.dobot = Dobot(port)
                
                if st.session_state.bot.connected():
                    st.success(f"Robot connected successfully on port {port}.")
                    st.session_state.emergency_stop = False  # Reset emergency stop on new connection
                else:
                    st.error(f"Failed to connect to the robot on port {port}. Please check the connection or port.")
                    st.session_state.bot = None
                    st.session_state.dobot = None
            except Exception as e:
                st.error(f"Connection error: {e}")
                st.session_state.bot = None
                st.session_state.dobot = None
        
        st.divider()
        
        # Robot Controls
        st.header("Robot Controls")
        
        # Move to Home button
        if st.button("Move to Home", key="move_to_home"):
            try:
                if st.session_state.bot is None:
                    st.warning("Please connect to the robot first using 'Check Connection'.")
                else:
                    home.move_to_home(st.session_state.bot)
                    st.success("Robot moved to home position successfully.")
            except Exception as e:
                st.error(f"Failed to move the robot to home position: {e}")
        
        st.divider()
        
    
    
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

            except Exception as e:
                st.error(f"Error handling uploaded image: {e}")
        
    else:
        # Image Generation Section
        st.header("Generate an Image")
        prompt = st.text_input("Enter your prompt:", "Cat with the balloon")

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
            if st.session_state.emergency_stop:
                st.warning("⚠️ Emergency stop active. Please reconnect the robot to reset.")
            else:
                # Prevent starting two drawings at once
                if (st.session_state.drawing_thread is not None and 
                    st.session_state.drawing_thread.is_alive()):
                    st.warning("A drawing is already in progress.")
                else:
                    # 1) Preprocess image -> coordinates (MAIN THREAD)
                    with st.spinner("Processing image to extract paths..."):
                        try:
                            coordinates = image_preprocessing.pipeline(
                                st.session_state["temp_image_path"], 
                                True
                            )
                        except Exception as e:
                            st.error(f"Error during image processing: {e}")
                            coordinates = None

                    if not coordinates:
                        st.error("Image preprocessing returned no coordinates.")
                    else:
                        st.write(f"Number of paths: {len(coordinates)}")

                        # 2) Show original image (MAIN THREAD)
                        st.image(
                            Image.open(st.session_state["temp_image_path"]),
                            caption="Original Image",
                            width="stretch"
                        )

                        # 3) Visualize paths (MAIN THREAD)
                        image_preprocessing.visualize_paths(coordinates)

                        # 4) Start background drawing thread (ROBOT ONLY)
                        st.session_state.stop_event.clear()
                        st.session_state.drawing_done = False
                        t = threading.Thread(
                            target=drawing_worker,
                            args=(coordinates, st.session_state.stop_event),
                            daemon=True,
                        )
                        t.start()
                        st.session_state.drawing_thread = t
                        st.success("🖊️ Drawing started in background.")
    else:
        st.info("Please upload or generate an image first to enable drawing.")

    

if __name__ == "__main__":
    main()