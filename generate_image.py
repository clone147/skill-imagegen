#!/usr/bin/env python3
"""
AI Image Generation with Automatic Prompt Enhancement (via OpenRouter)

Uses the OpenRouter API to generate high-quality images. Default model:
openai/gpt-5.4-image-2 (selectable via --model). Simple prompts are
automatically enhanced by an AI art director for professional results.

Usage:
    python generate_image.py "prompt" [--resolution 2K] [--aspect 1:1] [--output ./generated_images]
    python generate_image.py "change the background" --reference original.png

Environment:
    OPENROUTER_API_KEY: API key from https://openrouter.ai/keys
    (can be set in .env file next to this script)
"""

import argparse
import base64
import mimetypes
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

_script_dir = Path(__file__).parent
load_dotenv(_script_dir / ".env")

import os  # noqa: E402  (after load_dotenv so .env values are visible)

API_URL = "https://openrouter.ai/api/v1/chat/completions"
ENHANCE_MODEL = "google/gemini-2.5-flash"

# aliasy modeli obrazkowych (przyjmowany jest też pełny slug OpenRouter)
MODEL_ALIASES = {
    "nb2":      "google/gemini-3.1-flash-image-preview",  # Nano Banana 2
    "flash":    "google/gemini-3.1-flash-image-preview",
    "nbp":      "google/gemini-3-pro-image-preview",      # Nano Banana Pro
    "pro":      "google/gemini-3-pro-image-preview",
    "nb1":      "google/gemini-2.5-flash-image",          # Nano Banana 1
    "gpt":      "openai/gpt-5.4-image-2",
    "gpt54":    "openai/gpt-5.4-image-2",
    "gpt-mini": "openai/gpt-5-image-mini",
}
DEFAULT_MODEL = "gpt54"

DEFAULT_RESOLUTION = "2K"
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_OUTPUT_DIR = "./generated_images"

MIME_TO_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate images via OpenRouter (default model: GPT-5.4 Image 2)"
    )
    parser.add_argument("prompt", type=str, help="Image generation prompt")
    parser.add_argument(
        "--resolution", type=str, default=DEFAULT_RESOLUTION,
        choices=["1K", "2K", "4K"],
        help=f"Output resolution (default: {DEFAULT_RESOLUTION})"
    )
    parser.add_argument(
        "--aspect", type=str, default=DEFAULT_ASPECT_RATIO,
        help=f"Aspect ratio (default: {DEFAULT_ASPECT_RATIO})"
    )
    parser.add_argument(
        "--output", type=str, default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--reference", type=str, action="append", default=[],
        help="Reference image path (can be specified multiple times, up to 14)"
    )
    parser.add_argument(
        "--raw", action="store_true", default=False,
        help="Skip prompt enhancement — use the prompt as-is"
    )
    parser.add_argument(
        "--model", type=str, default=DEFAULT_MODEL,
        help="Image model: alias (%s) or full OpenRouter slug (default: %s)"
             % (", ".join(sorted(set(MODEL_ALIASES))), DEFAULT_MODEL)
    )
    return parser.parse_args(args)


def get_api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        print("[Error] OPENROUTER_API_KEY is not set (env or .env)")
        sys.exit(1)
    return key


def get_output_path(output_dir: str, mime_type: str = "image/png") -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = MIME_TO_EXT.get(mime_type, ".png")
    return output_path / f"{timestamp}{ext}"


def post(payload: dict, api_key: str, timeout: int = 300) -> dict:
    response = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ccskill-imagegen",
            "X-Title": "ccskill-imagegen",
        },
        json=payload,
        timeout=timeout,
    )
    data = response.json()
    if response.status_code != 200 or "error" in data:
        raise RuntimeError(f"{response.status_code} {data.get('error', data)}")
    return data


ENHANCE_SYSTEM_PROMPT = """\
You are a world-class art director, photographer, and visual storytelling master. \
Your job is to take a simple image prompt and transform it into a richly detailed, \
cinematic prompt that will produce stunning, professional-quality images.

RULES:
1. Rewrite the prompt using natural, descriptive English sentences (never tag soup).
2. Add specific details about: composition, camera angle, lighting (type, direction, color temperature), \
   materials/textures, mood/atmosphere, color palette, and depth of field.
3. Keep the original intent and subject matter — enhance, don't change the concept.
4. If the prompt involves or could involve people/humans: ALL people MUST be white/Caucasian \
   with Central-Eastern European (Polish) appearance — fair skin, natural hair colors \
   (blonde, brown, auburn), European facial features. This is a hard requirement.
5. Output ONLY the enhanced prompt — no explanations, no preamble, no quotes around it.
6. Keep the enhanced prompt under 300 words.
7. Think like a cinematographer briefing a VFX team — be precise about every visual element.\
"""


def enhance_prompt(prompt: str, api_key: str) -> str:
    """Enhance a simple prompt into a detailed, professional image generation prompt."""
    print("[Enhance] Rewriting prompt...")
    try:
        data = post({
            "model": ENHANCE_MODEL,
            "messages": [
                {"role": "system", "content": ENHANCE_SYSTEM_PROMPT},
                {"role": "user", "content": f"Enhance this image prompt:\n\n{prompt}"},
            ],
            "temperature": 0.9,
        }, api_key, timeout=120)
        enhanced = data["choices"][0]["message"]["content"].strip()
        print(f"[Enhance] Enhanced prompt:\n{enhanced}")
        return enhanced
    except Exception as e:
        print(f"[Enhance] Failed to enhance, using original: {e}")
        return prompt


def encode_reference(image_path: str) -> dict:
    mime = mimetypes.guess_type(image_path)[0] or "image/png"
    b64 = base64.b64encode(Path(image_path).read_bytes()).decode()
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}


def save_data_url(data_url: str, output_dir: str) -> Path:
    match = re.match(r"data:(image/[a-z+.-]+);base64,(.*)", data_url, re.S)
    if not match:
        raise RuntimeError("Unexpected image payload (not a base64 data URL)")
    mime_type, b64 = match.groups()
    output_path = get_output_path(output_dir, mime_type)
    output_path.write_bytes(base64.b64decode(b64))
    return output_path


def generate_image(
    prompt: str,
    resolution: str,
    aspect_ratio: str,
    output_dir: str,
    reference_images: list[str] | None = None,
    raw: bool = False,
    model: str = DEFAULT_MODEL,
) -> str | None:
    """
    Generate an image via OpenRouter.

    Args:
        prompt: Image generation prompt
        resolution: Output resolution (1K, 2K, 4K)
        aspect_ratio: Aspect ratio (e.g., 1:1, 16:9)
        output_dir: Output directory
        reference_images: List of reference image paths (up to 14)
        raw: If True, skip prompt enhancement

    Returns:
        Path to generated image, or None on failure
    """
    if reference_images:
        for image_path in reference_images:
            if not Path(image_path).exists():
                print(f"[Error] Reference image not found: {image_path}")
                return None

    api_key = get_api_key()
    image_model = MODEL_ALIASES.get(model, model)
    print(f"[Model] {image_model}")

    # Enhance prompt unless raw mode or reference images (editing mode)
    if not raw and not reference_images:
        prompt = enhance_prompt(prompt, api_key)

    if reference_images:
        content: list = [encode_reference(p) for p in reference_images]
        content.append({"type": "text", "text": prompt})
    else:
        content = prompt

    payload = {
        "model": image_model,
        "messages": [{"role": "user", "content": content}],
        "modalities": ["image", "text"],
        "image_config": {
            "aspect_ratio": aspect_ratio,
            "image_size": resolution,
        },
    }
    try:
        data = post(payload, api_key)
    except RuntimeError as e:
        # niektóre modele nie znają image_config — ponów z formatem opisanym w prompcie
        print(f"[Fallback] image_config rejected ({e}); retrying without it")
        payload.pop("image_config", None)
        if not reference_images:
            payload["messages"] = [{
                "role": "user",
                "content": f"{prompt}\n\nOutput format: {aspect_ratio} aspect ratio.",
            }]
        data = post(payload, api_key)

    message = data["choices"][0]["message"]
    text = (message.get("content") or "").strip()
    if text:
        print(f"[Info] {text}")

    images = message.get("images") or []
    if not images:
        print("[Warning] No image in response")
        return None

    output_path = save_data_url(images[0]["image_url"]["url"], output_dir)
    print(f"[Success] Image saved: {output_path}")
    return str(output_path)


def main():
    args = parse_args()

    if args.reference and len(args.reference) > 14:
        print("[Error] Maximum 14 reference images allowed")
        sys.exit(1)

    try:
        result = generate_image(
            prompt=args.prompt,
            resolution=args.resolution,
            aspect_ratio=args.aspect,
            output_dir=args.output,
            reference_images=args.reference if args.reference else None,
            raw=args.raw,
            model=args.model,
        )
        if result is None:
            sys.exit(1)
    except Exception as e:
        print(f"[Error] Image generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
