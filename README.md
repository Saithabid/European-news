# USA & Europe Auto News Site

100% free setup: GitHub Pages (hosting) + GitHub Actions (automation) + Google Gemini free API (rewriting).

---

## Step 1: GitHub repo banayein

1. GitHub par login karein.
2. Naya repository banayein, naam dein (e.g. `us-europe-news`).
3. **Public** rakhein (GitHub Pages free tier ke liye public repo chahiye, ya private bhi GitHub Pro mein chal jata hai - free account mein public rakhein).
4. Is folder ki saari files (fetch_news.py, requirements.txt, news_data.json, index.html, .github/, templates/) us repo mein upload kar dein.

   - Easy tareeqa: GitHub repo page par "Add file" > "Upload files" > sab files/folders drag-drop karein > Commit.

---

## Step 2: Google Gemini free API key banayein

1. Jayein: https://aistudio.google.com/app/apikey
2. Google account se login karein.
3. "Create API Key" par click karein - ek key milegi (free tier - daily limits hain lekin is project ke liye kaafi hain).
4. Key copy kar lein.

---

## Step 3: API key ko GitHub Secret mein daalein

1. Repo par jayein > **Settings** > left side menu mein **Secrets and variables** > **Actions**.
2. **New repository secret** par click karein.
3. Name: `GEMINI_API_KEY`
4. Value: apni copied key paste karein.
5. Save karein.

> Ye step zaroori hai - key kabhi bhi code mein direct na likhein, hamesha Secret mein rakhein.

---

## Step 4: GitHub Pages enable karein

1. Repo > **Settings** > left menu mein **Pages**.
2. "Build and deployment" > Source: **Deploy from a branch**.
3. Branch: `main` (ya `master`), folder: `/ (root)`.
4. Save karein.
5. Kuch minute baad aap ki site live ho jayegi: `https://yourusername.github.io/us-europe-news/`

---

## Step 5: Automation chalayein

- Workflow (`.github/workflows/update-news.yml`) automatically har 2 ghante mein chalega.
- Pehli baar manually chalane ke liye: repo > **Actions** tab > "Update News Site" workflow > **Run workflow** button.
- Ye script RSS feeds se latest USA/Europe news fetch karega, Gemini se rewrite karega, aur `index.html` + `news_data.json` ko update kar ke commit/push kar dega.

---

## Customization

- **RSS feeds**: `fetch_news.py` mein `RSS_FEEDS` dictionary mein apni pasand ke US/Europe news sources ki RSS links add/remove kar sakte hain.
- **Kitni news dikhengi**: `MAX_ITEMS` variable se control hota hai.
- **Design**: `templates/index_template.html` mein CSS/layout change kar sakte hain.
- **Cron schedule**: `.github/workflows/update-news.yml` mein `cron` line se update frequency change ho sakti hai.

---

## AdSense lagane ke liye

1. Pehle site par 20-30+ original posts/news ho jayen aur kuch din traffic ho.
2. https://www.google.com/adsense par apply karein, apni GitHub Pages URL dein (ya custom domain attach karne ke baad).
3. Approval ke baad, `templates/index_template.html` mein jahan "Ad Space" likha hai, wahan AdSense ka diya gaya `<ins class="adsbygoogle">` code paste kar dein, aur `<head>` mein AdSense script (jo comment kiya gaya hai) uncomment kar ke apna `client=ca-pub-XXXX` ID daal dein.

---

## Free custom domain (optional, baad mein)

- Shuru mein `yourusername.github.io/repo-name` URL kaafi hai.
- Baad mein agar real `.com` domain lena ho (~$10-15/year), GitHub Pages > Settings > Pages > "Custom domain" mein add kar sakte hain - DNS records domain provider ke panel mein set karni hongi (instructions GitHub docs par available hain).

---

## Important notes

- Gemini free tier ki daily request limit hai - is liye `MAX_NEW_PER_RUN = 8` rakha gaya hai (har run mein max 8 nayi news rewrite hongi). Zaroorat ho to badal sakte hain.
- Agar koi RSS feed kaam na kare (block/change ho jaye), `fetch_news.py` mein us URL ko replace kar dein.
- SEO ke liye: title, meta description, aur content English mein hai jo US/Europe audience ko target karta hai. Behtar Google ranking ke liye `sitemap.xml` aur Google Search Console setup bhi baad mein add kiya ja sakta hai.
