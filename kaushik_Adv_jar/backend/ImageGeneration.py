import asyncio
from json import dump
from random import randint
from PIL import Image  
import requests  
from dotenv import get_key  
import os
from time import sleep

# Define constants
DATA_FOLDER = os.path.abspath("Data\\Images")
DATA_FILE = os.path.abspath("kaushik_Adv_jar/Frontend/Files/ImageGeneration.data")
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceApiKey')}"}
print(f"[DEBUG] Headers: {headers}")


def open_images(prompt):
    """
    Open generated images from the Data folder based on the given prompt.
    """
    prompt = prompt.strip().replace(" ", "_").lower()  # Normalize prompt
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
    
    for jpg_file in files:
        image_path = os.path.join(DATA_FOLDER, jpg_file)
        
        try:
            img = Image.open(image_path)
            print(f"[INFO] Opening {image_path}")
            img.show()
            sleep(1)
        
        except FileNotFoundError:
            print(f"[ERROR] Could not find {image_path}")
        
        except IOError:
            print(f"[ERROR] Could not open {image_path}")


async def query(payload, headers):
    retries = 5  # Number of retry attempts
    delay = 2  # Delay in seconds between retries
    for attempt in range(retries):
        try:
            print(f"[DEBUG] Sending API request with payload: {payload}")
            response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
            response.raise_for_status()  # Ensure response status is 200
            print(f"[DEBUG] API response status: {response.status_code}")
            return response.content
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:  # Rate limit error
                print(f"[WARNING] Rate limited. Retrying in 2 seconds... (Attempt {attempt + 1}/{retries})")
                await asyncio.sleep(delay)# Wait before retrying
                delay *= 2  # Exponential backoff
            else:
                print(f"[ERROR] API call failed: {e}")
                break
        except Exception as e:
            print(f"[ERROR] Unexpected error during API call: {e}")
            break
    return None


async def generate_image(prompt: str):
    prompt = prompt.strip().replace(" ", "_").lower()
    print(f"[DEBUG] Generating images for prompt: {prompt}")

    tasks = []
    for i in range(3):
        payload = {
            "inputs": f"{prompt}, ultra-high quality, high resolution, seed={randint(1, 1000000)}"
        }
        print(f"[DEBUG] Payload for image {i+1}: {payload}")
        # Add delay between requests
        await asyncio.sleep(3)
        task = asyncio.create_task(query(payload, headers))
        tasks.append(task)
        


    image_bytes_list = await asyncio.gather(*tasks)
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            try:
                file_path = os.path.join(DATA_FOLDER, f"{prompt}{i + 1}.jpg")
                with open(file_path, "wb") as f:
                    f.write(image_bytes)
                print(f"[INFO] Image saved to {file_path}")
            except Exception as e:
                print(f"[ERROR] Failed to save image {i+1}: {e}")
        else:
            print(f"[ERROR] No data received for image {i+1}")
    missing_images = [i + 1 for i, image_bytes in enumerate(image_bytes_list) if image_bytes is None]
    if missing_images:
        print(f"[WARNING] The following images failed to generate: {missing_images}")




def generate_images(prompt: str):
    """
    Wrapper to run the asynchronous image generation and open the images.
    """
    asyncio.run(generate_image(prompt))
    open_images(prompt)

def GenerateImages(prompt: str):
    print(f"[DEBUG] GenerateImages called with prompt: {prompt}")
    asyncio.run(generate_image(prompt))
    open_images(prompt)


def main():
    """
    Main loop to monitor the ImageGeneration.data file and generate images based on its content.
    """
    while True:
        print("[DEBUG] Entering the while loop")
        try:
            with open(r"kaushik_Adv_jar\Frontend\Files\ImageGeneration.data", "r") as f:
                data = f.read().strip()
            print(f"[DEBUG] File content as lines: [{data}]")
                
            if data == F"False, False":
                print("[INFO] No new prompts. Exiting loop.")
                break  # Exit the loop when no new prompts
                
            prompt, status = data.split(",")
            print(f"[DEBUG] Processing line - Prompt: {prompt}, Status: {status.strip()}")
                
            if status.strip() == "True":
                print(f"[INFO] Generating Images for {prompt}")
                GenerateImages(prompt=prompt.strip())
                    
                with open(r"kaushik_Adv_jar\Frontend\Files\ImageGeneration.data", "w") as f:
                    f.write("False, False")
            else:
                sleep(1)
        except Exception as e:
            print(f"[ERROR] Exception in while loop: {e}")


if __name__ == "__main__":
    
    main()























# # import pyautogui
# # import time

# # print("Move your mouse to the desired location within 5 seconds...")
# # time.sleep(5)  # Wait for 5 seconds to allow you to move the mouse
# # x, y = pyautogui.position()  # Get the current mouse position
# # print(f"The coordinates are: ({x}, {y})")


# from googlesearch import search

# query = input("Enter your query: ")

# for i in search(query, tld="com", num=10, stop=10, pause=2):
#     print(i)