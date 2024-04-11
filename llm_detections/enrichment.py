import os

from typing import Optional

from llm_guard import scan_output, scan_prompt
from llm_guard.input_scanners import Anonymize, PromptInjection, TokenLimit, Toxicity
from llm_guard.output_scanners import Deanonymize, NoRefusal, Relevance, Sensitive
from llm_guard.vault import Vault

from langkit import injections, extract


vault = Vault()
input_scanners = [Anonymize(vault), Toxicity(), TokenLimit(), PromptInjection()]
output_scanners = [Deanonymize(vault), NoRefusal(), Relevance(), Sensitive()]


def analyze_and_enrich_request(
    prompt: str, response_text: str, error_response: Optional[dict] = None
) -> dict:
    """Analyze the prompt and response text for malicious content and enrich the document."""

    # LLM Guard analysis
    sanitized_prompt, results_valid_prompt, results_score_prompt = scan_prompt(
        input_scanners, prompt["content"]
    )
    (
        sanitized_response_text,
        results_valid_response,
        results_score_response,
    ) = scan_output(output_scanners, sanitized_prompt, response_text)

    # LangKit for additional analysis
    schema = injections.init()
    langkit_result = extract({"prompt": prompt["content"]}, schema=schema)

    # Initialize identified threats and malicious flag
    identified_threats = []

    # Check LLM Guard results for prompt
    if not any(results_valid_prompt.values()):
        identified_threats.append("LLM Guard Prompt Invalid")

    # Check LLM Guard results for response
    if not any(results_valid_response.values()):
        identified_threats.append("LLM Guard Response Invalid")

    # Check LangKit result for prompt injection
    prompt_injection_score = langkit_result.get("prompt.injection", 0)
    if prompt_injection_score > 0.4:  # Adjust threshold as needed
        identified_threats.append("LangKit Injection")

    # Identify threats based on LLM Guard scores
    for category, score in results_score_response.items():
        if score > 0.5:
            identified_threats.append(category)

    # Combine results and enrich document
    # llm_guard scores map scanner names to float values of risk scores,
    # where 0 is no risk, and 1 is high risk.
    # langkit_score is a float value of the risk score for prompt injection
    # based on known threats.
    enriched_document = {
        "analysis": {
            "llm_guard_prompt_scores": results_score_prompt,
            "llm_guard_response_scores": results_score_response,
            "langkit_score": prompt_injection_score,
        },
        "malicious": any(identified_threats),
        "identified_threats": identified_threats,
    }

    # Check if there was an error from OpenAI and enrich the analysis
    if error_response:
        code = error_response.get("code")
        filtered_categories = {
            category: info["filtered"]
            for category, info in error_response.get(
                "content_filter_result", {}
            ).items()
        }

        enriched_document["analysis"]["openai"] = {
            "code": code,
            "filtered_categories": filtered_categories,
        }
        if code == "ResponsibleAIPolicyViolation":
            enriched_document["malicious"] = True

    return enriched_document
