# larryzpl123.github.io

Personal site for Peilin (Larry) Zhong — computational neuroscience, brain-computer interfaces, and history.

**Live at [larryzpl123.github.io](https://larryzpl123.github.io)**

---

## What this is

A static, dependency-free personal site served by GitHub Pages. No framework, no package manager, no npm. Two HTML files hold all the markup, styling, and behaviour, and every piece of text on the site comes from one plain-text file.

The idea is that adding a paper or an award should mean editing a few lines of `content.txt`, running one script, and pushing.

That one script is `render.py`. The site used to build its entire body from `content.txt` with `fetch()` at load time, which meant anything that does not execute JavaScript — link-preview bots, Bing, most LLM and agent crawlers, whatever someone pastes your URL into — saw an empty shell with five nav anchors and no text. `render.py` writes the rendered HTML into the files so the content is in the source. `content.txt` is still the only file you edit.

## Layout

```
index.html          the whole site: markup, CSS and JS in one file
content.txt         ALL text content. This is the only file you normally edit.
render.py           pre-renders content.txt into the HTML. Run after every edit.
sitemap.xml         listed in robots.txt, submitted to search engines
robots.txt          allows everything, points at the sitemap
portrait.jpg        photo used on the landing page
.github/workflows/
  prerender-check.yml   CI: fails the push if render.py was not re-run
works/
  index.html        a standalone page listing the WORKS entries
  *.pdf             the papers and essays linked from WORKS
LICENSE             MIT
```

`index.html` and `works/index.html` both contain the content twice over: once pre-rendered into the markup by `render.py`, and once as a live `fetch('content.txt')` at load time. The format below applies to both pages, and `render.py` is a line-for-line port of the same parser, so all three agree.

## The pre-render contract

Every `render.py` run stamps `sha256(content.txt)` onto `<html data-content-hash="...">`. On load the page re-fetches `content.txt` and re-hashes it:

| situation | what happens |
|---|---|
| hash matches | the pre-rendered DOM is current — the page leaves it alone |
| hash differs | **`content.txt` wins**: the page re-renders live from it, shows a red STALE banner, and logs `console.error` |
| fetch fails (offline, `file://`) | the pre-rendered DOM stands |

So editing `content.txt` and forgetting to run `render.py` never shows stale text to a human — the live file always wins in the browser. It only degrades what crawlers see, and the banner plus the CI check are there to make sure that never lasts more than one push.

```bash
python3 render.py           # rewrite the HTML from content.txt
python3 render.py --check   # exit 1 if the HTML is stale — this is what CI runs
```

Optional local guard, so you cannot forget:

```bash
printf '#!/bin/sh\npython3 render.py --check || { python3 render.py; git add index.html works/index.html; }\n' > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Identity metadata

`index.html` carries a JSON-LD `Person` block binding the three name forms — `Peilin Zhong` (the name on the papers), `Larry Zhong`, and `Peilin (Larry) Zhong` — to one ORCID, plus `sameAs` links to GitHub, LinkedIn and the Zenodo DOIs. This exists because "Peilin Zhong" is also an active CS researcher; the block is what tells a search engine which one this site is about. If you add a profile anywhere, add it to `sameAs`.

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

GitHub Pages serves the `main` branch from the repository root. Run `python3 render.py`, commit both `content.txt` and the regenerated HTML, and push; the change is live within a minute or so, and a hard refresh may be needed to get past the CDN cache. The `prerender-check` workflow fails the push if the HTML was not regenerated.

## Notes

- Fonts come from Google Fonts. Everything else is local, so the site works offline apart from the typefaces.
- PDFs in `works/` are linked from the `WORKS` section by relative path, for example `/works/history-2025.pdf`.

## License

MIT, see [LICENSE](LICENSE). The written work and the PDFs under `works/` are my own and are not covered by that licence.
