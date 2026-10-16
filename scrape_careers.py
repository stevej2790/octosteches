#!/usr/bin/env python3
"""Scrape RecruitCRM careers portal and individual job pages."""

import asyncio
import json
import re
from pathlib import Path
from urllib.parse import quote

from playwright.async_api import async_playwright

BASE = Path(__file__).parent
CAREERS_DIR = BASE / "careers"
JOBS_DIR = CAREERS_DIR / "jobs"

CAREERS_URL = "https://recruitcrm.io/jobs/Ensitech_Careers"


def slugify(title: str, job_id: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return f"{slug}-{job_id[-8:]}"


async def get_all_jobs(page):
    await page.goto(CAREERS_URL, wait_until="networkidle", timeout=60000)
    await page.wait_for_timeout(3000)
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(2000)

    return await page.evaluate(
        """() => {
        const results = [];
        const seen = new Set();
        document.querySelectorAll('a').forEach(a => {
            const btn = a.textContent.trim();
            if (!btn.match(/View Job|Apply To This Job/i)) return;
            const href = a.href;
            if (seen.has(href)) return;
            seen.add(href);
            let title = '';
            let el = a.parentElement;
            for (let i = 0; i < 6 && el; i++) {
                for (const child of el.children) {
                    if (child === a || child.contains(a)) continue;
                    const t = child.textContent.trim();
                    if (t && t.length > 5 && t.length < 200 && !t.match(/View Job|Apply To/i)) {
                        title = t.split('\\n')[0].trim();
                        break;
                    }
                }
                if (title) break;
                el = el.parentElement;
            }
            const id = href.split('/apply/')[1]?.split('?')[0] || '';
            results.push({title, href, btnText: btn, id});
        });
        return results;
    }"""
    )


async def scrape():
    CAREERS_DIR.mkdir(parents=True, exist_ok=True)
    JOBS_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        print("Fetching careers listing...")
        jobs = await get_all_jobs(page)
        print(f"Found {len(jobs)} jobs")

        # Save careers listing HTML
        listing_html = await page.content()
        (CAREERS_DIR / "index.html").write_text(listing_html, encoding="utf-8")
        print(f"Saved careers/index.html ({len(listing_html)} bytes)")

        job_manifest = []
        for i, job in enumerate(jobs, 1):
            slug = slugify(job["title"] or f"job-{i}", job["id"])
            job_dir = JOBS_DIR / slug
            job_dir.mkdir(parents=True, exist_ok=True)

            print(f"[{i}/{len(jobs)}] Scraping: {job['title']}")
            try:
                await page.goto(job["href"], wait_until="networkidle", timeout=60000)
                await page.wait_for_timeout(2500)
                html = await page.content()
                (job_dir / "index.html").write_text(html, encoding="utf-8")

                page_title = await page.title()
                job_manifest.append(
                    {
                        "title": job["title"] or page_title,
                        "slug": slug,
                        "id": job["id"],
                        "btnText": job["btnText"],
                        "original_url": job["href"],
                        "local_path": f"jobs/{slug}/index.html",
                    }
                )
                print(f"  Saved jobs/{slug}/index.html")
            except Exception as exc:
                print(f"  ERROR: {exc}")

        (CAREERS_DIR / "jobs-manifest.json").write_text(
            json.dumps(job_manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        await browser.close()

    print(f"\nDone! {len(job_manifest)} job pages saved.")


if __name__ == "__main__":
    asyncio.run(scrape())
