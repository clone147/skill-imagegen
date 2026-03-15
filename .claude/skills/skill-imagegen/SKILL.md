---
name: skill-imagegen
description: |
  Skill for image generation.
  Uses Google Gemini 3.1 Flash Image API to generate high-quality images.
  Supports logos, infographics, illustrations, photorealistic images, and more.
---

# AI Image Generation Skill

## Overview

This skill uses the Google Gemini 3.1 Flash Image API to generate images.
Use this skill when users need image generation.

## IMPORTANT: Code location

The Python code and venv are NOT in this skill directory. They live at `$CCSKILL_IMAGEGEN_DIR` (set in user's shell profile). **Always use `$CCSKILL_IMAGEGEN_DIR` — never use the skill's base directory for running commands.**

Before generating any image, verify the setup:
```bash
echo $CCSKILL_IMAGEGEN_DIR && ls $CCSKILL_IMAGEGEN_DIR/venv/bin/python
```
If the variable is empty or venv missing, inform the user.

## Prerequisites

- `CCSKILL_IMAGEGEN_DIR` env var must point to the cloned repo (already set in `.zshrc`)
- `GEMINI_API_KEY` must be set (or in `$CCSKILL_IMAGEGEN_DIR/.env`)

## Usage

Generate images with the following command:

```bash
$CCSKILL_IMAGEGEN_DIR/venv/bin/python $CCSKILL_IMAGEGEN_DIR/generate_image.py "prompt"
```

### Options

- `--resolution`: Resolution (1K, 2K, 4K) Default: 2K
- `--aspect`: Aspect ratio (1:1, 16:9, 9:16, 4:3, etc.) Default: 16:9
- `--output`: Output directory Default: ./generated_images
- `--reference`: Reference image path (multiple allowed, up to 14)
- `--raw`: Skip automatic prompt enhancement — use the prompt exactly as provided

### Automatic Prompt Enhancement

By default, every prompt is automatically rewritten by an AI art director (Gemini Flash) before being sent to the image model. This makes simple prompts produce dramatically better results. The enhancement:
- Adds cinematic lighting, composition, camera angles, textures, and mood details
- Keeps the original concept intact
- If people are in the scene, ensures they have Central-Eastern European (Polish) appearance
- You do NOT need to write detailed prompts — simple descriptions work great

Use `--raw` only if you've already crafted a perfect prompt and don't want it changed.

### Examples

Basic image generation:
```bash
$CCSKILL_IMAGEGEN_DIR/venv/bin/python $CCSKILL_IMAGEGEN_DIR/generate_image.py "a cat playing piano in watercolor style"
```

High-resolution wide image:
```bash
$CCSKILL_IMAGEGEN_DIR/venv/bin/python $CCSKILL_IMAGEGEN_DIR/generate_image.py "sunset coastline" --resolution 4K --aspect 16:9
```

Output to specific directory:
```bash
$CCSKILL_IMAGEGEN_DIR/venv/bin/python $CCSKILL_IMAGEGEN_DIR/generate_image.py "logo design" --output ./assets/images
```

### Reference Image Editing

Edit or modify existing images by providing reference images:

```bash
# Change background
$CCSKILL_IMAGEGEN_DIR/venv/bin/python $CCSKILL_IMAGEGEN_DIR/generate_image.py "change background to sunset" --reference ./original.png

# Use multiple reference images (pose, style, etc.)
$CCSKILL_IMAGEGEN_DIR/venv/bin/python $CCSKILL_IMAGEGEN_DIR/generate_image.py "draw this person in this pose" --reference ./person.png --reference ./pose.png
```

Reference image use cases:
- Partial image editing (background change, color adjustment, etc.)
- Style transfer (apply style from another image)
- Character consistency (same person in different scenes)
- Image compositing

## Prompting Guide

### Quick Reference

Include these elements in your prompts for better results:

- **Subject**: Who/what is in the image? Be specific.
- **Composition**: How is the shot framed? (e.g., extreme close-up, wide shot, low-angle shot)
- **Action**: What's happening?
- **Location**: Where does the scene take place?
- **Style**: What's the overall aesthetic? (e.g., 3D animation, film noir, watercolor, photorealistic)
- **Editing Instructions**: When editing existing images, be direct and specific.

### Current Limitations

- Small text, fine details, and accurate spelling may not be perfect
- Always verify factual accuracy of diagrams and infographics
- Multilingual text generation may have grammatical errors

## Output

- Images are saved to the specified directory (default: `./generated_images`)
- Filename format is timestamp (e.g., `20251130_153045.png`)
- File extension is automatically determined based on the API response format (PNG/JPEG/WebP)

## Notes

- The environment variable `GEMINI_API_KEY` must be set
- Generated images include SynthID watermark
