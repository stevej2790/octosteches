#!/usr/bin/env python3
"""Download all CSS, JS, images, icons for careers pages and rewrite paths."""

import asyncio
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

from playwright.async_api import async_playwright

BASE = Path(__file__).parent
CAREERS = BASE / "careers"
ASSETS = CAREERS / "assets"
ORIGIN = "https://recruitcrm.io"

S3_IMAGES = {
    "logo": "https://production-recruitcrm-virginia.s3.amazonaws.com/42438/account/Ensitech_4/logo?updatedonParam=1717787583723",
    "logo_full": "https://production-recruitcrm-virginia.s3.amazonaws.com/42438/account/Ensitech_4/logo?updatedonParam=1717787583723,Sin%20dudas.png",
    "jobtitlebglogo": "https://production-recruitcrm-virginia.s3.amazonaws.com/42438/account/Ensitech_4/jobtitlebglogo?updatedonParam=1717787799062",
    "jobtitlebglogo_full": "https://production-recruitcrm-virginia.s3.amazonaws.com/42438/account/Ensitech_4/jobtitlebglogo?updatedonParam=1717787799062,Best.png",
    "sharejobimage": "https://production-recruitcrm-virginia.s3.amazonaws.com/42438/account/Ensitech_4/sharejobimage?updatedonParam=1718141083482",
    "talentpoollogo": "https://production-recruitcrm-virginia.s3.amazonaws.com/42438/account/Ensitech_4/talentpoollogo?updatedonParam=1718483285266",
}


def extract_asset_urls(text):
    urls = set()

    # Full URLs
    for m in re.finditer(r"https?://[^\s\"'<>\)\\]+", text):
        u = m.group(0).rstrip("\"');, ")
        if any(x in u for x in ("recruitcrm.io", "s3.amazonaws.com", "s3.ap-southeast")):
            u = u.split("#")[0]
            parsed = urlparse(u)
            if parsed.path or "s3.amazonaws" in parsed.netloc:
                urls.add(u)

    # Relative recruitcrm paths
    for m in re.finditer(r'["\'](/(?:_next|externalpages_v2|static-assets)[^"\']+)["\']', text):
        urls.add(ORIGIN + m.group(1).split("?")[0] if "?" not in m.group(1) else ORIGIN + m.group(1))

    # src/href without quotes issues - extract /_next paths
    for m in re.finditer(r'(?:href|src)="(/_next/[^"]+)"', text):
        urls.add(ORIGIN + m.group(1))
    for m in re.finditer(r'(?:href|src)="(/externalpages_v2/[^"]+)"', text):
        urls.add(ORIGIN + m.group(1))
    for m in re.finditer(r'(?:href|src)="(/static-assets/[^"]+)"', text):
        urls.add(ORIGIN + m.group(1))

    # From preload links
    for m in re.finditer(r'href="(/_next/static/[^"]+\.css)"', text):
        urls.add(ORIGIN + m.group(1))
    for m in re.finditer(r'src="(/_next/static/[^"]+\.js)"', text):
        urls.add(ORIGIN + m.group(1))

    # static-assets css preloads
    for m in re.finditer(r'href="(/static-assets/_next/static/[^"]+)"', text):
        urls.add(ORIGIN + m.group(1))

    return urls


def url_to_local(url):
    parsed = urlparse(url)
    if "recruitcrm.io" in parsed.netloc:
        path = parsed.path.lstrip("/")
        if not path:
            return None
        if path.startswith("static-assets/"):
            path = path[len("static-assets/") :]
        return ASSETS / "recruitcrm.io" / path
    if "s3.amazonaws.com" in parsed.netloc or "s3.ap-southeast" in parsed.netloc:
        path = parsed.path.lstrip("/")
        ext = ".png"
        if "?" in url:
            q = url.split("?", 1)[1]
            if "," in q:
                ext_part = q.split(",")[-1]
                if "." in ext_part:
                    ext = "." + ext_part.split(".")[-1].split("&")[0]
        safe = path.replace("/", "_") + ext
        return ASSETS / "images" / safe
    return None


def relative_asset_path(from_file, local_path):
    rel = Path(os_relpath(local_path, from_file.parent))
    return str(rel).replace("\\", "/")


def os_relpath(target, start):
    import os
    return os.path.relpath(str(target), str(start))


async def download_all(urls):
    ASSETS.mkdir(parents=True, exist_ok=True)
    mapping = {}
    failed = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.goto(f"{ORIGIN}/jobs/Ensitech_Careers", wait_until="networkidle", timeout=60000)

        all_urls = sorted(urls)
        # Add known S3 images
        for url in S3_IMAGES.values():
            all_urls.append(url)

        # Standard assets we know are needed
        known = [
            "/externalpages_v2/icons/magnify.svg",
            "/externalpages_v2/favicons/favicon.ico",
            "/_next/static/css/63c45352ad9c2382.css",
            "/_next/static/chunks/webpack-568c270586e4d5b9.js",
            "/_next/static/chunks/fd9d1056-f56f83c3bedbde16.js",
            "/_next/static/chunks/2117-f99bcdef1d318134.js",
            "/_next/static/chunks/main-app-cad3aa252788dd79.js",
            "/_next/static/chunks/2972-cf828072ec772a0b.js",
            "/_next/static/chunks/polyfills-42372ed130431b0a.js",
            "/_next/static/media/3a9fd9773111cd4d-s.p.woff2",
            "/static-assets/_next/static/media/1e41be92c43b3255-s.p.woff2",
            "/static-assets/_next/static/media/44ca41e4fd5cc616-s.p.woff2",
            "/static-assets/_next/static/media/904be59b21bd51cb-s.p.woff2",
            "/static-assets/_next/static/css/46d447d8895e09a1.css",
            "/static-assets/_next/static/css/8a3ab71d74223d6e.css",
            "/static-assets/_next/static/css/699608b5627cf431.css",
        ]
        for k in known:
            all_urls.append(ORIGIN + k)

        all_urls = sorted(set(all_urls))
        total = len(all_urls)

        ASSET_EXTS = (".css", ".js", ".woff2", ".woff", ".ttf", ".svg", ".png", ".jpg", ".ico", ".gif", ".webp", ".cur")

        for i, url in enumerate(all_urls, 1):
            local = url_to_local(url)
            if not local:
                continue
            # Skip non-asset recruitcrm paths
            if "recruitcrm.io" in url and "s3.amazonaws" not in url:
                path_lower = urlparse(url).path.lower()
                if not any(path_lower.endswith(e) or e in path_lower for e in ASSET_EXTS):
                    if "/_next/" not in path_lower and "/externalpages" not in path_lower:
                        continue
            if local.exists() and local.stat().st_size > 0:
                mapping[url] = str(local.relative_to(CAREERS))
                continue
            local.parent.mkdir(parents=True, exist_ok=True)
            try:
                resp = await ctx.request.get(url, timeout=30000)
                if resp.ok:
                    local.write_bytes(await resp.body())
                    mapping[url] = str(local.relative_to(CAREERS))
                    print(f"[{i}/{total}] OK {url[:80]}")
                else:
                    failed.append(url)
                    print(f"[{i}/{total}] FAIL {resp.status} {url[:80]}")
            except Exception as e:
                failed.append(url)
                print(f"[{i}/{total}] ERR {url[:60]}: {e}")

        await browser.close()

    return mapping, failed


def rewrite_html_files(mapping):
    # Image shortcut mappings for _next/image URLs
    image_map = {
        "Ensitech_4%2Flogo": "assets/images/42438_account_Ensitech_4_logo.png",
        "Ensitech_4%2Fjobtitlebglogo": "assets/images/42438_account_Ensitech_4_jobtitlebglogo.png",
        "Ensitech_4%2Fsharejobimage": "assets/images/42438_account_Ensitech_4_sharejobimage.png",
        "Ensitech_4%2Ftalentpoollogo": "assets/images/42438_account_Ensitech_4_talentpoollogo.png",
    }

    for html_file in CAREERS.rglob("*.html"):
        content = html_file.read_text(encoding="utf-8", errors="ignore")
        original = content
        depth = len(html_file.relative_to(CAREERS).parts) - 1  # index.html = 0 or 1 or 2
        prefix = "../" * depth if depth > 0 else ""

        # Replace full URL assets
        for url, rel in sorted(mapping.items(), key=lambda x: -len(x[0])):
            local_ref = prefix + rel
            content = content.replace(url, local_ref)
            # Without query string
            base = url.split("?")[0]
            if base != url:
                content = content.replace(base, local_ref)

        # Replace relative /_next and /externalpages paths
        for url, rel in sorted(mapping.items(), key=lambda x: -len(x[0])):
            if "recruitcrm.io" in url:
                path = urlparse(url).path
                local_ref = prefix + rel
                content = content.replace(f'"{path}"', f'"{local_ref}"')
                content = content.replace(f"'{path}'", f"'{local_ref}'")
                # static-assets prefix in HTML
                if path.startswith("/static-assets/"):
                    content = content.replace(f'"{path}"', f'"{local_ref}"')

        # Replace _next/image proxy URLs with direct local images
        def replace_next_image(match):
            full = match.group(0)
            for key, img_path in image_map.items():
                if key in full:
                    return f'src="{prefix}{img_path}"'
            return match.group(0)

        content = re.sub(r'src="/_next/image\?[^"]+"', replace_next_image, content)
        content = re.sub(r"srcset=\"/_next/image[^\"]+\"", "", content)  # remove srcset
        content = re.sub(r'imagesrcset="/_next/image[^"]+"', "", content)

        # Direct S3 URLs in content
        for name, s3_url in S3_IMAGES.items():
            local = ASSETS / "images" / (s3_url.split("s3.amazonaws.com/")[1].replace("/", "_").split("?")[0] + ".png")
            if local.exists():
                rel = prefix + str(local.relative_to(CAREERS))
                content = content.replace(s3_url, rel)
                content = content.replace(s3_url.replace("&", "&amp;"), rel)

        if content != original:
            html_file.write_text(content, encoding="utf-8")
            print(f"Rewrote {html_file.relative_to(BASE)}")


def add_search_script():
    """Add client-side job search filter matching original behavior."""
    script = """
<script>
document.addEventListener('DOMContentLoaded', function() {
  var input = document.getElementById('sTest-FilterSearchInput');
  if (!input) return;
  var rows = document.querySelectorAll('ul li, ul > div');
  input.addEventListener('input', function() {
    var q = this.value.toLowerCase().trim();
    document.querySelectorAll('ul > div').forEach(function(row) {
      var text = row.textContent.toLowerCase();
      row.style.display = !q || text.indexOf(q) !== -1 ? '' : 'none';
    });
  });
});
</script>
"""
    listing = CAREERS / "index.html"
    content = listing.read_text(encoding="utf-8")
    if "sTest-FilterSearchInput" in content and "FilterSearchInput" not in content.split("</body>")[0].split("sTest-FilterSearchInput")[1][:500]:
        if "sTest-FilterSearchInput" in content and 'addEventListener' not in content:
            content = content.replace("</body>", script + "\n</body>")
            listing.write_text(content, encoding="utf-8")
            print("Added search filter script to careers/index.html")


async def main():
    print("Extracting asset URLs from careers HTML...")
    urls = set()
    for html in CAREERS.rglob("*.html"):
        urls.update(extract_asset_urls(html.read_text(encoding="utf-8", errors="ignore")))

    print(f"Found {len(urls)} unique asset URLs")
    mapping, failed = await download_all(urls)
    (CAREERS / "asset-mapping.json").write_text(json.dumps(mapping, indent=2))
    if failed:
        (CAREERS / "asset-failed.json").write_text(json.dumps(failed, indent=2))

    print(f"\nDownloaded {len(mapping)} assets, {len(failed)} failed")
    print("Rewriting HTML files...")
    rewrite_html_files(mapping)
    add_search_script()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
