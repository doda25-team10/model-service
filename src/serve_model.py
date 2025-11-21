"""
Flask API of the SMS Spam detection model model.
"""
import argparse
import os
import joblib
from flask import Flask, jsonify, request
from flasgger import Swagger
import pandas as pd
import urllib.request

from text_preprocessing import prepare, _extract_message_len, _text_process

app = Flask(__name__)
swagger = Swagger(app)

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=8081)
args = parser.parse_args()


def find_model():
  model_path = 'output/model.joblib'

  if os.path.exists(model_path):
      print(f"Model found at {model_path}")
      return

  version = os.environ.get("MODEL_VERSION", "latest")
  if version == "latest":
      model_url = "https://github.com/doda25-team10/model-service/releases/latest/download/model.joblib"
  else:
      model_url = f"https://github.com/doda25-team10/model-service/releases/download/{version}/model.joblib"

  if not model_url:
      print("Error: Model missing and MODEL_DOWNLOAD_URL not set.")
      return

  print(f"Model not found. Downloading from {model_url}...")
  os.makedirs(os.path.dirname(model_path), exist_ok=True)
  try:
      urllib.request.urlretrieve(model_url, model_path)
      print("Download complete.")
  except Exception as e:
        print(f"Failed to download model: {e}")


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict whether an SMS is Spam.
    ---
    consumes:
      - application/json
    parameters:
        - name: input_data
          in: body
          description: message to be classified.
          required: True
          schema:
            type: object
            required: sms
            properties:
                sms:
                    type: string
                    example: This is an example of an SMS.
    responses:
      200:
        description: "The result of the classification: 'spam' or 'ham'."
    """
    input_data = request.get_json()
    sms = input_data.get('sms')
    processed_sms = prepare(sms)
    model = joblib.load('output/model.joblib')
    prediction = model.predict(processed_sms)[0]
    
    res = {
        "result": prediction,
        "classifier": "decision tree",
        "sms": sms
    }
    print(res)
    return jsonify(res)

if __name__ == '__main__':
    find_model()
    app.run(host="0.0.0.0", port=args.port, debug=True)