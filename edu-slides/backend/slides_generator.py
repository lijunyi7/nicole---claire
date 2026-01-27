"""
Slide generator for Educational Slides Resource Collector
Uses a single LLM prompt to return a full slide deck in JSON.
"""

import json
import re
from typing import List, Dict, Any, Tuple

from openai import OpenAI

from config.env_config import get_openai_api_key


def _extract_json(text: str) -> Dict[str, Any]:
    """Extract JSON object from model output."""
    if not text:
        raise ValueError("Empty response from model")

    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model response")

    return json.loads(match.group(0))


def _normalize_bullets(bullets: Any) -> List[str]:
    if not isinstance(bullets, list):
        return []
    cleaned = []
    for item in bullets:
        if isinstance(item, str):
            text = item.strip()
            if text:
                cleaned.append(text)
    return cleaned


def _normalize_sources(sources: Any) -> List[str]:
    if not isinstance(sources, list):
        return []
    cleaned = []
    for item in sources:
        if isinstance(item, str):
            text = item.strip()
            if text:
                cleaned.append(text)
    return cleaned


def _validate_deck(deck: Dict[str, Any]) -> Dict[str, Any]:
    slides = deck.get("slides", [])
    if not isinstance(slides, list):
        raise ValueError("Slides must be a list")

    validated_slides = []
    for slide in slides:
        if not isinstance(slide, dict):
            continue
        title = (slide.get("title") or "").strip()
        bullets = _normalize_bullets(slide.get("bullets"))
        sources = _normalize_sources(slide.get("sources"))
        notes = slide.get("notes")
        if not title:
            continue
        if len(bullets) < 3:
            continue
        if len(bullets) > 5:
            bullets = bullets[:5]
        if len(sources) > 2:
            sources = sources[:2]

        cleaned = {
            "title": title,
            "bullets": bullets,
            "sources": sources,
        }
        if isinstance(notes, str) and notes.strip():
            cleaned["notes"] = notes.strip()

        validated_slides.append(cleaned)

    if not validated_slides:
        raise ValueError("No valid slides returned from model")

    deck["slides"] = validated_slides[:10]
    return deck


def generate_slide_deck(topic: str, grade: str) -> Tuple[Dict[str, Any], str]:
    """
    Generate a slide deck using a single LLM prompt.
    Returns (deck, raw_text).
    """
    client = OpenAI(api_key=get_openai_api_key())
    prompt = (
        "You are generating a slide deck for students. "
        "Return ONLY valid JSON with the following schema:\n"
        "{\n"
        '  "topic": string,\n'
        '  "student_level": string,\n'
        '  "slides": [\n'
        "    {\n"
        '      "title": string,\n'
        '      "bullets": [string, string, string, ...],\n'
        '      "sources": [string, ...],\n'
        '      "notes": string (optional)\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Rules:\n"
        "- Create 8-10 slides.\n"
        "- Each slide must have 3-5 short bullets.\n"
        "- Bullets must be student-level appropriate.\n"
        "- Include 1-2 credible sources per slide (URLs or source names).\n"
        "- Do not use markdown or extra text outside JSON.\n\n"
        f"Topic: {topic}\n"
        f"Student level: {grade}\n"
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    raw_text = getattr(response, "output_text", None)
    if not raw_text and hasattr(response, "output"):
        for output in response.output:
            if hasattr(output, "content") and output.content:
                for content in output.content:
                    text_value = getattr(content, "text", None)
                    if text_value:
                        raw_text = text_value
                        break
            if raw_text:
                break

    if not raw_text:
        raise ValueError("Model returned no text output")

    deck = _extract_json(raw_text)
    if "topic" not in deck:
        deck["topic"] = topic
    if "student_level" not in deck:
        deck["student_level"] = grade

    deck = _validate_deck(deck)
    return deck, raw_text


def generate_slides(topic: str, grade: str) -> List[Dict[str, Any]]:
    """Return validated slides only (convenience wrapper)."""
    deck, _raw = generate_slide_deck(topic, grade)
    return deck["slides"]
