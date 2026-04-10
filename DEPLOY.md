# jeffhanna2.github.io — Deployment Guide

## What you have

```
index.html      ← homepage
resume.html     ← resume page
portrait.png    ← your photo (referenced by index.html)
```

---

## Step 1 — Create the repository

1. Go to **github.com/jhanna2**
2. Click **New repository**
3. Name it exactly: `jhanna2.github.io`
   - This name is required — GitHub Pages won't activate otherwise
4. Set to **Public**
5. Leave everything else unchecked (no README, no .gitignore)
6. Click **Create repository**

---

## Step 2 — Upload your files

### Option A — Browser upload (no terminal needed)

1. Open your new repo on GitHub
2. Click **Add file → Upload files**
3. Drag in all three files: `index.html`, `resume.html`, `portrait.png`
4. Scroll down, click **Commit changes**

### Option B — Git (if you have it installed)

```bash
# Clone the empty repo
git clone https://github.com/jhanna2/jhanna2.github.io
cd jhanna2.github.io

# Copy your files in, then:
git add index.html resume.html portrait.png
git commit -m "Initial deploy"
git push origin main
```

---

## Step 3 — Enable GitHub Pages

1. In your repo, go to **Settings → Pages** (left sidebar)
2. Under **Source**, select **Deploy from a branch**
3. Branch: **main** / folder: **/ (root)**
4. Click **Save**

GitHub will show a banner: *"Your site is being published at..."*

---

## Step 4 — Visit your site

```
https://jhanna2.github.io
```

It usually goes live within **1–2 minutes**. Hard refresh (`Ctrl+Shift+R` / `Cmd+Shift+R`) if you see a blank page.

---

## Making updates later

Whenever you want to change something — edit the HTML files and re-upload them (Option A), or push via git (Option B). Changes go live within about 60 seconds.

---

## Adding the PDF resume later

When you have a PDF version ready:
1. Upload it to the repo as `jeff-hanna-resume.pdf`
2. The Download button in `resume.html` already points to `#` — update that one line:

```html
<!-- find this in resume.html -->
<a href="#" class="download-btn">↓ Download PDF</a>

<!-- change to -->
<a href="jeff-hanna-resume.pdf" class="download-btn" download>↓ Download PDF</a>
```

---

## Adding projects later

When you're ready to add a projects page, just drop a `projects.html` into the repo and add the nav link back. Everything is already styled and consistent — it'll slot right in.
