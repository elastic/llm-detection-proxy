import os
import openai
from flask import Flask, request, jsonify
from openai import AzureOpenAI

from llm_detections.elastic_connector import log_to_elasticsearch
from llm_detections.enrichment import analyze_and_enrich_request

app = Flask(__name__)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")


@app.route("/proxy/openai", methods=["POST"])
def azure_openai_proxy():
    """Proxy endpoint for Azure OpenAI requests."""
    data = request.get_json()
    messages = data.get("messages", [])
    response_content = ""
    error_response = None

    try:
        # Forward the request to Azure OpenAI
        response = client.chat.completions.create(
            model=deployment_name, messages=messages
        )
        response_content = response.choices[
            0
        ].message.content  # Assuming one choice for simplicity
        choices = response.choices[0].model_dump()
    except openai.BadRequestError as e:
        # If BadRequestError is raised, capture the error details
        error_response = e.response.json().get("error", {}).get("innererror", {})
        response_content = e.response.json().get("error", {}).get("message")

        # Structure the response with the error details
        choices = {
            **error_response.get("content_filter_result", {}),
            "error": response_content,
            "message": {"content": response_content},
        }

    # Perform additional analysis and create the Elastic document
    additional_analysis = analyze_and_enrich_request(
        prompt=messages[-1],
        response_text=response_content,
        error_response=error_response,
    )
    log_data = {
        "request": {"messages": messages[-1]},
        "response": {"choices": response_content},
        **additional_analysis,
    }

    # Log the last message and response
    log_to_elasticsearch(log_data)

    # Calculate token usage
    prompt_tokens = sum(len(message["content"]) for message in messages)
    completion_tokens = len(response_content)
    total_tokens = prompt_tokens + completion_tokens

    # Structure and return the response
    return jsonify(
        {
            "choices": [choices],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
