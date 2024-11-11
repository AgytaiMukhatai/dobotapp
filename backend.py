import requests
import io
from PIL import Image, ImageFilter
import svgwrite
import base64
from io import BytesIO

# Your Hugging Face API token and model URL
API_URL = "https://api-inference.huggingface.co/models/Shakker-Labs/FLUX.1-dev-LoRA-Children-Simple-Sketch"
headers = {"Authorization": "Bearer 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"}

# Define a function to make a request to the Hugging Face API
def query_huggingface(prompt):
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    
    # Check for JSON error response or return image bytes
    if response.headers["Content-Type"] == "application/json":
        return None, response.json()  # Return the error message if JSON
    return response.content, None  # Return image bytes if successful

# Function to convert PNG to SVGE
def png_to_svg(image_bytes, svg_path):
    # Open the PNG image from bytes
    image = Image.open(io.BytesIO(image_bytes))

    # Convert image to grayscale
    image = image.convert("L")  # "L" mode is for grayscale
    sketch_image = image.filter(ImageFilter.FIND_EDGES)  # Edge detection to create a sketch effect
    sketch_image = sketch_image.point(lambda x: 255 if x < 128 else 0)  # Convert to black and white

    # Get dimensions
    width, height = sketch_image.size

    # Create an SVG drawing
    dwg = svgwrite.Drawing(svg_path, profile='tiny', size=(width, height))
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Add the image to the SVG
    dwg.add(dwg.image(f"data:image/png;base64,{img_str}", insert=(0, 0), size=(width, height)))

    # Save the SVG file
    dwg.save()

    print(f"SVG saved as '{svg_path}'")

# Main script execution
if __name__ == "__main__":
    prompt = input("Enter your prompt for image generation: ")
    
    # Generate the image
    image_bytes, error = query_huggingface(prompt)
    
    if error:
        print(f"Error: {error.get('error', 'An unknown error occurred')}")
    elif image_bytes:
        # Display the generated image
        image = Image.open(io.BytesIO(image_bytes))
        image.show()  # This will open the image in the default image viewer

        # Convert the generated image to SVG
        svg_output_path = "output_image.svg"  # Specify the desired output path for SVG
        png_to_svg(image_bytes, svg_output_path)
    else:
        print("No image received from the API.")
