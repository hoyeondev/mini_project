from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=""
)

result = CLIENT.infer("test2.jpg", model_id="note-defect-types/1")

print(result)