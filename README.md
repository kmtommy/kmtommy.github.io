# Gyeongmin Jung — Academic CV

국문·영문 전환을 지원하는 개인 연구 프로필입니다.

- Website: https://kmtommy.github.io/
- Korean: https://kmtommy.github.io/?lang=ko
- English: https://kmtommy.github.io/?lang=en

## Editing

Use **Gyeongmin Jung** as the preferred English name, including this exact capitalization. This owner-provided spelling takes precedence over external profiles.

- `index.html`: Korean CV content, links, and metadata. Readable without JavaScript.
- `script.js`: English translations, language preference, and section navigation.
- `styles.css`: Responsive layout and print styles.
- `assets/cv/`: Downloadable Korean and English CV PDFs.

## PDF downloads

The download link beside HSIR Lab. serves the PDF for the selected language.
After updating CV content, regenerate both files from `index.html` and the
English dictionary in `script.js`:

```sh
python3 scripts/generate_cv_pdfs.py
```

Generation requires Python with `reportlab` and a TrueType font containing
Korean glyphs. The script detects Arial Unicode on macOS and Nanum Gothic on
Linux; use `CV_PDF_FONT=/path/to/font.ttf` to choose another font. Only the
generated PDFs are served to visitors; no Python runtime is needed by Pages.

When editing Korean copy, update the corresponding `data-i18n` key in the
`english` dictionary in `script.js` as well. Academic grades are intentionally
excluded. Ongoing research, work in preparation, and planned projects are
labeled separately.

The site uses plain HTML, CSS, and JavaScript with no external libraries,
analytics, or build dependencies. GitHub Pages publishes from the root of `main`.

Language switching stores the preference locally and keeps the address clean.
The `?lang=ko` and `?lang=en` links still select a language on arrival; the site
then removes that parameter. The public CV excludes phone numbers.
