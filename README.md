# Static Site Generator

This project is a small static site generator built in Python. It reads Markdown files from `content/`, applies `template.html`, copies static assets from `static/`, and writes the generated site to `docs/`.

## Course

This project was created as part of the Boot.dev Back-end Developer Path course [Build a Static Site Generator](https://www.boot.dev/courses/build-static-site-generator-python).

## Live Demo

The generated site is deployed on GitHub Pages: [https://khaledsaeed18.github.io/static-site-generator/](https://khaledsaeed18.github.io/static-site-generator/)

## What It Does

1. Converts Markdown content into HTML.
2. Builds pages recursively from the `content/` directory.
3. Copies images and other static files into the output site.
4. Replaces relative links and asset paths so the site works correctly when deployed.

## Project Structure

- `content/` stores the Markdown source pages.
- `static/` stores CSS and image assets.
- `template.html` provides the HTML layout.
- `src/` contains the Python code that generates the site.
- `docs/` contains the built output used for deployment.

## Running Locally

Generate the site with:

```bash
python3 src/main.py
```

To build the site with the GitHub Pages base path, run:

```bash
./build.sh
```

To preview the generated site locally, serve the `docs/` folder:

```bash
cd docs && python3 -m http.server 8888
```

## Tests

Run the available tests with:

```bash
./test.sh
```
