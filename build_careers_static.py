#!/usr/bin/env python3
"""Build standalone static careers page matching recruitcrm.io exactly."""

import asyncio
import json
import re
from pathlib import Path

BASE = Path(__file__).parent
CAREERS = BASE / "careers"
ASSETS = CAREERS / "assets"
JOBS_MANIFEST = CAREERS / "jobs-manifest.json"
DESCRIPTIONS_FILE = CAREERS / "job-descriptions.json"

BUTTON_STYLE = "background-color: rgb(254, 137, 44); color: rgb(255, 255, 255);"

NAV_SCRIPT = """
<script>
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('a').forEach(function(a) {
    if (a.textContent.trim() === 'More Jobs') {
      a.href = '../../index.html';
      a.removeAttribute('target');
    }
  });
  document.querySelectorAll('button').forEach(function(btn) {
    if (btn.textContent.trim() === 'Close') {
      btn.addEventListener('click', function() { window.location.href = '../../index.html'; });
    }
  });
});
</script>
"""


def fix_css_font_paths():
    css_file = ASSETS / "recruitcrm.io/_next/static/css/63c45352ad9c2382.css"
    if not css_file.exists():
        return
    content = css_file.read_text(encoding="utf-8")
    content = re.sub(
        r"url\(/_next/static/media/([^)]+)\)",
        r"url(../../recruitcrm.io/_next/static/media/\1)",
        content,
    )
    content = content.replace(
        "url(/externalpages_v2/landing.svg)",
        "url(../../recruitcrm.io/externalpages_v2/landing.svg)",
    )
    css_file.write_text(content, encoding="utf-8")
    print("Fixed CSS font/image paths")


def job_row(job):
    btn_id = "sTest-ApplyToJobBtn" if job["btnText"] == "Apply To This Job" else "sTest-ViewJobDescription"
    title_escaped = job["title"].replace("&", "&amp;").replace("–", "&ndash;")
    btn_href = (
        f"jobs/{job['slug']}/apply/index.html"
        if job["btnText"] == "Apply To This Job"
        else f"jobs/{job['slug']}/index.html"
    )
    return f"""<div class="job-row"><div class="flex flex-col md:flex-row md:items-center md:justify-between z-10 gap-10 px-6 py-6 max-w-full bg-[#fff] border border-gray-200 border-solid" style="background-color: rgb(255, 255, 255); color: rgb(51, 51, 51);"><div class="flex gap-3 items-start"><div class="flex flex-col mt-1.5"><a id="sTest-jobDetailFileName" href="jobs/{job['slug']}/index.html"><div class="flex items-center"><span class="font-[600] text-[19px] font-sans" style="overflow-wrap: anywhere;">{title_escaped}</span></div></a></div></div><div class="flex flex-col"><a id="{btn_id}" class="flex justify-center md:min-w-[185px] md:max-w-[195px] text-wrap px-5 py-3 text-sm font-medium rounded max-md:px-5" href="{btn_href}" style="{BUTTON_STYLE}">{job['btnText']}</a></div></div></div>"""


def build_page():
    jobs = json.loads(JOBS_MANIFEST.read_text(encoding="utf-8"))
    job_rows = "\n".join(job_row(j) for j in jobs)

    html = f"""<!DOCTYPE html>
<html lang="en" class="bg-white">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Jobs Page</title>
<meta name="description" content="Jobs Page">
<link rel="icon" href="assets/recruitcrm.io/externalpages_v2/favicons/favicon.ico">
<link rel="stylesheet" href="assets/recruitcrm.io/_next/static/css/63c45352ad9c2382.css">
<link rel="stylesheet" href="assets/recruitcrm.io/_next/static/css/46d447d8895e09a1.css">
<link rel="stylesheet" href="assets/recruitcrm.io/_next/static/css/8a3ab71d74223d6e.css">
<link rel="stylesheet" href="assets/recruitcrm.io/_next/static/css/699608b5627cf431.css">
</head>
<body class="__variable_e36cd6">
<div class="h-full">
<main style="background-color:#FFFFFF" class="flex flex-col items-center leading-[150%]">

<nav class="min-h-14 flex items-center justify-center" role="navigation" aria-label="main navigation">
  <div class="p-2">
    <a href="../index.html"><img alt="Ensitech" loading="lazy" decoding="async" class="!relative w-auto !max-w-[200px] !max-h-[70px] !h-auto" style="max-width:200px;max-height:70px;height:auto;" src="assets/images/42438_account_Ensitech_4_logo.png"></a>
  </div>
</nav>

<section style="background-color:#000000" class="flex overflow-hidden relative flex-col justify-center items-center self-stretch px-16 pt-36 pb-32 w-full text-3xl font-bold text-center text-white whitespace-nowrap min-h-[300px] max-md:px-5 max-md:py-10 max-md:max-w-full">
  <img id="sTest-titleBackgroundImage" alt="Background Decorative" fetchpriority="high" decoding="async" class="object-cover object-center-top" style="position:absolute;height:100%;width:100%;left:0;top:0;right:0;bottom:0;object-fit:cover;" src="assets/images/42438_account_Ensitech_4_jobtitlebglogo.png">
  <div class="z-[1] w-full">
    <p style="color:#FFFFFF" class="text-[30px] mb-2 break-words text-wrap" id="sTest-jobPageTitle">Ensitech Jobs</p>
    <p style="color:#FFFFFF" class="text-[19px] break-words text-wrap m-auto mt-1 font-normal w-1/2" id="sTest-jobPageSubTitle">Careers</p>
  </div>
  <div style="background-color:#000000" class="absolute top-0 left-0 w-full h-full opacity-50"></div>
</section>

<section class="flex flex-col justify-center px-4 py-3.5 text-sm whitespace-nowrap rounded-md bg-zinc-100 md:w-[79%] w-11/12 mt-10 text-neutral-700 text-opacity-30 max-md:max-w-full">
  <div class="justify-center relative flex w-full h-full items-start bg-white rounded-sm border border-solid border-slate-200 max-md:max-w-full">
    <img id="sTest-FilterSearchIcon" alt="Search" loading="lazy" width="20" height="20" decoding="async" class="pt-2 ml-2 absolute left-0.5" style="color:transparent" src="assets/recruitcrm.io/externalpages_v2/icons/magnify.svg">
    <input type="text" class="w-full px-10 py-2 focus:outline-blue-400 focus:outline-1 text-gray-700" id="sTest-FilterSearchInput" value="" placeholder="">
  </div>
</section>

<ul class="md:w-[79%] w-11/12 mt-10" id="job-list">
{job_rows}
</ul>

<footer class="w-full font-sans position-static mt-8 border-t-slate-400 h-14 bg-white flex justify-center items-center text-[13px] tracking-normal">
  <div class="pt-3" id="sTest-footerTxt">
    <span class="text-gray-700"></span>
    <a target="_blank" href="https://recruitcrm.io/"><span class="ml-1 text-blue-500 font-bold"></span></a>
    <a target="_blank" href="https://recruitcrm.io/"><span class="ml-1 text-blue-500 font-bold"></span></a>
  </div>
</footer>

</main>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {{
  var input = document.getElementById('sTest-FilterSearchInput');
  if (!input) return;
  input.addEventListener('input', function() {{
    var q = this.value.toLowerCase().trim();
    document.querySelectorAll('.job-row').forEach(function(row) {{
      var text = row.textContent.toLowerCase();
      row.style.display = !q || text.indexOf(q) !== -1 ? '' : 'none';
    }});
  }});
}});
</script>
</body>
</html>"""

    out = CAREERS / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"Built static careers page: {out} ({len(html)} bytes, {len(jobs)} jobs)")


async def scrape_descriptions(jobs):
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Playwright not available, skipping description scrape")
        return {}

    descriptions = {}
    if DESCRIPTIONS_FILE.exists():
        descriptions = json.loads(DESCRIPTIONS_FILE.read_text(encoding="utf-8"))

    missing = [j for j in jobs if j["id"] not in descriptions]
    if not missing:
        print(f"Using cached descriptions ({len(descriptions)} jobs)")
        return descriptions

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for job in missing:
            page = await browser.new_page()
            url = job["original_url"]
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                await page.wait_for_timeout(5000)
                html = await page.evaluate("""() => {
                    const iframe = document.getElementById('view_html_iframe');
                    if (!iframe) return '';
                    try {
                        const doc = iframe.contentDocument || iframe.contentWindow.document;
                        return doc ? doc.body.innerHTML : '';
                    } catch(e) { return ''; }
                }""")
                descriptions[job["id"]] = html
                print(f"  Scraped: {job['title'][:50]} ({len(html)} chars)")
            except Exception as e:
                print(f"  Failed: {job['title'][:50]}: {e}")
                descriptions[job["id"]] = ""
            await page.close()
        await browser.close()

    DESCRIPTIONS_FILE.write_text(json.dumps(descriptions, ensure_ascii=False, indent=2), encoding="utf-8")
    return descriptions


def fix_job_pages(jobs, descriptions):
    for job in jobs:
        job_file = CAREERS / job["local_path"]
        if not job_file.exists():
            continue
        html = job_file.read_text(encoding="utf-8")
        html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
        html = re.sub(r"<script[^>]*/>", "", html)
        html = re.sub(r'<link rel="preload" as="script"[^>]*>', "", html)
        html = re.sub(r"<next-route-announcer[^>]*></next-route-announcer>", "", html)

        desc = descriptions.get(job["id"], "")
        if desc:
            iframe_pat = r'<iframe id="view_html_iframe"[^>]*></iframe>'
            replacement = (
                f'<div id="view_html_iframe" class="w-full min-h-52 bg-white p-0 md:p-4 job-description">'
                f"{desc}</div>"
            )
            html = re.sub(iframe_pat, replacement, html)

        html = html.replace('href="https://ensitech.com/careers"', 'href="../../index.html"')
        html = html.replace('<a href="#" class="p-2">', '<a href="../../../index.html" class="p-2">')
        html = re.sub(
            r'<button class="text-white text-sm font-sans font-bold py-1\.5 px-3 md:my-6 rounded mb-3" style="background-color: rgb\(254, 137, 44\); color: rgb\(255, 255, 255\);">Apply To This Job</button>',
            '<a href="apply/index.html" class="text-white text-sm font-sans font-bold py-1.5 px-3 md:my-6 rounded mb-3 inline-block text-center" style="background-color: rgb(254, 137, 44); color: rgb(255, 255, 255); text-decoration: none;">Apply To This Job</a>',
            html,
        )
        html = html.replace("<body", NAV_SCRIPT + "\n<body", 1)
        job_file.write_text(html, encoding="utf-8")
    print(f"Fixed {len(jobs)} job detail pages")


async def main():
    fix_css_font_paths()
    build_page()
    jobs = json.loads(JOBS_MANIFEST.read_text(encoding="utf-8"))
    descriptions = await scrape_descriptions(jobs)
    fix_job_pages(jobs, descriptions)

    from build_apply_pages import main as build_apply
    build_apply()


if __name__ == "__main__":
    asyncio.run(main())
