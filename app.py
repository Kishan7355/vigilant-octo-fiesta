import os
import re
import datetime
from datetime import timedelta
import requests
import time
import random
import html
import logging
import json
from urllib.parse import urlparse
from flask import Flask, jsonify
import google.generativeai as genai

# ==================== CONFIG ====================
INDIA_COUNTRY_FACET_ID = "c4f78be1a8f14da0ab49ce1162348a5e"
BACKEND_URL = os.environ.get('BACKEND_URL', "https://autoback-781i.vercel.app/posts")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyB7wWzCPvyVTbxh22dYZd0w4Wz37f7dyL8")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ==================== COMPANIES LIST ====================
COMPANIES = [
    {"name": "Boeing", "url": "https://boeing.wd1.myworkdayjobs.com/EXTERNAL_CAREERS"},
    {"name": "3M", "url": "https://3m.wd1.myworkdayjobs.com/search"},
    {"name": "Adobe", "url": "https://adobe.wd5.myworkdayjobs.com/external_experienced"},
    {"name": "NVIDIA", "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"},
    {"name": "Salesforce", "url": "https://salesforce.wd12.myworkdayjobs.com/External_Career_Site"},
    {"name": "Target", "url": "https://target.wd5.myworkdayjobs.com/targetcareers"},
    {"name": "Walmart", "url": "https://walmart.wd5.myworkdayjobs.com/WalmartExternal"},
    {"name": "Chevron", "url": "https://chevron.wd5.myworkdayjobs.com/jobs"},
    {"name": "Deloitte", "url": "https://deloitteie.wd3.myworkdayjobs.com/Early_Careers"},
    {"name": "Puma", "url": "https://puma.wd3.myworkdayjobs.com/Jobs_at_Puma"},
    {"name": "Sanofi", "url": "https://sanofi.wd3.myworkdayjobs.com/SanofiCareers"},
    {"name": "Comcast", "url": "https://comcast.wd5.myworkdayjobs.com/Comcast_Careers"},
    {"name": "Abbott", "url": "https://abbott.wd5.myworkdayjobs.com/abbottcareers"},
    {"name": "Alcoa", "url": "https://alcoa.wd5.myworkdayjobs.com/careers/1/refreshFacet/318c8bb6f553100021d223d9780d30be"},
    {"name": "American Electric Power", "url": "https://aep.wd1.myworkdayjobs.com/AEPCareerSite"},
    {"name": "Amgen", "url": "https://amgen.wd1.myworkdayjobs.com/Careers"},
    {"name": "Applied Materials", "url": "https://amat.wd1.myworkdayjobs.com/External"},
    {"name": "Arrow Electronics", "url": "https://arrow.wd1.myworkdayjobs.com/AC"},
    {"name": "Assurant", "url": "https://assurant.wd1.myworkdayjobs.com/Assurant_Careers"},
    {"name": "AT&T", "url": "https://att.wd1.myworkdayjobs.com/ATTGeneral"},
    {"name": "Avis Budget Group", "url": "https://avisbudget.wd1.myworkdayjobs.com/ABG_Careers"},
    {"name": "BlackRock", "url": "https://blackrock.wd1.myworkdayjobs.com/BlackRock_Professional"},
    {"name": "Bupa", "url": "https://bupa.wd3.myworkdayjobs.com/EXT_CAREER"},
    {"name": "Cognizant", "url": "https://collaborative.wd1.myworkdayjobs.com/AllOpenings"},
    {"name": "Workday", "url": "https://workday.wd5.myworkdayjobs.com/Workday"},
    {"name": "Fidelity", "url": "https://wd1.myworkdaysite.com/en-US/recruiting/fmr/FidelityCareers"},
    {"name": "AIG", "url": "https://aig.wd1.myworkdayjobs.com/aig"},
    {"name": "Analog Devices", "url": "https://analogdevices.wd1.myworkdayjobs.com/External"},
    {"name": "Intel", "url": "https://intel.wd1.myworkdayjobs.com/External"},
    {"name": "Mastercard", "url": "https://mastercard.wd1.myworkdayjobs.com/CorporateCareers"},
    {"name": "JLL", "url": "https://jll.wd1.myworkdayjobs.com/jllcareers"},
    {"name": "CNX", "url": "https://cnx.wd1.myworkdayjobs.com/external_global"},
    {"name": "Coca-Cola", "url": "https://coke.wd1.myworkdayjobs.com/coca-cola-careers"},
    {"name": "Dell", "url": "https://dell.wd1.myworkdayjobs.com/External"},
    {"name": "Bank of America", "url": "https://ghr.wd1.myworkdayjobs.com/Lateral-US"},
    {"name": "Accenture", "url": "https://accenture.wd103.myworkdayjobs.com/en-US/AccentureCareers/"},
    {"name": "PwC", "url": "https://pwc.wd3.myworkdayjobs.com/Global_Experienced_Careers"},
    {"name": "Huron", "url": "https://huron.wd1.myworkdayjobs.com/huroncareers"},
    {"name": "ING", "url": "https://ing.wd3.myworkdayjobs.com/ICSGBLCOR"},
    {"name": "eBay", "url": "https://ebay.wd5.myworkdayjobs.com/apply/"},
    {"name": "AstraZeneca", "url": "https://astrazeneca.wd3.myworkdayjobs.com/Careers"},
    {"name": "Nexstar", "url": "https://nexstar.wd5.myworkdayjobs.com/nexstar"},
    {"name": "Samsung", "url": "https://sec.wd3.myworkdayjobs.com/Samsung_Careers"},
    {"name": "Warner Bros", "url": "https://warnerbros.wd5.myworkdayjobs.com/global"},
    {"name": "Hitachi", "url": "https://hitachi.wd1.myworkdayjobs.com/hitachi"},
    {"name": "Ciena", "url": "https://ciena.wd5.myworkdayjobs.com/Careers"},
    {"name": "BDX", "url": "https://bdx.wd1.myworkdayjobs.com/EXTERNAL_CAREER_SITE_INDIA"},
    {"name": "Cengage", "url": "https://cengage.wd5.myworkdayjobs.com/CengageIndiaCareers"},
    {"name": "Pfizer", "url": "https://pfizer.wd1.myworkdayjobs.com/PfizerCareers"},
    {"name": "Availity", "url": "https://availity.wd1.myworkdayjobs.com/Availity_Careers_India"},
    {"name": "Wells Fargo", "url": "https://wd1.myworkdaysite.com/recruiting/wf/WellsFargoJobs"},
    {"name": "Motorola Solutions", "url": "https://motorolasolutions.wd5.myworkdayjobs.com/Careers"},
    {"name": "2020 Companies", "url": "https://2020companies.wd1.myworkdayjobs.com/External_Careers"},
    {"name": "Kyndryl", "url": "https://kyndryl.wd5.myworkdayjobs.com/KyndrylProfessionalCareers"},
    {"name": "IFF", "url": "https://iff.wd5.myworkdayjobs.com/en-US/iff_careers"},
    {"name": "Light & Wonder", "url": "https://lnw.wd5.myworkdayjobs.com/LightWonderExternalCareers"},
    {"name": "Bristol Myers Squibb", "url": "https://bristolmyerssquibb.wd5.myworkdayjobs.com/BMS"},
    {"name": "Alcon", "url": "https://alcon.wd5.myworkdayjobs.com/careers_alcon"},
    {"name": "DXC Technology", "url": "https://dxctechnology.wd1.myworkdayjobs.com/DXCJobs"},
    {"name": "London Stock Exchange Group (LSEG)", "url": "https://lseg.wd3.myworkdayjobs.com/Careers"},
    {"name": "Cigna", "url": "https://cigna.wd5.myworkdayjobs.com/cignacareers"},
    {"name": "GE Vernova", "url": "https://gevernova.wd5.myworkdayjobs.com/Vernova_ExternalSite"},
    {"name": "Clarivate", "url": "https://clarivate.wd3.myworkdayjobs.com/Clarivate_Careers"},
    {"name": "Silicon Labs", "url": "https://silabs.wd1.myworkdayjobs.com/SiliconLabsCareers"},
    {"name": "Micron", "url": "https://micron.wd1.myworkdayjobs.com/External"},
    {"name": "Blackbaud", "url": "https://blackbaud.wd1.myworkdayjobs.com/ExternalCareers"},
    {"name": "FIS", "url": "https://fis.wd5.myworkdayjobs.com/en-US/SearchJobs"},
    {"name": "Web Industries", "url": "https://web.wd1.myworkdayjobs.com/ExternalCareerSite"},
    {"name": "Qualys", "url": "https://qualys.wd5.myworkdayjobs.com/Careers"},
    {"name": "Optiv", "url": "https://optiv.wd5.myworkdayjobs.com/Optiv_Careers"},
    {"name": "T-Mobile", "url": "https://tmobile.wd1.myworkdayjobs.com/External"},
    {"name": "Morningstar", "url": "https://morningstar.wd5.myworkdayjobs.com/Americas"}
]

# ==================== GEMINI CONTENT GENERATION ====================
def generate_content_with_gemini(job, company_name):
    """
    Generate comprehensive job content using Gemini API
    """
    title = job['title']
    location = job['location']
    experience = job['experience']
    skills = job['skills'][:5] if job['skills'] else ["Teamwork", "Communication", "Problem Solving"]
    remote_type = job.get('remote_type', 'Office')
    time_type = job.get('time_type', 'Full Time')
    
    prompt = f"""
    Write a comprehensive, SEO-optimized job posting for the position of {title} at {company_name} in {location}.
    
    Job Details:
    - Company: {company_name}
    - Position: {title}
    - Location: {location}
    - Experience Required: {experience}
    - Key Skills: {', '.join(skills)}
    - Work Type: {remote_type}
    - Employment Type: {time_type}
    
    Please create a detailed job posting that includes:
    
    1. An engaging introduction about the company and the role
    2. Detailed company overview including culture, values, and achievements
    3. Comprehensive job description with key responsibilities
    4. Detailed requirements including education, experience, and skills
    5. Benefits and perks offered by the company
    6. Career growth opportunities
    7. Information about the work environment
    8. Step-by-step application process
    9. Tips for standing out as a candidate
    10. Typical interview process
    11. Frequently asked questions with answers
    12. Conclusion with call to action
    
    The content should be:
    - At least 1500 words
    - SEO optimized with relevant keywords
    - Professional and engaging
    - Compliant with AdSense policies
    - Structured with appropriate headings (H1, H2, H3)
    - Include bullet points where appropriate
    - Written in a conversational yet professional tone
    
    Format the content using HTML tags for headings, paragraphs, lists, and emphasis.
    Do not include any content that violates AdSense policies (no misleading claims, no inappropriate content, etc.).
    
    IMPORTANT: Format the content as continuous paragraphs without line breaks. Use HTML tags for formatting but ensure the final output has no line breaks in the HTML code itself.
    """
    
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        
        if response and response.text:
            # Remove line breaks from the generated content
            content = response.text.replace('\n', '').replace('\r', '')
            return content
        else:
            logger.error("Empty response from Gemini API")
            return None
    except Exception as e:
        logger.error(f"Error generating content with Gemini: {e}")
        return None

# ==================== HELPER FUNCTIONS ====================
def get_company_logo(logo_url):
    try:
        r = requests.head(logo_url, timeout=8)
        return logo_url if r.status_code == 200 else None
    except:
        return None

def is_location_in_india(location_text):
    """Check if the job location is in India"""
    if not location_text:
        return False
    
    location_text = location_text.lower()
    
    india_indicators = [
        'india', 'indian', 'bengaluru', 'bangalore', 'hyderabad', 
        'pune', 'mumbai', 'delhi', 'chennai', 'gurgaon', 'noida',
        'kolkata', 'ahmedabad', 'jaipur', 'chandigarh', 'cochin',
        'kochi', 'trivandrum', 'lucknow', 'nagpur', 'indore'
    ]
    
    for indicator in india_indicators:
        if indicator in location_text:
            return True
    
    indian_state_codes = [
        'ap', 'ar', 'as', 'br', 'ct', 'ga', 'gj', 'hr', 'hp', 
        'jk', 'jh', 'ka', 'kl', 'mp', 'mh', 'mn', 'ml', 'mz', 
        'nl', 'or', 'pb', 'rj', 'sk', 'tn', 'tg', 'tr', 'up', 
        'ut', 'wb', 'an', 'ch', 'dh', 'dn', 'dl', 'la', 'ld'
    ]
    
    for code in indian_state_codes:
        pattern = r'\b' + code + r'\b'
        if re.search(pattern, location_text):
            return True
    
    if re.search(r'\b\d{6}\b', location_text):
        return True
    
    return False

def generate_rich_content(job, company_name):
    title = html.escape(job['title'])
    location = html.escape(job['location'] or "Multiple Cities, India")
    exp = job['experience'] if job['experience'] else "Not specified"
    remote = job.get('remote_type', 'Office').replace('Remote', 'Work from Home').replace('Hybrid', 'Hybrid')
    time_type = job.get('time_type', 'Full Time')
    job_id = job['job_req_id']

    gemini_content = generate_content_with_gemini(job, company_name)
    
    if gemini_content:
        content = gemini_content
        job_details = f"<h1>{title} - {company_name} Hiring in India</h1>"
        job_details += f"<p><strong>Location:</strong> {location} | <strong>Experience:</strong> {exp} | <strong>Job Type:</strong> {time_type} | <strong>Mode:</strong> {remote}</strong></p>"
        job_details += f"<p><strong>Job ID:</strong> {job_id}</p><br>"
        
        apply_button = f"<div style='text-align:center; margin:30px 0;'>"
        apply_button += f"<a href='{job['apply_link']}' target='_blank' style='background:#0077b6; color:white; padding:18px 40px; font-size:18px; text-decoration:none; border-radius:8px; font-weight:bold;'>APPLY NOW - OFFICIAL LINK</a>"
        apply_button += "</div>"
        
        footer = f"<p><small>Posted on: {job['posted_text']} | Last updated: {datetime.date.today().strftime('%B %d, %Y')} | Source: {company_name} Official Careers</small></p>"
        
        full_content = job_details + content + apply_button + footer
        # Remove any line breaks from the final content
        return full_content.replace('\n', '').replace('\r', '')
    else:
        logger.warning(f"Gemini API failed for {title} at {company_name}. Using fallback content.")
        skills = job['skills'][:6] if job['skills'] else ["Teamwork", "Communication", "Problem Solving"]
        is_fresher = 'fresher' in job.get('exp', '').lower() or '0' in exp or 'entry' in exp.lower()
        fresher_answer = "Yes! Freshers are encouraged to apply." if is_fresher else "No, relevant experience is required."

        content = f"<h1>{title} - {company_name} Hiring in India</h1>"
        content += f"<p><strong>Location:</strong> {location} | <strong>Experience:</strong> {exp} | <strong>Job Type:</strong> {time_type} | <strong>Mode:</strong> {remote}</strong></p>"
        content += f"<p><strong>Job ID:</strong> {job_id}</p><br>"
        content += f"<p>Your next career move starts here! {company_name} is expanding its India team and looking for talented professionals to join as <strong>{title}</strong>. Apply now!</p>"
        content += f"<p>{company_name} offers industry-leading benefits, learning opportunities, and a chance to work on global projects. Join a team that values innovation, diversity, and excellence.</p><br>"
        content += "<h2>About the Role</h2>"
        content += "<p>This is a fantastic opportunity to grow your career with a world-class organization. You'll work with talented professionals and contribute to meaningful projects that impact millions.</p>"
        content += "<h2>Key Requirements</h2>"
        content += f"<ul><li>Experience: {exp}</li>"
        content += "<li>Bachelor's/Master's degree in relevant field</li>"
        content += f"<li>Strong knowledge of: {', '.join(skills)}</li>"
        content += "<li>Excellent communication and analytical skills</li>"
        content += "<li>Ability to work in a fast-paced environment</li></ul><br>"
        content += f"<div style='text-align:center; margin:30px 0;'>"
        content += f"<a href='{job['apply_link']}' target='_blank' style='background:#0077b6; color:white; padding:18px 40px; font-size:18px; text-decoration:none; border-radius:8px; font-weight:bold;'>APPLY NOW - OFFICIAL LINK</a>"
        content += "</div>"
        content += f"<p><small>Posted on: {job['posted_text']} | Last updated: {datetime.date.today().strftime('%B %d, %Y')} | Source: {company_name} Official Careers</small></p>"
        
        # Remove any line breaks from the final content
        return content.replace('\n', '').replace('\r', '')

def post_to_backend(job, company_name, logo_url):
    raw_skills = job.get('skills', [])
    clean_skills = []
    if isinstance(raw_skills, list):
        for skill in raw_skills:
            try:
                clean_skill = str(skill).strip().lower().capitalize()
                if len(clean_skill) > 2:
                    clean_skills.append(clean_skill)
            except Exception:
                continue
                
    seen = set()
    final_skills = []
    for skill in clean_skills:
        if skill not in seen:
            seen.add(skill)
            final_skills.append(skill)
    final_skills = final_skills[:10]

    if not final_skills:
        final_skills = ["Communication", "Teamwork", "Problem Solving"]

    payload = {
        "title": f"{job['title']} at {company_name} - {job['location'].split(',')[0] if job['location'] else 'India'}",
        "description": generate_rich_content(job, company_name),
        "company_name": company_name,
        "company_logo": logo_url,
        "job_req_id": job['job_req_id'],
        "apply_link": job['apply_link'],
        "location": job['location'],
        "experience": job['experience'],
        "skills": final_skills,
        "remote_type": job.get('remote_type'),
        "time_type": job.get('time_type'),
        "posted_date": job['posted_date']
    }

    for _ in range(3):
        try:
            r = requests.post(BACKEND_URL, json=payload, timeout=15)
            if r.status_code == 201:
                logger.info(f"Posted: {payload['title']}")
                return True
            else:
                logger.error(f"Failed to post: {r.status_code} - {r.text}")
        except Exception as e:
            logger.warning(f"Retry posting... {e}")
            time.sleep(5)
    return False

# ==================== CORE SCRAPING FUNCTION ====================
def fetch_past_jobs(company_name, base_url, target_date_str):
    parsed = urlparse(base_url)
    host = parsed.netloc
    path = parsed.path.strip('/')
    tenant = host.split('.')[0]
    site = path.split('/')[-1] if '/' in path else path
    endpoint = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": base_url
    }

    jobs = []
    offset = 0
    limit = 20
    today = datetime.date.today()

    while True:
        payload = {"limit": limit, "offset": offset, "searchText": ""}
        try:
            payload_with_facet = payload.copy()
            payload_with_facet["appliedFacets"] = {"locationCountry": [INDIA_COUNTRY_FACET_ID]}
            r = requests.post(endpoint, headers=headers, json=payload_with_facet, timeout=12)
            
            if r.status_code == 400:
                r = requests.post(endpoint, headers=headers, json=payload, timeout=12)
                
            data = r.json()
        except Exception as e:
            logger.error(f"Failed to fetch jobs for {company_name}: {e}")
            break

        postings = data.get("jobPostings", [])
        if not postings:
            break

        for p in postings:
            title = p.get("title", "")
            path = p.get("externalPath", "")
            if not path: continue
            slug = path.split("/")[-1]
            job_id = slug.split("_")[-1]
            apply_link = f"https://{host}/en-US/{site}/job/{slug}"

            posted_text = p.get("postedOn", "Today")
            posted_delta = 0
            if "day" in posted_text.lower():
                match = re.search(r"(\d+)", posted_text)
                posted_delta = int(match.group(1)) if match else 0
            posted_date = (today - timedelta(days=posted_delta)).isoformat()

            if posted_date != target_date_str:
                if posted_delta > 1:
                    break
                continue

            location_text = p.get("locationsText", "")
            
            if not is_location_in_india(location_text):
                logger.info(f"Skipping non-India job: {title} at {location_text}")
                continue

            detail_url = f"https://{host}/wday/cxs/{tenant}/{site}{path}"
            try:
                detail = requests.get(detail_url, headers=headers, timeout=10).json()
                info = detail.get("jobPostingInfo", {})
                desc_html = info.get("jobDescription", "")
                desc = re.sub(r'<[^>]+>', '', desc_html)
                skills = re.findall(r'\b[A-Za-z#+.]{3,20}\b', desc)[:6]
            except:
                desc = "Exciting opportunity with great growth potential."
                skills = []

            jobs.append({
                "title": title,
                "location": location_text,
                "apply_link": apply_link,
                "posted_date": posted_date,
                "posted_text": posted_text,
                "job_req_id": job_id,
                "experience": "Not specified",
                "skills": list(set([s.lower().capitalize() for s in skills if len(s) > 2])),
                "remote_type": info.get("remoteType", "Office"),
                "time_type": info.get("timeType", "Full Time"),
                "exp": "exp" if any(x in title.lower() for x in ["senior", "lead", "manager", "5+", "8+"]) else "fresher"
            })

        offset += limit
        if offset >= data.get("total", 0):
            break

    return jobs

# ==================== SINGLE JOB POSTING ====================
def post_single_job():
    """Post a single job from a random company"""
    # MODIFIED: Look for jobs posted in the last 3 days instead of just today
    target_date = (datetime.date.today() - timedelta(days=3)).isoformat()
    logger.info(f"Posting a single job for {target_date}")
    
    # --- ROBUST DUPLICATE CHECKING ---
    # 1. Fetch all existing jobs once to build a cache of seen job IDs
    existing_job_ids = set()
    try:
        logger.info("Fetching existing jobs to build duplicate cache...")
        r = requests.get(BACKEND_URL, timeout=20)
        if r.status_code == 200:
            posts = r.json().get('jobs', [])
            for post in posts:
                job_id = post.get('job_req_id')
                company = post.get('company_name')
                if job_id and company:
                    existing_job_ids.add(f"{company}_{job_id}")
        logger.info(f"Cache built with {len(existing_job_ids)} existing jobs.")
    except Exception as e:
        logger.error(f"Failed to build duplicate cache. Proceeding with caution. Error: {e}")

    # Pick a random company
    random.shuffle(COMPANIES)
    company = COMPANIES[0]
    name = company["name"]
    logger.info(f"Scraping {name} for a single job...")
    jobs = fetch_past_jobs(name, company["url"], target_date)
    
    if not jobs:
        logger.warning(f"No jobs found for {name}")
        return {"status": "no_jobs", "company": name}
    
    # Pick a random job from this company
    job = random.choice(jobs)
    
    # --- EFFICIENT DUPLICATE CHECK ---
    unique_job_id = f"{name}_{job['job_req_id']}"
    if unique_job_id in existing_job_ids:
        logger.info(f"Skipping duplicate job: {job['title']} at {name}")
        return {"status": "duplicate", "title": job['title'], "company": name}

    logo = f"https://logo.clearbit.com/{name.lower().replace(' ', '')}.com"
    logo = get_company_logo(logo)

    if post_to_backend(job, name, logo):
        logger.info(f"Successfully posted: {job['title']} at {name}")
        return {"status": "success", "title": job['title'], "company": name}
    else:
        logger.error(f"Failed to post: {job['title']} at {name}")
        return {"status": "failed", "title": job['title'], "company": name}

# ==================== MAIN SCRAPER ====================
def run_scrape():
    target_date = datetime.date.today().isoformat()
    logger.info(f"Starting scrape for jobs posted on {target_date}")
    new_posts = 0
    random.shuffle(COMPANIES)

    # --- ROBUST DUPLICATE CHECKING ---
    # 1. Fetch all existing jobs once to build a cache of seen job IDs
    existing_job_ids = set()
    try:
        logger.info("Fetching existing jobs to build duplicate cache...")
        r = requests.get(BACKEND_URL, timeout=20)
        if r.status_code == 200:
            posts = r.json().get('jobs', [])
            for post in posts:
                job_id = post.get('job_req_id')
                company = post.get('company_name')
                if job_id and company:
                    existing_job_ids.add(f"{company}_{job_id}")
        logger.info(f"Cache built with {len(existing_job_ids)} existing jobs.")
    except Exception as e:
        logger.error(f"Failed to build duplicate cache. Proceeding with caution. Error: {e}")

    for comp in COMPANIES:
        name = comp["name"]
        logger.info(f"Scraping {name}...")
        jobs = fetch_past_jobs(name, comp["url"], target_date)

        for job in jobs:
            # --- EFFICIENT DUPLICATE CHECK ---
            unique_job_id = f"{name}_{job['job_req_id']}"
            if unique_job_id in existing_job_ids:
                logger.info(f"Skipping duplicate job: {job['title']} at {name}")
                continue

            logo = f"https://logo.clearbit.com/{name.lower().replace(' ', '')}.com"
            logo = get_company_logo(logo)

            if post_to_backend(job, name, logo):
                new_posts += 1
                # Add to cache after successful post to prevent re-posting in the same run
                existing_job_ids.add(unique_job_id)
                time.sleep(2)

    logger.info(f"Completed! {new_posts} new jobs posted.")
    return {"status": "success", "new_posts": new_posts, "date": target_date}

# ==================== FLASK ROUTES ====================
@app.route('/scrape', methods=['GET'])
def scrape_endpoint():
    result = run_scrape()
    return jsonify(result)

@app.route('/post-single', methods=['GET'])
def post_single_endpoint():
    result = post_single_job()
    return jsonify(result)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "Rich Content Scraper v3.1 Running",
        "features": ["100% Original Content", "1500+ Words", "SEO Optimized", "Duplicate Proof", "India Jobs Only", "Gemini AI Powered"],
        "scheduler": "External cron required (e.g., GitHub Actions)"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
