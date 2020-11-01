import os
import sys
import requests
import json
import random
import matplotlib.pyplot as plt
from PIL import Image,ImageDraw
from io import BytesIO
try:
    with open('logincred.json','r') as f:
        credentials = json.loads(f.read())
        COMPUTER_VISION_SUBSCRIPTION_KEY = credentials['COMPUTER_VISION_SUBSCRIPTION_KEY'] 
        COMPUTER_VISION_ENDPOINT = credentials['COMPUTER_VISION_ENDPOINT']
except FileNotFoundError:
    print("logincred.json doesnt exist...")
    print("create a file with azure object detection credentials")
    print("format: {COMPUTER_VISION_SUBSCRIPTION_KEY\":\"value\",\"COMPUTER_VISION_ENDPOINT\":\"value\"}")
    exit()
# Add your Computer Vision subscription key and endpoint to your environment variables.

subscription_key = COMPUTER_VISION_SUBSCRIPTION_KEY
endpoint = COMPUTER_VISION_ENDPOINT

analyze_url = endpoint + "vision/v3.1/analyze"

# Set image_path to the local path of an image that you want to analyze.
# Sample images are here, if needed:
# https://github.com/Azure-Samples/cognitive-services-sample-data-files/tree/master/ComputerVision/Images
if len(sys.argv) > 1:
    image_path = sys.argv[1]
else:
    raise Exception("Wrong number of arguments.")

# Read the image into a byte array
image_data = open(image_path, "rb").read()
headers = {'Ocp-Apim-Subscription-Key': subscription_key,
           'Content-Type': 'application/octet-stream'}
params = {'visualFeatures': 'Categories,Description,Color,Objects'}
response = requests.post(
    analyze_url, headers=headers, params=params, data=image_data)
response.raise_for_status()

# The 'analysis' object contains various fields that describe the image. The most
# relevant caption for the image is obtained from the 'description' property.
analysis = response.json()
# jsoutput = json.dumps(analysis)
# with open('output.json','w') as jsonfile:
#     jsonfile.write(jsoutput)
image_caption = analysis["description"]["captions"][0]["text"].capitalize()


def color_generator():
    color = []
    for i in range(3):
        color.append(random.randint(0,255))
    return tuple(color)

loaded_json = analysis.copy()
objects = loaded_json['objects']
person_rectangles = []
for i in objects:
    if i['object'] == 'person':
        person_rectangles.append(i['rectangle'])
im = Image.open(image_path) #opening sample picture
draw_im = ImageDraw.Draw(im)
all_coords = []
for i in person_rectangles:
    print(i)
    x0 = i['x']
    y0 = i['y']
    x1 = x0 + i['w']
    y1 = y0 + i['h']
    coords = [x0,y0,x1,y1]
    all_coords.append(coords)
    draw_im.rectangle(coords,outline=color_generator(),width=2)
output = {"people":all_coords}
writejson = json.dumps(output)
with open(image_path.split('.')[0] + '.json','w') as f:
    f.write(writejson)
im.show()