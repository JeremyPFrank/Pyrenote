import argparse
import os
import sys
import requests
import json
import wave
import mutagen
from pathlib import Path

parser = argparse.ArgumentParser(description="Upload sample data to project")

parser.add_argument(
    "--username",
    type=str,
    help="Username to which this data will be assigned for annotation",
    required=True,
)
parser.add_argument(
    "--audio_file",
    type=str,
    help="Path to audio file which is to be annotated (wav, mp3, ogg only)",
    default=False,
)
parser.add_argument("--host", type=str, help="Host of service", default=None)
parser.add_argument(
    "--is_marked_for_review",
    type=bool,
    help="Whether datapoint should be marked for review",
    default=False,
)
parser.add_argument(
    "--segmentations",
    type=str,
    help="List of segmentations for the audio",
    default=[],
)
parser.add_argument("--port", type=int, help="Port to make request to",
                    default=80)

parser.add_argument("--api_key", type=str, help="Port to make request to",
                    default=80)

args = parser.parse_args()

api_key = args.api_key
headers = {"Authorization": api_key}

directory = os.path.normcase(args.audio_file)
for filename in os.listdir(directory):
    print(os.path.join(directory, filename))
    audio_path = Path(os.path.join(directory, filename))
    # audio_path = os.path.join(directory, filename)
    audio_filename = audio_path.name
    if audio_path.is_file():
        audio_obj = open(audio_path.resolve(), "rb")
    else:
        print("Audio file does not exist")
        continue

    metadata = mutagen.File(audio_path.as_posix()).info
    frame_rate = metadata.sample_rate
    clip_duration = metadata.length

    username = args.username.split('.')
    print(username)
    username_dict = {}
    is_marked_for_review = args.is_marked_for_review
    segmentations = args.segmentations

    file = {"audio_file": (audio_filename, audio_obj)}

    values = {
        "username": username,
        "segmentations": segmentations,
        "is_marked_for_review": is_marked_for_review,
        "sampling_rate": frame_rate,
        "clip_length": clip_duration,
    }

    print("Creating datapoint")
    response = requests.post(
        f"http://{args.host}:{args.port}/api/data", files=file, data=values,
        headers=headers
    )

    if response.status_code == 201:
        response_json = response.json()
        print(f"Message: {response_json['message']}")
    else:
        print(f"Error Code: {response.status_code}")
        response_json = response.json()
        print(f"Message: {response_json['message']}")
        print(response_json)
