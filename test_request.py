import requests
import json

url = 'http://localhost:8080/invocations'
data = {
    "bucket": "unai-videodata",
    "video_path": "VFHQ/clipped_videos/Clip+--MJTR3evMw+P0+C0+F205-350_206clip.mp4",
}

response = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})
print(response.text)


