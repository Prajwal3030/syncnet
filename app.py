import logging
import os
import json
import subprocess
import tempfile
from flask import Flask, request, jsonify

# Logging configuration
format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

# Ignore warnings
import warnings
warnings.filterwarnings('ignore')

logger.info("[INFO] Importing required libraries...")

# Flask app setup
app = Flask(__name__)

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
tempfile.tempdir = '/tmp/processing/'
if not os.path.exists("/tmp/processing/"):
    os.makedirs("/tmp/processing/")

data_cloud = "gcp"

def get_cloud_storage_bucket(bucket_name):
    if data_cloud == "gcp":
        from google.cloud import storage
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
    return bucket

def download_from_cloud(bucket, src_file, tgt_file):
    if data_cloud == "gcp":
        blob = bucket.blob(src_file)
        blob.download_to_filename(tgt_file)
    logger.info("[INFO] Downloaded the content from {} to {}".format(src_file, tgt_file))

def upload_to_cloud(bucket, src_file, tgt_file):
    if data_cloud == "gcp":
        blob = bucket.blob(tgt_file)
        blob.upload_from_filename(src_file)
    logger.info("[INFO] Uploaded the content from {} to {}".format(src_file, tgt_file))

def input_fn(request_body, request_type="application/json"):
    try:
        logger.info("[INFO] Inside input function ...")
        json_obj = request_body
        if json_obj.get("verbose", True):
            logger.info("Input Json: {}".format(json_obj))
        json_obj["status"] = "success"
    except Exception as e:
        json_obj = {"status": "failed", "error": str(e)}
    return json_obj 

def model_fn(model_dir, checkpoint_path):
    pass

def predict_fn(input_obj):
    logger.info("Inside the predict function...")
    if input_obj["status"] == "failed":
        return input_obj

    curr_dir = tempfile.TemporaryDirectory(prefix="temp_")
    _, file_ext = os.path.splitext(input_obj["video_path"])
    bucket = get_cloud_storage_bucket(input_obj["bucket"])

    temp_file_path = os.path.join(curr_dir.name, 'temp_file{}'.format(file_ext))
    download_from_cloud(bucket, input_obj["video_path"], temp_file_path)
    
    # Replace the following lines with the execution of your scripts
    subprocess.run(["python", "run_pipeline.py", "--videofile", temp_file_path, "--reference", "wav2lip", "--data_dir", "/home/ubuntu/base/Repos/syncnet_python/tmp_dir"])
   
    subprocess.run(["python", "calculate_scores_real_videos.py", "--videofile", temp_file_path, "--reference", "wav2lip", "--data_dir", "/home/ubuntu/base/Repos/syncnet_python/tmp_dir"])

    # Assuming that the script outputs are captured and assigned to result
    # input_obj["script_output"] = result.stdout

    curr_dir.cleanup()
    return input_obj

def output_fn(pred_obj, request_type="application/json"):
    logger.info("[INFO] Inside the output function...")
    json_dump = json.dumps(pred_obj)
    return json_dump

@app.route("/")
def base():
    return jsonify("Healthy")

@app.route("/ping")
def ping():
    return jsonify("Healthy")

@app.route("/invocations", methods=['POST'])
def invocations():
    request_data = request.get_json()
    input_obj = input_fn(request_data)
    pred_obj = predict_fn(input_obj)
    response = output_fn(pred_obj)
    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)

# import logging

# format = "%(asctime)s: %(message)s"
# logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
# logger = logging
# logger.info("[INFO] Importing required libraries...")

# import warnings
# warnings.filterwarnings('ignore')

# import os
# import json
# import uvicorn

# import subprocess
# import tempfile

# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse

# logger.info("[INFO] Successfully imported required libraries!!")

# app = FastAPI()

# CURR_DIR = os.path.dirname(os.path.abspath(__file__))

# tempfile.tempdir = '/tmp/processing/'
# os.makedirs("/tmp/processing/", exist_ok=True)

# data_cloud="gcp"

# def get_cloud_storage_bucket(bucket_name):
#     if data_cloud=="gcp":
#         from google.cloud import storage
#         storage_client = storage.Client()
#         bucket = storage_client.bucket(bucket_name)
#     return bucket

# def download_from_cloud(bucket, src_file, tgt_file):
#     if data_cloud=="gcp":
#         blob = bucket.blob(src_file)
#         blob.download_to_filename(tgt_file)
#     logger.info("[INFO] Downloaded the content from {} to {}".format(src_file, tgt_file))

# def upload_to_cloud(bucket, src_file, tgt_file):
#     if data_cloud=="gcp":
#         blob = bucket.blob(tgt_file)
#         blob.upload_from_filename(src_file)
#     logger.info("[INFO] Uploaded the content from {} to {}".format(src_file, tgt_file))


# def input_fn(request_body, request_type="application/json"):
#     try:
#         logger.info("[INFO] Inside input function ...")
#         json_obj = request_body
#         # json_obj = json.loads(request_body)
#         if json_obj.get("verbose", True):
#             logger.info("Input Json: {}".format(json_obj))
#         json_obj["status"] = "success"
#     except Exception as e:
#         json_obj = {"status": "failed", "error": str(e)}
#     return json_obj 

# def model_fn(model_dir, checkpoint_path):
#     pass


# def predict_fn(input_obj):
#     logger.info("Inside the predict function...")
#     if input_obj["status"] == "failed":
#         return input_obj

#     curr_dir = tempfile.TemporaryDirectory(prefix="temp_")
#     _, file_ext = os.path.splitext(input_obj["video_path"])
#     bucket = get_cloud_storage_bucket(input_obj["bucket"])

#     temp_file_path = os.path.join(curr_dir.name, 'temp_file{}'.format(file_ext))
#     download_from_cloud(bucket, input_obj["video_path"], temp_file_path)
    
#     print( curr_dir.name)
#     # Replace the following lines with the execution of your scripts
#     subprocess.run(["python", "run_pipeline.py", "--videofile", temp_file_path, "--reference", "wav2lip", "--data_dir", "/home/ubuntu/base/Repos/syncnet_python/tmp_dir"])
#     print("################################################")
   
#     subprocess.run(["python", "calculate_scores_real_videos.py", "--videofile", temp_file_path, "--reference", "wav2lip", "--data_dir", "/home/ubuntu/base/Repos/syncnet_python/tmp_dir"])
#     print("################################################")
#     # print(result)
#     input_obj["script_output"] = result.stdout

#     curr_dir.cleanup()
#     return input_obj


# def output_fn(pred_obj, request_type="application/json"):
#     logger.info("[INFO] Inside the output function...")
#     json_dump = json.dumps(pred_obj)
#     return json_dump

# @app.get("/")
# async def base():
#     return JSONResponse(content="Healthy")

# @app.get("/ping")
# async def ping():
#     return JSONResponse(content="Healthy")
    
# @app.post("/invocations")
# async def invocations(request: Request):
#     request = await request.json()
#     input_obj = input_fn(request)
#     pred_obj = predict_fn(input_obj)
#     response = output_fn(pred_obj)
#     return response

# if __name__=='__main__':
#     # Specify the folder containing the videos

#     # input_json = {"bucket":"unai-videodata",
#     #               "video_path":"celebv_hq/video/--Jiv5iYqT8_0.mp4",
#     #               "upload_path":"celeb_vhq/clean_video/"}

#     # input_json = json.dumps(input_json)
#     uvicorn.run(app, host="0.0.0.0", port=8080)