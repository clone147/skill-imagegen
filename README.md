# skill-imagegen

Claude Code skill for AI image generation with automatic prompt enhancement.

Write a simple prompt like "a cat on a roof" and the built-in AI art director rewrites it into a cinematic, detailed description before generating the image. Powered by Gemini 3.1 Flash Image.

## Install

```bash
claude install-skill https://github.com/clone147/skill-imagegen
```

Then set your API key:

```bash
export GEMINI_API_KEY="your-key-from-ai.google.dev"
```

## How prompt enhancement works

Your simple prompt goes through a two-step pipeline:

1. **Gemini 2.5 Flash** rewrites your prompt into a professional art direction — adding composition, lighting, camera angle, textures, mood, and color palette
2. **Gemini 3.1 Flash Image** generates the image from the enhanced prompt

Use `--raw` to skip enhancement and send your prompt directly.

## Examples

| You write | AI art director sends |
|---|---|
| `"a cat on a roof"` | A ginger tabby cat perched on weathered terracotta roof tiles, golden hour backlighting casting warm amber highlights through translucent ear tips... |
| `"modern office"` | A minimalist open-plan office space with floor-to-ceiling windows, soft diffused northern light streaming across polished concrete floors... |
| `"coffee shop logo"` | A hand-lettered coffee shop emblem featuring an artisan coffee cup with rising steam forming elegant swirls... |

## CLI options

```
python generate_image.py "prompt" [options]

--resolution   1K, 2K, 4K (default: 2K)
--aspect       Aspect ratio (default: 16:9) — supports 1:1, 4:3, 9:16, etc.
--output       Output directory (default: ./generated_images)
--reference    Reference image for editing (up to 14, repeatable)
--raw          Skip prompt enhancement
```

## Reference image editing

```bash
# Change background
python generate_image.py "change background to sunset" --reference photo.png

# Style transfer with multiple references
python generate_image.py "apply this art style" --reference content.png --reference style.png
```

## License

MIT — see [LICENSE](LICENSE)
