#!/usr/bin/env python3
"""
AI Image Generation with Automatic Prompt Enhancement

Uses Google Gemini 3.1 Flash Image API to generate high-quality images.
Simple prompts are automatically enhanced by an AI art director for professional results.

Usage:
    python generate_image.py "prompt" [--resolution 2K] [--aspect 1:1] [--output ./generated_images]
    python generate_image.py "change the background" --reference original.png

Environment:
    GEMINI_API_KEY: API key from Google AI Studio
    (can be set in .env file)
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

_script_dir = Path(__file__).parent
load_dotenv(_script_dir / ".env")

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
        description="Generate images using Gemini 3.1 Flash Image API"
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
    return parser.parse_args(args)


def get_output_path(output_dir: str, mime_type: str = "image/png") -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = MIME_TO_EXT.get(mime_type, ".png")
    return output_path / f"{timestamp}{ext}"


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


def enhance_prompt(client: genai.Client, prompt: str) -> str:
    """Enhance a simple prompt into a detailed, professional image generation prompt."""
    print(f"[Enhance] Rewriting prompt...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Enhance this image prompt:\n\n{prompt}",
            config=types.GenerateContentConfig(
                system_instruction=ENHANCE_SYSTEM_PROMPT,
                temperature=0.9,
            )
        )
        enhanced = response.text.strip()
        print(f"[Enhance] Enhanced prompt:\n{enhanced}")
        return enhanced
    except Exception as e:
        print(f"[Enhance] Failed to enhance, using original: {e}")
        return prompt


def generate_image(
    prompt: str,
    resolution: str,
    aspect_ratio: str,
    output_dir: str,
    reference_images: list[str] | None = None,
    raw: bool = False
) -> str | None:
    """
    Generate an image using Gemini 3.1 Flash Image API.

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

    client = genai.Client()

    # Enhance prompt unless raw mode or reference images (editing mode)
    if not raw and not reference_images:
        prompt = enhance_prompt(client, prompt)

    if reference_images:
        contents: list = []
        for image_path in reference_images:
            img = Image.open(image_path)
            contents.append(img)
        contents.append(prompt)
    else:
        contents = prompt

    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=resolution
            )
        )
    )

    for part in response.parts:
        if part.text is not None:
            print(f"[Info] {part.text}")
        elif part.inline_data is not None:
            mime_type = part.inline_data.mime_type or "image/png"
            image = part.as_image()
            output_path = get_output_path(output_dir, mime_type)
            image.save(str(output_path))
            print(f"[Success] Image saved: {output_path}")
            return str(output_path)

    print("[Warning] No image in response")
    return None


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
            raw=args.raw
        )
        if result is None:
            sys.exit(1)
    except Exception as e:
        print(f"[Error] Image generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
