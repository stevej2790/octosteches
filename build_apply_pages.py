#!/usr/bin/env python3
"""Build local apply form pages for each job and wire Apply buttons."""

import json
import random
import re
from pathlib import Path

BASE = Path(__file__).parent
CAREERS = BASE / "careers"
JOBS_MANIFEST = CAREERS / "jobs-manifest.json"

ASSET = "../../../assets"
THANKYOU_ASSET = "../../../../assets"
BUTTON_STYLE = "background-color: rgb(254, 137, 44); color: rgb(255, 255, 255);"

SALARY_TYPES = ["Annual Salary", "Monthly Salary", "Hourly Salary", "Weekly Salary"]
EXPERIENCE = [f"{i} Year" if i == 1 else f"{i} Years" for i in range(0, 21)]
LANGUAGES = [
    "English", "Spanish", "French", "German", "Portuguese", "Italian",
    "Chinese", "Japanese", "Korean", "Arabic", "Hindi", "Russian",
]
PROFICIENCY = ["Native", "Fluent", "Advanced", "Intermediate", "Basic"]
MATCH_OPTIONS = ["Strong Match", "Good Match", "Partial Match", "No Match"]


def dropdown(btn_id, label, options, placeholder=None, extra_class="text-xs"):
    placeholder = placeholder or label
    items = "".join(
        f'<div data-value="{opt}" role="option">{opt}</div>' for opt in options
    )
    return f"""<div class="space-y-2"><label class="text-xs leading-none font-bold text-[#464646]">{label}</label>
<div class="rcrm-dropdown">
<button class="inline-flex items-center whitespace-nowrap font-medium border border-slate-200 bg-white hover:bg-slate-100 h-10 px-4 py-2 {extra_class} w-full rounded justify-between" type="button" id="{btn_id}" data-dropdown>
<span class="text-slate-500" data-label data-placeholder="{placeholder}">{placeholder}</span>
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="lucide lucide-chevrons-up-down ml-2 h-4 w-4 shrink-0 opacity-50"><path d="m7 15 5 5 5-5"></path><path d="m7 9 5-5 5 5"></path></svg>
</button>
<div class="rcrm-dropdown-menu">{items}</div>
</div></div>"""


def text_input(field_id, label, name="", placeholder="", required=False, input_type="text", half=True):
    req = '<span class="text-red-500">*</span>' if required else ""
    width = "md:w-1/2" if half else "w-full"
    return f"""<div class="{width} p-3 min-h-[6rem] md:flex-none"><div class="space-y-2">
<label class="text-xs leading-none font-bold text-[#464646]">{label}{req}</label>
<input class="flex h-10 w-full rounded border border-slate-200 bg-white px-3 py-2 text-sm placeholder:text-slate-300 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-customBlue" id="{field_id}" name="{name}" placeholder="{placeholder}" type="{input_type}">
</div></div>"""


def file_upload(field_id, label, required=False):
    req = '<span class="text-red-500">*</span>' if required else ""
    return f"""<div class="w-full p-3 min-h-[6rem] md:flex-none"><div class="space-y-2">
<label class="text-xs leading-none font-bold text-[#464646]">{label}{req}</label>
<div class="filecontrol flex items-center">
<input id="{field_id}" accept=".docx,.rtf,.doc,.pdf" type="file" style="display:none">
<button type="button" class="border rounded border-slate-200 bg-white h-10 flex items-center px-3" data-file-trigger="{field_id}" style="font-size:13px;font-weight:500">
<img alt="" width="20" height="20" class="mr-2" src="{ASSET}/recruitcrm.io/externalpages_v2/icons/upload.svg"><span>Upload File</span>
</button></div></div></div>"""


def section(title, subtitle, body):
    return f"""<div><div class="flex flex-col md:flex-row pt-6 pb-6" style="border-bottom:1px solid rgb(206,211,218)">
<div class="md:w-1/4 p-2"><h2 style="color:rgb(42,51,61);font-size:18px;font-weight:500;margin-bottom:5px">{title}</h2>
<p style="font-size:14px;color:rgb(138,162,173)">{subtitle}</p></div>
<div class="w-full md:w-3/4"><div class="block md:flex md:flex-wrap">{body}</div></div></div></div>"""


def build_apply_html(job):
    title = job["title"].replace("&", "&amp;").replace("–", "&ndash;")
    title_plain = job["title"]
    submit_delay_ms = random.randint(300, 700)

    personal = (
        text_input("sTest-candidateFirstName", "First Name", "firstname", "Tony", required=True)
        + text_input("sTest-candidateLastName", "Last Name", "lastname", "Jordan", required=True)
        + text_input("sTest-candidateEmail", "Email", "emailid", "jordan@abc.com", required=True)
        + text_input("sTest-candidateMobile", "Phone", "contactnumber", "+1-202-555-0194")
        + text_input("sTest-candidateCountry", "Country", "", "United States", required=True)
        + text_input("sTest-candidateLocality", "Locality", "", "Manhatten", required=True)
        + text_input("sTest-candidatePostalCode", "Postal Code", "", "123456")
    )

    education = """<div class="w-full md:w-3/4 p-2"><div id="education-history-container"></div>
<div class="w-full mb-4"><button type="button" id="sTest-addEducationHistoryBtn" class="w-full p-3 button mt-2"
style="border-radius:2px;text-align:center;cursor:pointer;border:1px solid rgb(206,211,218);background-color:rgb(252,252,252);display:flex;align-items:center;justify-content:center">
<img alt="" width="15" height="15" class="mr-1" src="{ASSET}/recruitcrm.io/externalpages_v2/icons/plus.svg">
<p class="text-sm mr-2">Add Education History</p></button></div></div>""".format(ASSET=ASSET)

    employment = (
        f'<div class="md:w-1/2 p-3 min-h-[6rem]">{dropdown("sTest-candidateSalaryType", "Salary Type", SALARY_TYPES, "Annual Salary")}</div>'
        + text_input("sTest-candidateAnnualSalary", "Current Salary", "currentsalary", "500000", input_type="number")
        + text_input("sTest-candidateExpectatedSalary", "Salary Expectation", "salaryexpectation", "800000", input_type="number")
        + text_input("sTest-candidateEmploymentStatus", "Employment Status", "currentstatus", "Unemployed")
        + text_input("sTest-candidatePosition", "Title", "position", "Java Developer")
        + f'<div class="md:w-1/2 p-3 min-h-[6rem]">{dropdown("sTest-candidateRelevantExp", "Relevant Experience", EXPERIENCE, "0 Year")}</div>'
        + text_input("sTest-candidateNoticePeriod", "Notice Period", "noticeperiod", "60", input_type="number")
        + f"""<div class="md:w-1/2 p-3 min-h-[6rem]"><div class="space-y-2">
<label class="text-xs leading-none font-bold text-[#464646]">Available From</label>
<input type="date" id="sTest-candidateAvailableFromInput" style="position:absolute;opacity:0;pointer-events:none;width:0;height:0">
<button class="inline-flex items-center border border-slate-200 bg-white hover:bg-slate-100 h-10 px-4 py-2 w-full rounded text-left text-xs" type="button" id="sTest-candidateAvailableFrom" data-date-trigger="sTest-candidateAvailableFromInput">
<span class="text-slate-500" data-label>Click To Select</span>
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="lucide lucide-calendar ml-auto h-4 w-4 opacity-50"><path d="M8 2v4"></path><path d="M16 2v4"></path><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M3 10h18"></path></svg>
</button></div></div>"""
    )

    language_row = f"""<div class="language-row flex items-center space-x-4 mb-1">
<div class="w-5/12"><div class="rcrm-dropdown m-3">
<button class="inline-flex items-center border border-slate-200 bg-white h-10 px-4 py-2 w-5/6 m-3 justify-between rounded text-sm" type="button" data-dropdown>
<span class="text-slate-500" data-label data-placeholder="Select Language">Select Language</span>
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="ml-2 h-4 w-4 opacity-50"><path d="m7 15 5 5 5-5"></path><path d="m7 9 5-5 5 5"></path></svg></button>
<div class="rcrm-dropdown-menu">{"".join(f'<div data-value="{l}" role="option">{l}</div>' for l in LANGUAGES)}</div></div></div>
<div class="w-5/12"><div class="rcrm-dropdown m-3">
<button class="inline-flex items-center border border-slate-200 bg-white h-10 px-4 py-2 w-5/6 m-3 justify-between rounded text-sm" type="button" data-dropdown>
<span class="text-slate-500" data-label data-placeholder="Select Proficiency Level">Select Proficiency Level</span>
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="ml-2 h-4 w-4 opacity-50"><path d="m7 15 5 5 5-5"></path><path d="m7 9 5-5 5 5"></path></svg></button>
<div class="rcrm-dropdown-menu">{"".join(f'<div data-value="{p}" role="option">{p}</div>' for p in PROFICIENCY)}</div></div></div>
<div class="flex justify-center items-center"><button class="inline-flex items-center justify-center border border-slate-200 bg-white h-10 w-10 rounded" type="button" title="Remove">
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="h-5 w-5"><path d="M20 5H9l-7 7 7 7h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2Z"></path><line x1="18" x2="12" y1="9" y2="15"></line><line x1="12" x2="18" y1="9" y2="15"></line></svg></button></div></div>"""

    resume_skills = (
        file_upload("sTest-uploadFile-sTest-candidateResume", "Resume", required=True)
        + f"""<div class="w-full p-3 min-h-[6rem]"><div class="space-y-2">
<div class="flex items-center border-b pb-2 w-full">
<div class="w-5/12 flex"><label class="block text-xs font-medium">Language</label></div>
<div class="w-5/12 pl-4 flex"><label class="block text-xs font-medium">Proficiency Level</label></div>
<div class="w-1/6 flex justify-center"><button type="button" id="sTest-addLanguageBtn" class="text-blue-500 rounded-full p-2 border hover:text-white">
<img alt="" width="15" height="15" src="{ASSET}/recruitcrm.io/externalpages_v2/icons/plus.svg"></button></div></div>
<div id="language-rows">{language_row}</div></div></div>"""
        + f"""<div class="w-full p-3 min-h-[6rem]"><div class="space-y-2">
<label class="text-xs leading-none font-bold text-[#464646]">Skills</label>
<div id="skills-tags" class="flex flex-wrap gap-2 rounded-md mb-2"></div>
<input class="flex h-10 w-full rounded border border-slate-200 bg-white px-3 py-2 text-sm sm:min-w-[450px]" id="sTest-candidateSkillsInput" placeholder="Add Your Skill" type="text">
</div></div>"""
    )

    social = text_input("sTest-candidateLinkedinTxt", "Linkedin Profile", "profilelinkedin", "https://www.linkedin.com/ryancooper", half=True)

    associated = ""
    for i, label in enumerate([
        ("Main Skills Vetting", "Main Skills Match"),
        ("Soft Skills Match", "Soft Skills Match"),
        ("Seniority Match", "Seniority Match"),
        ("Salary + Benefits Match", "Salary + Benefits Match"),
        ("Language Match", "Language Match"),
    ]):
        associated += f'<div class="w-full p-3 min-h-[6rem]">{dropdown(f"sTest-jobAssociated-{i}", label[0], MATCH_OPTIONS, label[1], "text-sm")}</div>'

    form_body = (
        section("Personal Information", "Your Name & Contact Information", personal)
        + f"""<div><div class="flex flex-col md:flex-row pt-6 pb-6" style="border-bottom:1px solid rgb(206,211,218)">
<div class="md:w-1/4 p-2"><h2 style="color:rgb(54,54,54);font-size:15px;font-weight:500">Education History</h2>
<p style="font-size:14px;color:rgb(138,162,173)">Education History We Need</p></div>{education}</div></div>"""
        + section("Employment Details", "Your Professional Work History", employment)
        + section("Resume &amp; Skills", "Upload Your CV or Resume", resume_skills)
        + section("Social Media Details", "Links To Your Public Profiles Online", social)
        + section("Job Associated Files", "Job Associated Files", associated)
        + f"""<div class="w-full text-center mt-8 mb-8">
<div class="text-red-500 mb-4" id="apply-error-box" style="font-size:14px;display:none"></div>
<button type="submit" id="submit_candidate2" class="text-[13px] mb-4 py-4 min-w-40 rounded button btn-job-apply inline-flex items-center justify-center gap-2" style="{BUTTON_STYLE}padding-left:2rem;padding-right:2rem;min-height:48px">
<span class="submit-btn-label">Submit Your Application</span>
<span class="submit-btn-loader" role="status" aria-label="Loading"></span>
</button></div>"""
    )

    return f"""<!DOCTYPE html>
<html lang="en" class="bg-white">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Apply To {title}</title>
<link rel="icon" href="{ASSET}/recruitcrm.io/externalpages_v2/favicons/favicon.ico">
<link rel="stylesheet" href="{ASSET}/recruitcrm.io/_next/static/css/63c45352ad9c2382.css">
<link rel="stylesheet" href="{ASSET}/recruitcrm.io/_next/static/css/46d447d8895e09a1.css">
<link rel="stylesheet" href="{ASSET}/recruitcrm.io/_next/static/css/8a3ab71d74223d6e.css">
<link rel="stylesheet" href="{ASSET}/recruitcrm.io/_next/static/css/699608b5627cf431.css">
<style>
.rcrm-dropdown {{ position:relative; }}
.rcrm-dropdown-menu {{ display:none; position:absolute; top:100%; left:0; right:0; z-index:50; background:#fff; border:1px solid rgb(226,232,240); border-radius:4px; max-height:200px; overflow-y:auto; box-shadow:0 4px 6px rgba(0,0,0,.08); }}
.rcrm-dropdown-menu.open {{ display:block; }}
.rcrm-dropdown-menu [data-value] {{ padding:8px 12px; cursor:pointer; font-size:13px; }}
.rcrm-dropdown-menu [data-value]:hover {{ background:rgb(248,250,252); }}
.job-description img {{ max-width:100%; }}
#submit_candidate2:disabled {{ opacity:0.85; cursor:not-allowed; }}
#submit_candidate2.loading .submit-btn-label {{ display:none; }}
.submit-btn-loader {{
  display:none;
  width:22px;
  height:22px;
  border-radius:50%;
  flex-shrink:0;
  background:conic-gradient(from 0deg, rgba(255,255,255,0) 0deg, rgba(255,255,255,0.15) 50deg, rgba(255,255,255,0.55) 180deg, #ffffff 280deg, #ffffff 310deg, rgba(255,255,255,0) 360deg);
  -webkit-mask:radial-gradient(farthest-side, transparent calc(100% - 2.5px), #000 calc(100% - 2.5px));
  mask:radial-gradient(farthest-side, transparent calc(100% - 2.5px), #000 calc(100% - 2.5px));
  animation:submit-btn-spin 0.85s linear infinite;
}}
#submit_candidate2.loading .submit-btn-loader {{ display:inline-block; }}
@keyframes submit-btn-spin {{ to {{ transform:rotate(360deg); }} }}
.field-error {{ color:#ef4444; font-size:12px; margin-top:4px; }}
.input-invalid {{ border-color:#ef4444 !important; }}
</style>
</head>
<body class="__variable_e36cd6">
<div>
<nav class="min-h-28 h-[120px] mb-3 md:mb-0" style="background-color:#fff;background:transparent">
<div class="min-h-28 lg:flex lg:justify-around lg:items-center">
<div class="flex justify-center lg:block"><a href="../../../../index.html" class="p-2">
<img alt="Ensitech" class="!relative w-auto !max-w-[200px] !max-h-[70px] !h-auto" style="max-width:200px;max-height:70px;height:auto" src="{ASSET}/images/42438_account_Ensitech_4_logo.png"></a></div>
<div class="flex justify-center">
<a href="../../index.html" class="cursor-pointer flex items-center px-3 py-1.5 text-center whitespace-nowrap text-xs rounded-sm font-medium font-roboto bg-white border border-gray-300 text-gray-800 mr-3 h-10">
<img alt="More Job" width="15" height="15" class="mr-2" src="{ASSET}/recruitcrm.io/externalpages_v2/icons/arrow-right.svg">More Jobs</a>
<a href="../index.html" class="cursor-pointer flex items-center px-3 py-1.5 text-center whitespace-nowrap text-xs rounded-sm font-medium font-roboto bg-white border border-gray-300 text-gray-800 mr-3 h-10 w-fit">
<img alt="Job Description" width="15" height="15" class="mr-2" src="{ASSET}/recruitcrm.io/externalpages_v2/icons/file-presentation-box.svg"><span>View Job Description</span></a>
</div></div></nav>

<section id="sTest-jobApplyBanner" style="background-color:#000000" class="flex overflow-hidden relative flex-col justify-center items-center self-stretch px-16 pt-36 pb-32 w-full text-3xl font-bold text-center text-white max-h-[350px] min-h-[300px] max-md:px-5 max-md:py-10">
<img alt="Background Decorative" class="object-cover object-center-top" style="position:absolute;height:100%;width:100%;left:0;top:0;right:0;bottom:0;object-fit:cover" src="{ASSET}/images/42438_account_Ensitech_4_jobtitlebglogo.png">
<div class="container text-center pt-4 pb-3 z-[1] text-wrap">
<img id="sTest-accountLogo" alt="Ensitech" class="!relative mx-auto mb-2 w-auto !max-w-[200px] !max-h-[70px] !h-auto" style="max-width:200px;max-height:70px;height:auto" src="{ASSET}/images/42438_account_Ensitech_4_logo.png">
<h1 class="break-words" style="color:#FFFFFF;font-size:30px;font-weight:700">{title}</h1>
</div>
<div style="background-color:#000000" class="absolute top-0 left-0 w-full h-full opacity-50"></div>
</section>

<section class="relative md:w-[75%] m-auto">
<div class="container mx-auto px-6"><div class="flex flex-wrap mt-4">
<div class="w-full"><div class="font-sans">
<form id="sTest-applyForm" class="pt-12" data-submit-delay="{submit_delay_ms}">{form_body}</form>
</div></div></div></div>
</section>


</div>
<script src="{ASSET}/apply-form.js"></script>
</body>
</html>"""


def build_thank_you_html(job):
    title = job["title"].replace("&", "&amp;").replace("–", "&ndash;")
    return f"""<!DOCTYPE html>
<html lang="en" class="bg-white">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thank You - {title}</title>
<link rel="icon" href="{THANKYOU_ASSET}/recruitcrm.io/externalpages_v2/favicons/favicon.ico">
<link rel="stylesheet" href="{THANKYOU_ASSET}/recruitcrm.io/_next/static/css/63c45352ad9c2382.css">
<link rel="stylesheet" href="{THANKYOU_ASSET}/recruitcrm.io/_next/static/css/46d447d8895e09a1.css">
<link rel="stylesheet" href="{THANKYOU_ASSET}/recruitcrm.io/_next/static/css/8a3ab71d74223d6e.css">
<link rel="stylesheet" href="{THANKYOU_ASSET}/recruitcrm.io/_next/static/css/699608b5627cf431.css">
</head>
<body class="__variable_e36cd6">
<div>
<nav class="min-h-28 h-[120px] mb-3 md:mb-0" style="background-color:#fff;background:transparent">
<div class="min-h-28 lg:flex lg:justify-around lg:items-center">
<div class="flex justify-center lg:block"><a href="../../../../../index.html" class="p-2">
<img alt="Ensitech" class="!relative w-auto !max-w-[200px] !max-h-[70px] !h-auto" style="max-width:200px;max-height:70px;height:auto" src="{THANKYOU_ASSET}/images/42438_account_Ensitech_4_logo.png"></a></div>
<div class="flex justify-center">
<a href="../../../../index.html" class="cursor-pointer flex items-center px-3 py-1.5 text-center whitespace-nowrap text-xs rounded-sm font-medium font-roboto bg-white border border-gray-300 text-gray-800 mr-3 h-10">
<img alt="More Job" width="15" height="15" class="mr-2" src="{THANKYOU_ASSET}/recruitcrm.io/externalpages_v2/icons/arrow-right.svg">More Jobs</a>
</div></div></nav>

<section id="sTest-jobApplyBanner" style="background-color:#000000" class="flex overflow-hidden relative flex-col justify-center items-center self-stretch px-16 pt-36 pb-32 w-full text-3xl font-bold text-center text-white max-h-[350px] min-h-[300px] max-md:px-5 max-md:py-10">
<img alt="Background Decorative" class="object-cover object-center-top" style="position:absolute;height:100%;width:100%;left:0;top:0;right:0;bottom:0;object-fit:cover" src="{THANKYOU_ASSET}/images/42438_account_Ensitech_4_jobtitlebglogo.png">
<div class="container text-center pt-4 pb-3 z-[1] text-wrap">
<img alt="Ensitech" class="!relative mx-auto mb-2 w-auto !max-w-[200px] !max-h-[70px] !h-auto" style="max-width:200px;max-height:70px;height:auto" src="{THANKYOU_ASSET}/images/42438_account_Ensitech_4_logo.png">
<h1 class="break-words" style="color:#FFFFFF;font-size:30px;font-weight:700">{title}</h1>
</div>
<div style="background-color:#000000" class="absolute top-0 left-0 w-full h-full opacity-50"></div>
</section>

<section class="relative md:w-[75%] m-auto py-16">
<div class="container mx-auto px-6 text-center">
<div class="font-sans">
<h2 id="sTest-thankYouMessage" style="color:rgb(42,51,61);font-size:24px;font-weight:600;margin-bottom:16px">Thank you for submitting your application</h2>
<p style="color:rgb(138,162,173);font-size:16px;line-height:1.6;max-width:600px;margin:0 auto 32px">
We have received your application for <strong style="color:rgb(42,51,61)">{title}</strong>.
Our team will review your information and get back to you soon.
</p>
<a href="../../../../index.html" class="inline-block text-[13px] py-4 px-8 rounded font-bold" style="{BUTTON_STYLE}text-decoration:none">Browse More Jobs</a>
</div>
</div>
</section>


</div>
</body>
</html>"""


def wire_apply_buttons(jobs):
    for job in jobs:
        job_file = CAREERS / job["local_path"]
        if not job_file.exists():
            continue
        html = job_file.read_text(encoding="utf-8")

        # Replace Apply To This Job button with link to apply page
        html = re.sub(
            r'<button class="text-white text-sm font-sans font-bold py-1\.5 px-3 md:my-6 rounded mb-3" style="background-color: rgb\(254, 137, 44\); color: rgb\(255, 255, 255\);">Apply To This Job</button>',
            '<a href="apply/index.html" class="text-white text-sm font-sans font-bold py-1.5 px-3 md:my-6 rounded mb-3 inline-block text-center" style="background-color: rgb(254, 137, 44); color: rgb(255, 255, 255); text-decoration: none;">Apply To This Job</a>',
            html,
        )

        apply_link_script = """
<script>
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('button').forEach(function(btn) {
    if (btn.textContent.trim() === 'Apply To This Job') {
      var a = document.createElement('a');
      a.href = 'apply/index.html';
      a.className = btn.className + ' inline-block text-center';
      a.style.cssText = btn.getAttribute('style') || '';
      a.style.textDecoration = 'none';
      a.textContent = 'Apply To This Job';
      btn.parentNode.replaceChild(a, btn);
    }
  });
});
</script>
"""
        if 'apply/index.html' not in html and 'Apply To This Job' in html:
            html = html.replace("<body", apply_link_script + "\n<body", 1)

        job_file.write_text(html, encoding="utf-8")


def main():
    jobs = json.loads(JOBS_MANIFEST.read_text(encoding="utf-8"))
    for job in jobs:
        apply_dir = CAREERS / "jobs" / job["slug"] / "apply"
        apply_dir.mkdir(parents=True, exist_ok=True)
        out = apply_dir / "index.html"
        out.write_text(build_apply_html(job), encoding="utf-8")
        print(f"Built {out.relative_to(BASE)}")

        thank_you_dir = apply_dir / "thank-you"
        thank_you_dir.mkdir(parents=True, exist_ok=True)
        thank_out = thank_you_dir / "index.html"
        thank_out.write_text(build_thank_you_html(job), encoding="utf-8")
        print(f"Built {thank_out.relative_to(BASE)}")

    wire_apply_buttons(jobs)
    print(f"Wired Apply buttons on {len(jobs)} job pages")


if __name__ == "__main__":
    main()
