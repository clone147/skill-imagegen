# skill-imagegen

Claude Code skill for AI image generation **and logo design**: infographics, illustrations, photorealistic shots and thumbnails with built-in control over photo composition, plus a full logo workflow that ends in real SVG files, not raster pictures of logos.

It runs on your **OpenAI subscription first**: by default every image goes through `codex exec` (the Codex CLI you're already logged into, billed to your ChatGPT/OpenAI plan), so you don't need an API key or pay per image. OpenRouter is only a fallback you ask for explicitly.

- **Default:** `codex exec` (OpenAI Codex CLI with its built-in image generator). No API key, just a logged-in Codex CLI. Reference images work natively.
- **Fallback, on explicit request:** OpenRouter API through `generate_image.py`, with a selectable model and automatic prompt enhancement by an AI art director.
- **Logo design:** an identity-designer workflow (brief, category clichés, 8–12 one-line concepts, hand-built SVG, tests at 16 px / one colour / reversed / shelf test, concept sheet, then the kit: variants, favicon and app icons, presentation board, guidelines). Bundles a searchable library of 1,400+ classified real-world SVG logos and dependency-free Python scripts. Image models are used only for sketches and mockups; the mark itself is vector.
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

## Logo design

The `logo/` module inside the skill is based on [kaankiziltug/logo-design-skill](https://github.com/kaankiziltug/logo-design-skill) (MIT, see `logo/LICENSE` and `logo/SOURCE.txt`), picked as the best-reviewed logo skill of the past year. Start with `logo/WORKFLOW.md`. The main scripts:

```bash
LG=~/.claude/skills/imagegen/logo
python3 $LG/scripts/search_library.py --industry fintech --summary   # what the category looks like
python3 $LG/scripts/svg_audit.py concept-a.svg                       # live text, colours, angles, tiny details
python3 $LG/scripts/render_png.py concept-a.svg --out-dir renders    # look at your work
python3 $LG/scripts/preview_sheet.py concept-a.svg -o preview.html   # 16/32 px, one colour, reversed, shelf test
python3 $LG/scripts/concept_sheet.py a.svg b.svg c.svg --greyscale -o concepts.png
python3 $LG/scripts/export_variants.py final.svg --web-icons         # favicon.ico, PNG icons, webmanifest
```

Library logos are trademarks of their owners and are there for study only (`logo/TRADEMARKS.md`).

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
