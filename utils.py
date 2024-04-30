import os
import base64

from PIL import Image
from moviepy.editor import VideoFileClip
import requests

def get_video_info_and_shortlink(video_url, filepath):
    info_url = "https://autocompressor.net/videoinfo"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://autocompressor.net",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    data = {"url": video_url}
    response = requests.post(info_url, headers=headers, json=data)
    info_json = response.json()

    width = info_json["info"]["width"]
    height = info_json["info"]["height"]

    shortlink_url = "https://autocompressor.net/av1/mkshortlink"
    data["w"] = width
    data["h"] = height
    data["v"] = video_url
    data["i"] = create_and_upload_thumbnail(filepath)
    response = requests.post(shortlink_url, headers=headers, json=data)
    shortlink_json = response.json()

    return "https://autocompressor.net/av1?s=" + shortlink_json["shortLink"]

def create_and_upload_thumbnail(video_path):
    clip = VideoFileClip(video_path)
    frame = clip.get_frame(clip.duration / 2.0)
    image = Image.fromarray(frame)
    image_path = "thumbnail.jpg"
    image.save(image_path)
    url = "https://api.imgbb.com/1/upload"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    data = {
        "key": "124cef37f31c614b7b3d3040cce3b09a",
        "image": encoded_string
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        json_response = response.json()
        image_url = json_response["data"]["url"]
        os.remove(image_path)
        return image_url
    else:
        os.remove(image_path)
        return "Error: " + response.text
