# larryzpl123.github.io

Personal site for Peilin (Larry) Zhong — computational neuroscience, brain-computer interfaces, and history.

**Live at [larryzpl123.github.io](https://larryzpl123.github.io)**

---

## What this is

A static, dependency-free personal site served by GitHub Pages. No framework, no build step, no package manager. Two HTML files hold all the markup, styling, and behaviour, and every piece of text on the site comes from one plain-text file.

The idea is that adding a paper or an award should mean editing a few lines of `content.txt` and pushing. Nothing else.

## Layout

```
index.html          the whole site: markup, CSS and JS in one file
content.txt         ALL text content. This is the only file you normally edit.
portrait.jpg        photo used on the landing page
works/
  index.html        a standalone page listing the WORKS entries
  *.pdf             the papers and essays linked from WORKS
LICENSE             MIT
```

`index.html` and `works/index.html` both `fetch` `content.txt` at load time and render it. They share the same parser, so the format below applies to both.

## Editing the site

Open `content.txt`. It is divided into sections:

```
=== SECTION-NAME ===
...content...
```

The sections, in the order they appear on the page:

| Section | Renders as | Format |
|---|---|---|
| `INTRO` | the line under the name | one paragraph of prose |
| `ABOUT` | About | prose, blank line between paragraphs |
| `CURRENTLY` | Currently | prose |
| `RESEARCH-INTERESTS` | Research | prose |
| `SELECTED-WORK` | Projects | entries (see below) |
| `AWARDS` | Awards | entries |
| `CONTACTS` | Contact | entries |
| `WORKS` | Writing & Research | entries |

### Entry format

Entries are blocks of `KEY: value` lines, separated by a blank line. Keys must be **uppercase**; a lowercase key is treated as a continuation of the line above it.

`SELECTED-WORK` and `WORKS` take `TAG`, `TITLE`, `LINK`, `DESCRIPTION`:

```
TAG: Computational Neuroscience · preprint
TITLE: Screens Reject, Only Mechanism Confirms
LINK: https://doi.org/10.5281/zenodo.21272958
DESCRIPTION: Independent research. Shows the standard spectral test is blind to
genuine gamma on a theta-driven CA1 network.
```

`AWARDS` takes `YEAR`, `NAME`, `DETAIL`, `LINK`:

```
YEAR: 2025
NAME: Brain Bee, Regional Runner-Up (2nd)
DETAIL: Neuroscience
LINK:
```

`CONTACTS` takes `LABEL`, `VALUE`, `LINK`:

```
LABEL: ORCID
VALUE: 0009-0006-5542-8057
LINK: https://orcid.org/0009-0006-5542-8057
```

`LINK` may be left empty. If it is, the title or name renders as plain text instead of a link.

A value can wrap onto the following lines; anything that is not a `KEY:` line gets appended to the key above it.

### Inline formatting

Available inside any prose or `DESCRIPTION`:

- `**bold**`
- `*italic*`
- `[link text](https://example.com)`

Everything else is escaped, so raw HTML will not render.

### Removing a section

Delete the section, or leave it empty, and the whole block disappears from the page. The remaining sections renumber themselves automatically, so there are no gaps to clean up.

## Theme

Dark by default, with a light theme toggled by the button in the corner. The choice is stored in `localStorage` under `theme` and applied before first paint, so there is no flash on reload. The two palettes are defined as CSS custom properties at the top of `index.html`, under `:root` and `:root[data-theme="light"]`.

## Running it locally

`content.txt` is loaded with `fetch`, which browsers block on `file://`. Serve the folder over HTTP instead:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## Deploying

GitHub Pages serves the `main` branch from the repository root. Push and the change is live within a minute or so; a hard refresh may be needed to get past the CDN cache.

## Notes

- Fonts come from Google Fonts. Everything else is local, so the site works offline apart from the typefaces.
- PDFs in `works/` are linked from the `WORKS` section by relative path, for example `/works/history-2025.pdf`.

## License

MIT, see [LICENSE](LICENSE). The written work and the PDFs under `works/` are my own and are not covered by that licence.
