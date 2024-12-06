
Image Generator App

The Image Generator App is a web-based application that lets users generate images from text prompts using pre-trained machine learning models available on Hugging Face. The app is built with Streamlit (https://streamlit.io/) for an intuitive user interface and integrates Hugging Face APIs for image generation.

Features

- Input a custom text prompt.
- Select from various models:
  - Doodle Redmond: Hand-drawing style.
  - FLUX: Simple children's sketches.
  - Gesture Draw: Gesture-based art.
- Generate and view the resulting image directly in the app.



Requirements

To run the application, you need:
- Python: Version 3.7 or higher.
- Libraries:
  - streamlit>=1.0.0
  - requests>=2.25.1
  - pillow>=8.0.0



Installation

1. Clone the repository:
   
   git clone https://github.com/AgytaiMukhatai/dobotapp
   cd dobotapp.py
   

2. Create and activate a virtual environment:
   
   python -m venv venv
   source venv/bin/activate  #On Windows: venv\Scripts\activate
   

3. Install the required packages
   

4. Obtain a Hugging Face API token:
   - Create a Hugging Face account at https://huggingface.co.
   - Generate an API token under Account Settings > API Tokens.

5. Add your Hugging Face token to the script:
   - Open `dobotapp.py`.
   - Replace the `Authorization` header value with your token:
     	
     headers = {"Authorization": "Bearer YOUR_HUGGING_FACE_TOKEN"}
     


Usage

1. Run the app locally:
   
   streamlit run dobotapp.py
   

2. Open the app in your browser.

3. Interact with the interface:
   - Select a model.
   - Enter a text prompt.
   - View the generated image.



Example

- Input Prompt: `"A futuristic cityscape at sunset"`
- Selected Model: `Doodle Redmond`
- Output:
  (A hand-drawn style image of a futuristic cityscape)



Acknowledgments

- Powered by Streamlit (https://streamlit.io).
- Models hosted on Hugging Face (https://huggingface.co).
