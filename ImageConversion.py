

# Import Statements
import os
import streamlit as st
import openai
import requests
from io import BytesIO
import timm
#img_link = "https://github.com/pytorch/hub/raw/master/images/dog.jpg" # Input image address here

st.title('The Artifier')

model = timm.create_model('tf_efficientnet_b0', pretrained = True)

model.eval()

import urllib
from PIL import Image
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform

config = resolve_data_config({}, model=model)
transform = create_transform(**config)

#user_input = st.text_input("Enter the url of an image")
uploaded_file = None
uploaded_file = st.file_uploader("Upload Files",type=['png','jpeg','jpg'])
if uploaded_file is not None:
    image_size = st.selectbox('Select an image size', ['256x256', '512x512', '1024x1024'])
    art_style = st.selectbox('Select an art style', ['Art Deco ', 'Crayon', 'Cubist', 'Impressionist', 'Japanese', 'Painted', 'Pop Art', 'Realism', 'Sketch', 'Watercolor'])
    state = st.button("Submit All")

    if state:
        img = Image.open(uploaded_file).convert('RGB')
        tensor = transform(img).unsqueeze(0) # transform and add batch dimension


        import torch
        with torch.no_grad():
            out = model(tensor)
        probabilities = torch.nn.functional.softmax(out[0], dim=0)
        print(probabilities.shape)
        # prints: torch.Size([1000])

        #To get the top-5 predictions class names:

        # Get imagenet class mappings
        url, filename = ("https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt", "imagenet_classes.txt")
        urllib.request.urlretrieve(url, filename)
        with open("imagenet_classes.txt", "r") as f:
            categories = [s.strip() for s in f.readlines()]

        # Print top categories per image
        top5_prob, top5_catid = torch.topk(probabilities, 5)
        for i in range(top5_prob.size(0)):
            print(categories[top5_catid[i]], top5_prob[i].item())
        # prints class names and probabilities like:
        # [('Samoyed', 0.6425196528434753), ('Pomeranian', 0.04062102362513542), ('keeshond', 0.03186424449086189), ('white wolf', 0.01739676296710968), ('Eskimo dog', 0.011717947199940681)]

        openai.api_key = "secret_val"
        response = openai.Image.create(
            prompt=art_style + categories[top5_catid[0]] + "Art" + "Painting",
            n=1,
            size= image_size
        )
        image_url = response['data'][0]['url']

        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))

        alt_url, alt_filename = (image_url, "new_image.jpg")
        urllib.request.urlretrieve(alt_url, alt_filename)
        st.image('new_image.jpg')
