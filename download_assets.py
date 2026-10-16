#!/usr/bin/env python3
"""Download all CSS, JS, images, fonts, and icons from ensitech.com."""

import asyncio
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse, unquote

from playwright.async_api import async_playwright

BASE = Path(__file__).parent
ASSETS = BASE / "assets"

ASSET_EXTENSIONS = {
    "css": (".css",),
    "js": (".js",),
    "images": (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".cur"),
    "fonts": (".woff", ".woff2", ".ttf", ".eot", ".otf"),
}

ALLOWED_HOSTS = {
    "ensitech.com",
    "www.ensitech.com",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
}


def normalize_url(url: str):
    url = url.strip().strip("\"'")
    if not url or url.startswith(("data:", "blob:", "javascript:")):
        return None
    if url.startswith("//"):
        url = "https:" + url
    if url.startswith("/"):
        url = "https://ensitech.com" + url
    parsed = urlparse(url)
    if parsed.netloc not in ALLOWED_HOSTS:
        return None
    return url.split("#")[0]


def url_to_local_path(url: str) -> Path:
    parsed = urlparse(url)
    path = unquote(parsed.path.lstrip("/"))
    if parsed.netloc == "fonts.googleapis.com":
        safe = re.sub(r"[^\w\-.]", "_", parsed.path + parsed.query)[:120]
        return ASSETS / "fonts.googleapis.com" / f"{safe}.css"
    if parsed.netloc == "fonts.gstatic.com":
        return ASSETS / "fonts.gstatic.com" / path
    return ASSETS / "ensitech.com" / path


def extract_urls_from_html_files() -> set[str]:
    patterns = [
        r"https?://(?:www\.)?ensitech\.com/[^\s\"'<>\)]+",
        r"//ensitech\.com/[^\s\"'<>\)]+",
        r"https?://fonts\.googleapis\.com/[^\s\"'<>\)]+",
        r"https?://fonts\.gstatic\.com/[^\s\"'<>\)]+",
    ]
    urls: set[str] = set()
    for html in BASE.rglob("*.html"):
        text = html.read_text(encoding="utf-8", errors="ignore")
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                raw = match.group(0).rstrip("\"');, ")
                normalized = normalize_url(raw)
                if normalized:
                    urls.add(normalized)
    return urls


def categorize_url(url: str) -> str:
    path = urlparse(url).path.lower()
    for category, extensions in ASSET_EXTENSIONS.items():
        if any(path.endswith(ext) or f"{ext}?" in url.lower() for ext in extensions):
            return category
    if "fonts.googleapis.com" in url:
        return "css"
    if "fonts.gstatic.com" in url:
        return "fonts"
    return "other"


def url_to_site_relative(url: str) -> str:
    """Convert URL to relative path from any HTML file at site root."""
    local = url_to_local_path(url)
    return str(local.relative_to(BASE)).replace("\\", "/")


async def download_assets(urls: set[str]) -> dict:
    ASSETS.mkdir(parents=True, exist_ok=True)
    mapping: dict[str, str] = {}
    failed: list[str] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        )
        # Visit homepage first to get past Sucuri
        page = await context.new_page()
        await page.goto("https://ensitech.com/", wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(2000)

        sorted_urls = sorted(urls)
        total = len(sorted_urls)
        for i, url in enumerate(sorted_urls, 1):
            local_path = url_to_local_path(url)
            if local_path.exists() and local_path.stat().st_size > 0:
                mapping[url] = url_to_site_relative(url)
                continue

            local_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                response = await context.request.get(url, timeout=30000)
                if response.ok:
                    body = await response.body()
                    local_path.write_bytes(body)
                    mapping[url] = url_to_site_relative(url)
                    print(f"[{i}/{total}] OK {url} -> {local_path.relative_to(BASE)}")
                else:
                    failed.append(url)
                    print(f"[{i}/{total}] FAIL {response.status} {url}")
            except Exception as exc:
                failed.append(url)
                print(f"[{i}/{total}] ERROR {url}: {exc}")

        await browser.close()

    return {"mapping": mapping, "failed": failed}


def rewrite_html_files(mapping: dict[str, str]) -> int:
    updated = 0
    # Sort longest URLs first to avoid partial replacements
    replacements = sorted(mapping.items(), key=lambda x: -len(x[0]))

    for html in BASE.rglob("*.html"):
        content = html.read_text(encoding="utf-8", errors="ignore")
        original = content
        depth = len(html.parent.relative_to(BASE).parts)
        prefix = "../" * depth if depth > 0 else ""

        for url, rel_from_root in replacements:
            local_ref = prefix + rel_from_root
            # Replace various escaped forms
            content = content.replace(url, local_ref)
            content = content.replace(url.replace("/", "\\/"), local_ref.replace("/", "\\/"))
            content = content.replace("//" + url.split("://", 1)[1], local_ref)
            if url.startswith("https://ensitech.com"):
                content = content.replace(
                    url.replace("https://ensitech.com", "//ensitech.com"), local_ref
                )

        if content != original:
            html.write_text(content, encoding="utf-8")
            updated += 1
            print(f"Rewrote: {html.relative_to(BASE)}")

    return updated


async def main():
    print("Extracting asset URLs from HTML files...")
    urls = extract_urls_from_html_files()

    # Filter to actual assets only
    asset_urls = {u for u in urls if categorize_url(u) != "other"}
    print(f"Found {len(asset_urls)} asset URLs to download")

    manifest = {cat: [] for cat in list(ASSET_EXTENSIONS) + ["other"]}
    for url in sorted(urls):
        manifest[categorize_url(url)].append(url)
    (BASE / "asset-manifest.json").write_text(json.dumps(manifest, indent=2))

    print("Downloading assets...")
    result = await download_assets(asset_urls)
    (BASE / "asset-mapping.json").write_text(json.dumps(result["mapping"], indent=2))

    print(f"\nDownloaded: {len(result['mapping'])}")
    print(f"Failed: {len(result['failed'])}")

    if result["failed"]:
        (BASE / "asset-failed.json").write_text(json.dumps(result["failed"], indent=2))

    print("\nRewriting HTML files to use local assets...")
    updated = rewrite_html_files(result["mapping"])
    print(f"Updated {updated} HTML files")

    # Parse downloaded CSS for additional assets (fonts, images)
    print("\nChecking CSS files for nested assets...")
    css_urls = set()
    for css_file in ASSETS.rglob("*.css"):
        text = css_file.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r"url\(['\"]?([^'\")]+)['\"]?\)", text):
            raw = match.group(1)
            if raw.startswith("../") or raw.startswith("./"):
                base_url = "https://ensitech.com/" + str(css_file.relative_to(ASSETS / "ensitech.com").parent).replace("\\", "/") + "/"
                from urllib.parse import urljoin
                full = urljoin(base_url, raw)
            else:
                full = raw
            normalized = normalize_url(full)
            if normalized and normalized not in result["mapping"]:
                css_urls.add(normalized)

    if css_urls:
        print(f"Found {len(css_urls)} additional assets in CSS, downloading...")
        extra = await download_assets(css_urls)
        result["mapping"].update(extra["mapping"])
        (BASE / "asset-mapping.json").write_text(json.dumps(result["mapping"], indent=2))
        rewrite_html_files(result["mapping"])

        # Rewrite paths inside CSS files
        for css_file in ASSETS.rglob("*.css"):
            text = css_file.read_text(encoding="utf-8", errors="ignore")
            original = text
            for url, rel in sorted(result["mapping"].items(), key=lambda x: -len(x[0])):
                text = text.replace(url, rel)
                if url.startswith("https://ensitech.com"):
                    text = text.replace(url.replace("https://ensitech.com", "//ensitech.com"), rel)
            if text != original:
                css_file.write_text(text, encoding="utf-8")

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
