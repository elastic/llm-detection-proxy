# LLM Detection Proxy

This repository contains the LLM Detection Proxy, a proof-of-concept tool developed at Elastic during our quarterly OnWeek session. The project is designed to integrate security practices within the lifecycle of Large Language Models (LLMs), allowing for the detection, alerting, and triage of malicious activities in LLM workflows.

## Installation

Before running the application, ensure the following dependencies are installed:

1. **Python 3.12** - The proxy is written in Python and requires Python 3.12.
2. **Poetry** - This project uses Poetry for dependency management.

Install the required dependencies by running:

```bash
poetry install
```

## Configuration

You must set the following environment variables before starting the Flask application:

- `AZURE_OPENAI_API_KEY` - The API key for Azure OpenAI.
- `AZURE_OPENAI_ENDPOINT` - The endpoint URL for Azure OpenAI.
- `AZURE_DEPLOYMENT_NAME` - The deployment name for the Azure OpenAI instance.
- `ELASTIC_USER` - The username for the Elastic instance.
- `ELASTIC_PASSWORD` - The password for the Elastic instance.

## Running the Proxy

To start the Flask server, use the following command:

```bash
poetry run flask run --port=5000
```

This will start the Flask server on `http://localhost:5000`.

## Integration with Elastic

Ensure you have Kibana and Elasticsearch running locally. Follow the guide on [setting up a local Kibana instance](https://www.elastic.co/guide/en/kibana/current/development-getting-started.html) and [creating a connector for OpenAI in Kibana](https://www.elastic.co/guide/en/kibana/current/openai-action-type.html).

## Disclaimer

This proxy is a **proof of concept** and is **not maintained** as a production-grade tool by Elastic. It is intended for experimental use and to illustrate potential security integrations with LLMs.

## About the Project

As we continue to explore integrating security within LLMs at Elastic, this project serves as a demonstration of how embedding security into LLM workflows can provide a path forward for creating safer and more reliable applications. This project is part of ongoing research and is reflective of our commitment to security in all facets of technology development.

This repository is linked to a blog post that discusses the broader context of this work. [Read more about our work on LLMs and security on our blog.](#)

## Contact

For more information, please contact Mika Ayenson at [Mika.ayenson@elastic.co](mailto:Mika.ayenson@elastic.co).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
