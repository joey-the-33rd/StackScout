# 🎯 Job Search Automation for Remote Developer Roles

This project automates the search for remote developer jobs that match your technology stack and preferences.

## 🔎 Search Query

```plaintext
("Remote Full Stack Developer" OR "Remote Software Engineer" OR "Remote Python Developer" OR "Remote React Developer" OR "AI Developer Remote" OR "Remote API Engineer")
AND (React OR Node.js OR Python OR JavaScript OR PostgreSQL OR Docker OR FastAPI OR API development OR GitHub OR AWS OR RESTful APIs OR LLMs OR WebSockets OR OAuth)
AND (Remote OR Worldwide OR Kenya)
```

## 📌 Filters

- 🌍 Location: Remote / Worldwide / Kenya (geo-specific)
- 🧰 Stack: React, Node.js, Python, JavaScript, PostgreSQL, Docker, FastAPI, API development, GitHub, AWS, RESTful APIs, LLMs, WebSockets, OAuth
- 💼 Job Type: Contract, Freelance, Full-time, Part-time
- 💸 Salary: $30/hour+ or $60,000+/year
- 🧠 Bonus Keywords: AI chatbot, LLM integration, DevOps, OpenAI, GPT, LangChain, REST/GraphQL APIs, pgvector, Redis, CI/CD
- ✅ Experience Level: Mid to Senior (include Entry level as fallback)

## 📁 Portfolio/GitHub

[https://github.com/joey-the-33rd](https://github.com/joey-the-33rd)

## 🧾 Output Format

| Company     | Role               | Tech Stack           | Salary      | Type      | Contact Person | Email/Contact | 🔗 Link                                                                 |
|-------------|--------------------|----------------------|-------------|-----------|----------------|---------------|------------------------------------------------------------------------|
| Snap! Mobile| Full Stack Engineer | React, Node.js, AWS  | $60K–$70K   | Full-time | Jane Doe       | <hr@snap.com> | [Apply](https://rubyonremote.com/jobs/58536-software-engineer-i-at-snap-mobile) |

## 🌐 Suggested Platforms

- [Google Search for Remote Developer Jobs](https://www.google.com/search?q=remote+developer+jobs+react+python+node+fastapi+docker)
- [LinkedIn Jobs](https://www.linkedin.com/jobs/)
- [Indeed](https://www.indeed.com)
- [Remote OK](https://remoteok.com/)
- [We Work Remotely](https://weworkremotely.com/)
- [ZipRecruiter](https://www.ziprecruiter.com)
- [Arc Remote Jobs](https://arc.dev/remote-jobs)

## 🚀 Project Progress and Recent Updates

- Added a FastAPI web interface to run the job search scraper with an HTML form and results pages.
- Implemented multi-platform scraping using Selenium and requests for platforms including Remote OK, Indeed, LinkedIn, Arc.dev, We Work Remotely, and placeholders for others.
- Utilized Selenium stealth techniques and automated login for LinkedIn scraping to improve scraping reliability.
- Job search results are saved to a markdown file (`multi_platform_jobs.md`) with detailed job information.
- Included robust error handling, retry logic, and rate limiting management to ensure scraper stability.
- Current limitations include the Google Jobs scraper being a placeholder due to dynamic content and page structure complexities.

## 🛠️ How to Run the Web Interface

1. Ensure you have the required environment variables set for LinkedIn credentials (`LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD`).
2. Install dependencies listed in `requirements.txt`.
3. Run the FastAPI app using a command like:
   ```bash
   uvicorn stackscout_web:app --reload
   ```
4. Open your browser and navigate to `http://localhost:8000` to access the job search form.
5. Submit the form to run the scraper and view job search results.

## 📊 Supported Job Platforms

- Remote OK
- Indeed
- LinkedIn (with login)
- Arc.dev
- We Work Remotely
- Google Jobs (currently placeholder)
- ZipRecruiter (placeholder)

  
