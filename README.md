# Pelican Portfolio & Blog

Personal website and blog built with Pelican static site generator.

## Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Build the site:
```bash
pelican content
```

3. Preview locally:
```bash
pelican --listen
```

Visit http://localhost:8000 to preview.

## Deployment

Site automatically builds and deploys to GitHub Pages on push to the `master` branch via GitHub Actions.

The CV is fetched from the private `andre-motta/personal_cv` repository during
the GitHub Pages build, so CV revisions are not stored in this public
repository. The workflow requires a read-only `PERSONAL_CV_REPO_TOKEN` secret
with access to the private repository. It can be started manually after a CV
update, or triggered with the `cv-updated` repository-dispatch event.

## Structure

- `content/` - Markdown files for blog posts
- `content/pages/` - Markdown files for static pages (About, etc.)
- `themes/minimal/` - Custom minimalist theme
- `pelicanconf.py` - Development configuration
- `publishconf.py` - Production configuration

## Adding Content

### Blog Post

Create a new `.md` file in `content/`:

```markdown
Title: Your Post Title
Date: 2025-11-15
Category: Category Name
Tags: tag1, tag2
Slug: url-slug
Summary: Brief description

Your content here...
```

### Static Page

Create a new `.md` file in `content/pages/`:

```markdown
Title: Page Title
Slug: page-url

Your content here...
```

## License

Content © 2025 Andre Lustosa
