# skill-imagegen

Claude Code skill for AI image generation: logos, infographics, illustrations, photorealistic shots and thumbnails, with built-in control over photo composition.

- **Default:** `codex exec` (OpenAI Codex CLI with its built-in image generator). No API key, just a logged-in Codex CLI. Reference images work natively.
- **Fallback, on explicit request:** OpenRouter API through `generate_image.py`, with a selectable model and automatic prompt enhancement by an AI art director.
- **Composition control:** a tested recipe for rule of thirds, negative space for headlines, leading lines, vanishing point, symmetry, frame in a frame and golden spiral. Two helper scripts draw a composition card to use as a reference and overlay a thirds grid for QA.

## Install

```bash
git clone https://github.com/clone147/skill-imagegen.git
cd skill-imagegen

# the skill itself
cp -r .claude/skills/imagegen ~/.claude/skills/

# Python for the fallback path and the helper scripts
python3 -m venv venv
venv/bin/pip install -r requirements.txt

# tell the skill where the code lives (add to ~/.zshrc or ~/.bashrc)
export CCSKILL_IMAGEGEN_DIR="$(pwd)"
```

For the default path install and log in to the [Codex CLI](https://github.com/openai/codex).

For the OpenRouter fallback set your key in the environment or in `.env` next to `generate_image.py` (see `.env.example`):

```bash
export OPENROUTER_API_KEY="your-key-from-openrouter.ai/keys"
```

`.env` is in `.gitignore`. Never commit it.

## Composition helpers

```bash
# draw a composition card (here: subject in the lower-right third, empty left side, low horizon)
python3 ~/.claude/skills/imagegen/scripts/karta_kompozycji.py trojpodzial --punkt prawy-dol --pusta lewa --horyzont dol -o /tmp/karta.png

# overlay a rule-of-thirds grid on generated images for review
python3 ~/.claude/skills/imagegen/scripts/siatka.py result.png -o /tmp/siatka.jpg
```

The card goes to the model as a reference image, together with the geometry written out in the prompt. The grid lets you check whether the model actually placed the subject where you asked.

## OpenRouter fallback

```
venv/bin/python generate_image.py "prompt" [options]

--model        alias or full OpenRouter slug (default: gpt54)
--resolution   1K, 2K, 4K (default: 2K)
--aspect       aspect ratio (default: 16:9), e.g. 1:1, 4:3, 9:16
--output       output directory (default: ./generated_images)
--reference    reference image, repeatable (up to 14)
--raw          skip prompt enhancement
```

| Alias | OpenRouter model |
| --- | --- |
| `gpt`, `gpt54` (default) | `openai/gpt-5.4-image-2` |
| `nbp`, `pro` | `google/gemini-3-pro-image-preview` (Nano Banana Pro) |
| `nb2`, `flash` | `google/gemini-3.1-flash-image-preview` (Nano Banana 2) |
| `gpt-mini` | `openai/gpt-5-image-mini` |
| `nb1` | `google/gemini-2.5-flash-image` |

Models without `image_config` support fall back automatically: the aspect ratio is appended to the prompt text.

Prompt enhancement sends your short prompt to `google/gemini-2.5-flash` first. It adds composition, lighting, camera angle, textures and mood, then the image model renders the result. Use `--raw` when your prompt is already final.

## License

MIT, see [LICENSE](LICENSE)
