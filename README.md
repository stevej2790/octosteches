# Ensitech Website Recreation

A local recreation of [ensitech.com](https://ensitech.com/) with identical HTML, CSS, JavaScript, and page structure scraped from the original site.

## Pages Included

| Page | Local Path |
|------|------------|
| Landing Page | `index.html` |
| About Us | `about-us/index.html` |
| Staff Augmentation | `staff-augmentation/index.html` |
| Software Development | `software-development/index.html` |
| Cloud Operations | `cloud-operations/index.html` |
| Artificial Intelligence | `artificial-intelligence/index.html` |
| Big Data Analytics | `big-data-analytics/index.html` |
| Careers | `careers/index.html` (17 job listings + individual job detail pages, local CSS/JS/images) |
| Case Studies | `case-study/index.html` + 7 individual case studies |
| Blog | `blogs/index.html` + 10 blog posts |
| About COVID-19 | `about-covid-19/index.html` |
| Privacy Policy | `privacy-policy/index.html` |
| Terms of Services | `terms-of-services/index.html` |
| SGSI Policy | `politica-del-sistema-de-gestion-de-la-seguridad-de-la-informacion-sgsi/index.html` |
| Contact Us | `contact-us/index.html` |

## Navigation

- **Services** dropdown (on hover): Staff Augmentation, Software Development, Cloud Operations, Artificial Intelligence
- **Resources** dropdown (on hover): Case Studies, Blog
- **Careers** links to external RecruitCRM portal
- Footer links: About COVID-19, Privacy Policy, Terms of Services, SGSI Policy

## Instagram Links (from About Us page)

See `instagram-links.txt` for all Instagram links found on the About Us page.

## Running Locally

```bash
python3 server.py
```

Then open [http://localhost:8888](http://localhost:8888) in your browser.

Alternatively, open `index.html` directly in a browser (some features may require a local server).

## Assets (Local)

All CSS, JavaScript, images, fonts, and icons have been downloaded locally to the `assets/` folder:

| Type | Count |
|------|-------|
| Images (PNG/JPG/SVG) | ~247 |
| JavaScript | 40 |
| Fonts (WOFF2/WOFF/TTF) | ~127 |
| Google Fonts CSS | 1 |
| Inline CSS extracts | 35 (in `assets/inline-css/`) |

**Total: 420+ asset files (~35 MB)**

Run `python3 download_assets.py` to re-download any missing Ensitech assets.
Run `python3 download_careers_assets.py` to re-download careers portal assets.

Asset mappings are saved in `asset-manifest.json` and `asset-mapping.json`.

## Notes

- Main page CSS is inlined in each HTML file (`<style id="wpr-usedcss">`) — copies also saved in `assets/inline-css/`.
- Third-party services (Google Analytics, reCAPTCHA, WordPress admin-ajax) still reference external URLs as on the original site.
- Cookie notice, carousels, dropdown menus, and mobile burger menu work via the locally stored Elementor/WordPress JavaScript.
