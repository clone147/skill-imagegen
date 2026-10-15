---
name: imagegen
description: |
  Skill for image generation. DEFAULT method: `codex exec` (OpenAI Codex CLI with
  built-in image_gen). FALLBACK (only when the user explicitly asks for another
  method/model): OpenRouter API with selectable model — GPT-5.4 Image 2,
  Nano Banana Pro (Gemini 3 Pro Image), Nano Banana 2, GPT-5 Image Mini.
  Supports logos, infographics, illustrations, photorealistic images, and more.
  Includes tested photo-composition control (rule of thirds, negative space for
  headlines, leading lines, vanishing point, symmetry, frame in a frame, golden
  spiral): geometry-in-prompt recipe + composition-card sketches as reference +
  thirds-grid QA. Use for thumbnails and any image where framing matters.
  LOGO DESIGN: full identity-designer workflow (brief → clichés → 8–12 concepts →
  hand-built SVG → audit/16px/one-colour/shelf tests → concept sheet checkpoint →
  kit: variants, favicon/app icons, presentation board, guidelines) with a
  searchable library of 1,400+ real SVG logos — module `logo/` (from
  kaankiziltug/logo-design-skill, MIT). Use for logo, logotype, wordmark,
  monogram, brand mark, app icon, favicon, logo critique or redesign.
  Formerly known as nano-banana-pro.
---

# Imagegen — Image Generation Skill

## DEFAULT METHOD: `codex exec`

**Always generate images via the Codex CLI by default.** Use the OpenRouter path
(below) ONLY when the user explicitly asks for a different method or a specific
model (e.g. "użyj OpenRoutera", "użyj Nano Banana", "użyj gpt54").

Usage — one command, describe in the prompt what to generate and where to save:

```bash
codex exec "wygeneruj obraz: <opis czego chcesz>. Zapisz go do pliku <ścieżka/plik.png>"
```

**Reference images (obrazy referencyjne): codex OBSŁUGUJE je natywnie.**
Podaj ścieżki lokalnych plików wprost w prompcie — codex je odczyta i użyje jako
referencji (np. identity-lock twarzy, styl, edycja istniejącego obrazu).
Zweryfikowano 2026-07-22: podobieństwo twarzy z referencji — bardzo dobre.
NIE przełączaj się na OpenRouter tylko dlatego, że potrzebujesz referencji.

```bash
codex exec "wygeneruj obraz na podstawie zdjęcia referencyjnego /sciezka/ref.png (zachowaj dokładnie rysy twarzy): <opis sceny>. Zapisz go do pliku <ścieżka/plik.png>"
```

Notes:
- Run in background if possible — generation takes ~1–3 min.
- Codex often runs in a **read-only sandbox** and cannot write into the project.
  In that case it reports the source path under `~/.codex/generated_images/...`
  in its output — **copy that file yourself** to the requested destination (`cp`).
- Always verify the final file exists (`file <plik>.png`) and view it (Read) to
  confirm the result matches the request before reporting success.
- Prompt language: polski lub angielski — oba działają.

## Kompozycja kadru (sprawdzone 2026-10-06)

Źródło: film z 13 technikami kompozycji (X, @wmluvc, „构图原来如此简单”) + eksperyment A/B/C/D/E
na `codex exec` (2 sceny × warianty, ocena z siatką trójpodziału). Wnioski:

1. **Same nazwy technik nic nie dają.** „Use the rule of thirds, leading lines and negative space”
   dało praktycznie ten sam kadr co prompt bez kompozycji. Model i tak „ładnie kadruje” po swojemu.
2. **Działa geometria opisana wprost:** gdzie stoi obiekt (które przecięcie linii trójpodziału),
   gdzie leży horyzont, jaki % kadru jest pusty i jak, skąd i dokąd biegną linie prowadzące, jak duży
   jest obiekt (ułamek wysokości kadru), ogniskowa i wysokość aparatu, ile źródeł światła.
   Scena „inżynier + STM32 + LED” z takim opisem dała kadr premium z czystym miejscem na tytuł.
3. **Najdokładniej: karta kompozycji jako referencja** (odpowiednik przezroczystej karty ze złotą
   proporcją przykładanej do sceny w filmie). Szkic układu z `scripts/karta_kompozycji.py` podany jako
   obraz referencyjny: obiekt, punkt zbiegu i horyzont wylądowały dokładnie na liniach, bez śladów szkicu.
4. **Prawie dobry kadr → edycja, nie nowe losowanie:** „edytuj obraz X: zachowaj wszystko, tylko
   obniż horyzont na dolną linię trójpodziału” działa (może przy okazji zmienić kolory nieba).
5. **Ekrany i szyldy:** bez podanej treści model wymyśla napisy („Build / Innovate”, „Hello World!”).
   Podaj dokładny tekst albo napisz „no readable text on screens”.
6. **„One light source only: …”** daje spokojny, „drogi” obraz zamiast oświetlenia z każdej strony.

### Przepis

1. Wybierz technikę ze ściągi niżej (jedna główna, max dwie).
2. Dopisz do opisu sceny akapit `Composition (exact): …` z geometrią: pozycja obiektu, horyzont,
   pusta przestrzeń w %, linie prowadzące (skąd → dokąd), wielkość obiektu, obiektyw, wysokość
   aparatu, światło. Pisz pozycje redundantnie („on the lower third line; sky fills the top two thirds”).
3. Gdy kadr musi być precyzyjny (miniatura z miejscem na tytuł, seria w jednym układzie), dodaj kartę:
   ```bash
   python3 ~/.claude/skills/imagegen/scripts/karta_kompozycji.py trojpodzial --punkt prawy-dol --pusta lewa --horyzont dol -o /tmp/karta.png
   # układy: trojpodzial | punkt-zbiegu | symetria | rama | centrum | spirala ; --aspect 16:9|9:16|1:1|4:3|3:4|21:9
   codex exec "wygeneruj obraz: <scena>. <Composition (exact): …> Use the attached layout sketch /tmp/karta.png ONLY as a composition guide: <co oznacza każda linia i pomarańczowy znacznik>. Do not draw any lines, grid, marks or text from the sketch. Zapisz go do pliku <plik.png>"
   ```
4. Sprawdź wynik z siatką i dopiero potem raportuj:
   ```bash
   python3 ~/.claude/skills/imagegen/scripts/siatka.py wynik.png [wynik2.png …] -o /tmp/siatka.jpg   # obejrzyj przez Read
   ```
5. Jeśli coś jest prawie dobrze, popraw edycją (pkt 4 wniosków), nie generuj od zera.

### Ściąga technik (z filmu) → jak to napisać w prompcie

| Technika | Kiedy | Geometria do promptu | Karta |
|---|---|---|---|
| Trójpodział (rule of thirds) | domyślnie; obiekt + otoczenie | „subject on the intersection of the right and lower third lines; horizon on the lower third” | `trojpodzial` |
| Pusta przestrzeń (negative space) | miniatury, okładki, miejsce na tekst | „the left 55% of the frame is empty and uncluttered (no objects, no text) for a headline” / „sky fills the top two thirds” | `trojpodzial --pusta lewa\|prawa\|gora` |
| Linie prowadzące (leading lines) | droga, kable, poręcze, tory | „cables/road edges run as diagonal lines from the lower-left corner to the subject” | `punkt-zbiegu` |
| Punkt zbiegu (vanishing point) | ulice, korytarze, mosty | „all lines converge to a vanishing point on the right-third vertical line, just above the lower third” | `punkt-zbiegu --punkt lewy\|srodek\|prawy` |
| Symetria | architektura, korytarze, produkt frontem | „perfectly symmetrical, centre axis exactly in the middle, camera dead-centre at eye level” | `symetria` |
| Kadr centralny (centered) | portret, produkt, ikona | „subject dead-centre, occupying the middle fifth of the width, plain background” | `centrum` |
| Rama w ramie (frame in a frame) | okno, łuk, drzwi, liście na pierwszym planie | „dark foreground window/arch frames the scene on all sides; subject inside the opening, right of centre” | `rama` |
| Złota spirala (golden ratio) | dynamiczne sceny, posągi, krajobraz z akcentem | „main subject at the eye of a golden spiral (lower-right area); the shape of the scene curls toward it” | `spirala` |
| Równowaga asymetryczna (balanced) | dwa obiekty różnej wielkości | „large element on the left third, small counterweight element on the right third, lower” | `trojpodzial` (2 znaczniki opisz słownie) |
| Kontrast / zestawienie (juxtaposition) | dwa światy w kadrze (morze/piasek, stare/nowe) | „the frame is split diagonally from top-right to bottom-left: <A> on one side, <B> on the other” | słownie |
| Powtarzalność (repetition) | okna, rzędy, sprzęt w szeregu | „a grid of 6 identical arched windows filling the frame, evenly spaced” | słownie |

## Logo i identyfikacja (moduł `logo/`, dodany 2026-10-15)

Źródło: research `/last30days` (365 dni) — najlepiej oceniany skill do logo w ostatnim roku to
**kaankiziltug/logo-design-skill** (r/ClaudeAI 387 pkt, r/BestGitHubRepos 327 pkt, recenzje na X: „renders its own
draft SVGs and tests them… then stops” ). Skopiowany w całości do `~/.claude/skills/imagegen/logo/` (MIT,
`logo/LICENSE`, `logo/SOURCE.txt`). Pełna instrukcja: **`logo/WORKFLOW.md` — przeczytaj ją przed projektowaniem logo.**

**Zasada nr 1: logo to plik wektorowy, nie obrazek z generatora.** Model rastrowy (codex/Nano Banana) wymyśla
napisy, robi gradienty i cienie, nie daje SVG i nie przejdzie testu 16 px. Rola `codex exec` przy logo:
moodboard i szybkie szkice pomysłów (czarne na białym), oraz mockupy na końcu (szyld, kubek, koszulka z gotowym
znakiem jako referencją). Sam znak budujesz w SVG kodem i testujesz skryptami.

Skrypty (czysty Python 3, bez zależności; render przez Chrome/qlmanage — sprawdź `render_png.py --which`):
```bash
LG=~/.claude/skills/imagegen/logo
python3 $LG/scripts/search_library.py --industry <branża> --summary        # jak wygląda kategoria (nie powielaj)
python3 $LG/scripts/search_library.py --subject <motyw> --format paths     # czy taki znak już istnieje
python3 $LG/scripts/svg_audit.py a.svg b.svg c.svg                         # live text, kolory, kąty, drobne detale
python3 $LG/scripts/render_png.py a.svg b.svg --out-dir renders --size 512 # POTEM obejrzyj PNG przez Read
python3 $LG/scripts/preview_sheet.py a.svg b.svg c.svg -o preview.html     # 16/32 px, jeden kolor, rewers, mirror, shelf test
python3 $LG/scripts/concept_sheet.py a.svg b.svg c.svg --lockups a-l.svg b-l.svg c-l.svg \
    --names A B C --notes "…" "…" "…" --recommend 1 --greyscale -o concepts.png
python3 $LG/scripts/export_variants.py final.svg --title "Marka" --mono "#HEX" --icon-bg "#HEX" --web-icons
python3 $LG/scripts/presentation_board.py spec.json -o board.html --png-dir slides   # wzór: $LG/templates/
```

Przepis skrócony (szczegóły w `logo/WORKFLOW.md` i `logo/references/*.md`):
1. **Brief**: nazwa (dokładna pisownia), co robią, dla kogo, 3–5 przymiotników, konkurencja, ograniczenia
   (istniejące kolory marki!). Braki → załóż i wypisz założenia, nie zasypuj pytaniami.
2. **Klisze kategorii wypisz jawnie** i traktuj jako zakazane bez świeżej formy (taniec: sylwetka tancerki,
   nuty, buty na obcasie, serce z nutą). **Mapa słów** → przecięcia znaczeń.
3. **8–12 koncepcji po jednym zdaniu**, różne typy znaków (`references/mark-types.md`); wybierz 3 najmocniejsze
   i najbardziej różne. Opcjonalnie: szkice rastrowe przez codex („flat black vector logo sketch on white, no text,
   no gradient”) tylko do wyboru kierunku.
4. **SVG najpierw czarne**, `viewBox="0 0 256 256"`, prymitywy + łuki, kąty 0/15/30/45/60/90°, stała grubość,
   prawdziwe dziury (`fill-rule="evenodd"`), **bez `<text>` w finalu** (litery jako ścieżki). Zapisuj wersje v1, v2…
5. **Testy w pętli ≥2×**: audyt → render → obejrzyj → popraw. Craft pass: czy litera nadal czyta się jako litera,
   czyste styki, peer test obok 3–4 wzorowych znaków z biblioteki, czy nie jest zbyt dosłowne.
6. **Checkpoint**: pokaż arkusz koncepcji (greyscale), 1 linia na koncepcję + rekomendacja, zaproponuj kit
   i czekaj. Kit (kolory, lockupy, wersja na małe rozmiary, favicon/app icon, board z mockupami, guideline)
   dopiero po wyborze — chyba że user wprost każe zrobić wszystko bez pytania.
7. Uczciwość: brak gwarancji znaku towarowego (zalecić wyszukiwanie), licencje fontów, nie twierdź, że testy
   przeszły, jeśli ich nie uruchomiłeś. Biblioteka = znaki towarowe właścicieli, tylko do nauki, nigdy do kalki.

## FALLBACK: OpenRouter API (only on explicit request)

This path generates images **via the OpenRouter API** with a selectable model
(`--model` flag). Default: OpenAI GPT-5.4 Image 2 (`openai/gpt-5.4-image-2`).
Use ONLY when the user explicitly requests this method or a specific model.
Reference images are NOT a reason to use this path — codex handles them too
(see above). Uwaga na saldo OpenRouter (błąd 402 = brak kredytów; codex działa
na osobnym koncie OpenAI).

### Model selection (`--model`)

| Alias | Model OpenRouter | Klasa |
| --- | --- | --- |
| `gpt` / `gpt54` (default) | `openai/gpt-5.4-image-2` | topowy OpenAI — trzymanie się promptu, typografia; wolny (~3 min/obraz) |
| `nbp` / `pro` | `google/gemini-3-pro-image-preview` | topowy Google — detal, światło, tekst na obrazie |
| `nb2` / `flash` | `google/gemini-3.1-flash-image-preview` | szybki/tani — abstrakcje, tła |
| `gpt-mini` | `openai/gpt-5-image-mini` | kompromis cena/jakość |
| `nb1` | `google/gemini-2.5-flash-image` | starszy, najtańszy |

A full OpenRouter slug is also accepted. Models without `image_config` support
fall back automatically (aspect ratio is appended to the prompt text).

## IMPORTANT: Code location

The Python code and venv are NOT in this skill directory. They live at `$CCSKILL_IMAGEGEN_DIR` (set in user's shell profile). **Always use `$CCSKILL_IMAGEGEN_DIR` — never use the skill's base directory for running commands.**

Before generating any image, verify the setup:
```bash
echo $CCSKILL_IMAGEGEN_DIR && ls $CCSKILL_IMAGEGEN_DIR/venv/bin/python
```
If the variable is empty or venv missing, inform the user.

## Prerequisites

- `CCSKILL_IMAGEGEN_DIR` env var must point to the cloned repo (already set in `.zshrc`)
- `OPENROUTER_API_KEY` must be set (exported from `~/.secrets`, or in `$CCSKILL_IMAGEGEN_DIR/.env`)

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
- `--model`: Image model alias or full OpenRouter slug (default: `gpt54`) — see "Model selection" above

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

> Source: [7 tips to get the most out of Nano Banana Pro](https://blog.google/products/gemini/prompting-tips-nano-banana-pro/) - Google Official Blog

Include these elements in your prompts for better results:

- **Subject**: Who/what is in the image? Be specific. (e.g., "a stoic robot barista with glowing blue eyes", "a fluffy calico cat wearing a tiny wizard hat")
- **Composition**: How is the shot framed? (e.g., extreme close-up, wide shot, low-angle shot, portrait)
- **Action**: What's happening? (e.g., brewing coffee, casting a spell, mid-run through a meadow)
- **Location**: Where does the scene take place? (e.g., a futuristic cafe on Mars, a cluttered alchemist's study, a sunlit meadow at golden hour)
- **Style**: What's the overall aesthetic? (e.g., 3D animation, film noir, watercolor, photorealistic, 1990s product photography)
- **Editing Instructions**: When editing existing images, be direct and specific. (e.g., "change the man's tie to green", "remove the car from the background")

For professional results, include more specific instructions:

- **Composition & Aspect Ratio**: Define the canvas (e.g., "9:16 vertical poster", "cinematic 21:9 wide shot")
- **Camera & Lighting**: Direct the shot like a cinematographer (e.g., "low-angle shot with shallow depth of field (f/1.8)", "golden hour backlight casting long shadows")
- **Text Integration**: Clearly specify text appearance and placement (e.g., "place the headline 'URBAN EXPLORER' at the top in bold, white, sans-serif font")

### Comprehensive Guide

> Source: Guillaume Vernade, Gemini Developer Advocate, Google DeepMind
> - [X/Twitter Thread](https://x.com/GoogleAIStudio/status/1994480371061469306)

#### The Golden Rules of Prompting

Nano-Banana Pro is a "Thinking" model. It doesn't just match keywords; it understands intent, physics, and composition. To get the best results, stop using "tag soups" (e.g., dog, park, 4k, realistic) and start acting like a Creative Director.

**1. Edit, Don't Re-roll**

The model is exceptionally good at understanding conversational edits. If an image is 80% correct, do not generate a new one from scratch. Instead, simply ask for the specific change you need.

Example: "That's great, but change the lighting to sunset and make the text neon blue."

**2. Use Natural Language & Full Sentences**

Talk to the model as if you were briefing a human artist. Use proper grammar and descriptive adjectives.

- Bad: "Cool car, neon, city, night, 8k."
- Good: "A cinematic wide shot of a futuristic sports car speeding through a rainy Tokyo street at night. The neon signs reflect off the wet pavement and the car's metallic chassis."

**3. Be Specific and Descriptive**

Vague prompts yield generic results. Define the subject, the setting, the lighting, and the mood.

- Subject: Instead of "a woman," say "a sophisticated elderly woman wearing a vintage chanel-style suit."
- Materiality: Describe textures. "Matte finish," "brushed steel," "soft velvet," "crumpled paper."

**4. Provide Context (The "Why" or "For whom")**

Because the model "thinks," giving it context helps it make logical artistic decisions.

Example: "Create an image of a sandwich for a Brazilian high-end gourmet cookbook." (The model will infer professional plating, shallow depth of field, and perfect lighting).

#### Text Rendering, Infographics & Visual Synthesis

Nano-Banana Pro has SOTA capabilities for rendering legible, stylized text and synthesizing complex information into visual formats.

**Best Practices:**
- Compression: Ask the model to "compress" dense text or PDFs into visual aids.
- Style: Specify if you want a "polished editorial," a "technical diagram," or a "hand-drawn whiteboard" look.
- Quotes: Clearly specify the text you want in quotes.

**Example Prompts:**

Earnings Report Infographic (Data Ingestion):
```
[Input PDF of Google's latest earnings report]
"Generate a clean, modern infographic summarizing the key financial highlights from this earnings report. Include charts for 'Revenue Growth' and 'Net Income', and highlight the CEO's key quote in a stylized pull-quote box."
```

Retro Infographic:
```
"Make a retro, 1950s-style infographic about the history of the American diner. Include distinct sections for 'The Food,' 'The Jukebox,' and 'The Decor.' Ensure all text is legible and stylized to match the period."
```

Technical Diagram:
```
"Create an orthographic blueprint that describes this building in plan, elevation, and section. Label the 'North Elevation' and 'Main Entrance' clearly in technical architectural font. Format 16:9."
```

Whiteboard Summary (Educational):
```
"Summarize the concept of 'Transformer Neural Network Architecture' as a hand-drawn whiteboard diagram suitable for a university lecture. Use different colored markers for the Encoder and Decoder blocks, and include legible labels for 'Self-Attention' and 'Feed Forward'."
```

#### Character Consistency & Viral Thumbnails

Nano-Banana Pro supports up to 14 reference images (6 with high fidelity). This allows for "Identity Locking"—placing a specific person or character into new scenarios without facial distortion.

**Best Practices:**
- Identity Locking: Explicitly state: "Keep the person's facial features exactly the same as Image 1."
- Expression/Action: Describe the change in emotion or pose while maintaining the identity.
- Viral Composition: Combine subjects with bold graphics and text in a single pass.

**Example Prompts:**

The "Viral Thumbnail" (Identity + Text + Graphics):
```
"Design a viral video thumbnail using the person from Image 1. Face Consistency: Keep the person's facial features exactly the same as Image 1, but change their expression to look excited and surprised. Action: Pose the person on the left side, pointing their finger towards the right side of the frame. Subject: On the right side, place a high-quality image of a delicious avocado toast. Graphics: Add a bold yellow arrow connecting the person's finger to the toast. Text: Overlay massive, pop-style text in the middle: '3 mins!' Use a thick white outline and drop shadow. Background: A blurred, bright kitchen background. High saturation and contrast."
```

The "Fluffy Friends" Scenario (Group Consistency):
```
[Input 3 images of different plush creatures]
"Create a funny 10-part story with these 3 fluffy friends going on a tropical vacation. The story is thrilling throughout with emotional highs and lows and ends in a happy moment. Keep the attire and identity consistent for all 3 characters, but their expressions and angles should vary throughout all 10 images. Make sure to only have one of each character in each image."
```

Brand Asset Generation:
```
[Input 1 image of a product]
"Create 9 stunning fashion shots as if they're from an award-winning fashion editorial. Use this reference as the brand style but add nuance and variety to the range so they convey a professional design touch. Please generate nine images, one at a time."
```

#### Advanced Editing, Restoration & Colorization

The model excels at complex edits via conversational prompting. This includes "In-painting" (removing/adding objects), "Restoration" (fixing old photos), "Colorization" (Manga/B&W photos), and "Style Swapping."

**Best Practices:**
- Semantic Instructions: You do not need to manually mask; simply tell the model what to change naturally.
- Physics Understanding: You can ask for complex changes like "fill this glass with liquid" to test physics generation.

**Example Prompts:**

Object Removal & In-painting:
```
"Remove the tourists from the background of this photo and fill the space with logical textures (cobblestones and storefronts) that match the surrounding environment."
```

Manga/Comic Colorization:
```
[Input black and white manga panel]
"Colorize this manga panel. Use a vibrant anime style palette. Ensure the lighting effects on the energy beams are glowing neon blue and the character's outfit is consistent with their official colors."
```

Localization (Text Translation + Cultural Adaptation):
```
[Input image of a London bus stop ad]
"Take this concept and localize it to a Tokyo setting, including translating the tagline into Japanese. Change the background to a bustling Shibuya street at night."
```

Lighting/Seasonal Control:
```
[Input image of a house in summer]
"Turn this scene into winter time. Keep the house architecture exactly the same, but add snow to the roof and yard, and change the lighting to a cold, overcast afternoon."
```

#### Dimensional Translation (2D to 3D)

A powerful new capability is translating 2D schematics into 3D visualizations, or vice versa. This is ideal for interior designers, architects, and meme creators.

**Example Prompts:**

2D Floor Plan to 3D Interior Design Board:
```
"Based on the uploaded 2D floor plan, generate a professional interior design presentation board in a single image. Layout: A collage with one large main image at the top (wide-angle perspective of the living area), and three smaller images below (Master Bedroom, Home Office, and a 3D top-down floor plan). Style: Apply a Modern Minimalist style with warm oak wood flooring and off-white walls across ALL images. Quality: Photorealistic rendering, soft natural lighting."
```

2D to 3D Meme Conversion:
```
"Turn the 'This is Fine' dog meme into a photorealistic 3D render. Keep the composition identical but make the dog look like a plush toy and the fire look like realistic flames."
```

#### One-Shot Storyboarding & Concept Art

You can generate sequential art or storyboards without a grid, ensuring a cohesive narrative flow in a single session. This is also popular for "Movie Concept Art" (e.g., fake leaks of upcoming films).

**Example Prompt:**
```
"Create an addictively intriguing 9-part story with 9 images featuring a woman and man in an award-winning luxury luggage commercial. The story should have emotional highs and lows, ending on an elegant shot of the woman with the logo. The identity of the woman and man and their attire must stay consistent throughout but they can and should be seen from different angles and distances. Please generate images one at a time. Make sure every image is in a 16:9 landscape format."
```

#### Structural Control & Layout Guidance

Input images aren't limited to character references or subjects to edit. You can use them to strictly control the composition and layout of the final output. This is a game-changer for designers who need to turn a napkin sketch, a wireframe, or a specific grid layout into a polished asset.

**Best Practices:**
- Drafts & Sketches: Upload a hand-drawn sketch to define exactly where the text and object should sit.
- Wireframes: Use screenshots of existing layouts or wireframes to generate high-fidelity UI mockups.
- Grids: Use grid images to force the model to generate assets for tile-based games or LED displays.

**Example Prompts:**

Sketch to Final Ad:
```
"Create a ad for a [product] following this sketch."
```

UI Mockup from Wireframe:
```
"Create a mock-up for a [product] following these guidelines."
```

Pixel Art & LED Displays:
```
"Generate a pixel art sprite of a unicorn that fits perfectly into this 64x64 grid image. Use high contrast colors."
(Tip: Developers can then programmatically extract the center color of each cell to drive a connected 64x64 LED matrix display).
```

Sprites:
```
"Sprite sheet of a woman doing a backflip on a drone, 3x3 grid, sequence, frame by frame animation, square aspect ratio. Follow the structure of the attached reference image exactly."
(Tip: You can then extract each cell and make a gif)
```

### Current Limitations

- Small text, fine details, and accurate spelling may not be perfect
- Always verify factual accuracy of diagrams and infographics
- Multilingual text generation may have grammatical errors or lack cultural nuance
- Advanced edits like compositing or lighting changes may produce unnatural artifacts

## Output

- Images are saved to the specified directory (default: `./generated_images`)
- Filename format is timestamp (e.g., `20251130_153045.png`, `20251130_153045.jpg`)
- File extension is automatically determined based on the API response format (PNG/JPEG/WebP)

## Notes

- Default path (`codex exec`) needs only a logged-in Codex CLI; no API key
- OpenRouter fallback needs `OPENROUTER_API_KEY` and is billed per image
- Images from Google models (Nano Banana) include a SynthID watermark
