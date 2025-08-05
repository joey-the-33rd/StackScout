"""
Enhanced Job Scraper aligned with public.jobs table schema
Extracts: company, role, tech_stack, job_type, salary, location, description, 
          requirements, benefits, source_platform, source_url, posted_date, keywords
"""

import asyncio
from typing import List, Dict, Any
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, Tag
from datetime import datetime
import re
import json

class EnhancedJobScraper:
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    async def scrape_remoteok_enhanced(self, keywords: str = "python") -> List[Dict[str, Any]]:
        """Enhanced RemoteOK scraper with full schema alignment"""
        url = f"https://remoteok.com/remote-dev-jobs?search={keywords}"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=self.user_agent)
            page = await context.new_page()
            
            try:
                await page.goto(url)
                await page.wait_for_selector("tr.job", timeout=10000)
                content = await page.content()
                
                soup = BeautifulSoup(content, "html.parser")
                jobs = []
                
                job_rows = soup.find_all("tr", class_="job")[:10]
                
                for job in job_rows:
                    if isinstance(job, Tag):
                        # Extract basic info
                        company = job.get("data-company", "").strip()
                        role = job.get("data-position", "").strip()
                        
                        # Extract description
                        description_div = job.find_next_sibling("tr", class_="expand")
                        description = ""
                        if description_div:
                            desc_content = description_div.find("td", class_="description")
                            if desc_content:
                                description = desc_content.get_text(strip=True)
                        
                        # Extract tags/tech stack
                        tags = []
                        tag_elements = job.find_all("div", class_="tag")
                        for tag in tag_elements:
                            tag_text = tag.get_text(strip=True)
                            if tag_text:
                                tags.append(tag_text)
                        
                        # Extract salary
                        salary = self.extract_salary(description)
                        
                        # Extract location
                        location = "Remote"  # RemoteOK is primarily remote jobs
                        
                        # Extract job type
                        job_type = self.extract_job_type(description)
                        
                        # Extract requirements and benefits
                        requirements = self.extract_requirements(description)
                        benefits = self.extract_benefits(description)
                        
                        # Source platform
                        source_platform = "RemoteOK"
                        
                        # Source URL
                        data_href = job.get("data-href", "")
                        source_url = f"https://remoteok.com{data_href}" if data_href else ""
                        
                        # Posted date (approximate)
                        posted_date = datetime.now()  # RemoteOK doesn't show exact dates
                        
                        # Keywords
                        keywords_list = [kw.strip() for kw in keywords.split(",")]
                        
                        jobs.append({
                            "company": company,
                            "role": role,
                            "tech_stack": tags,
                            "job_type": job_type,
                            "salary": salary,
                            "location": location,
                            "description": description,
                            "requirements": requirements,
                            "benefits": benefits,
                            "source_platform": source_platform,
                            "source_url": source_url,
                            "posted_date": posted_date,
                            "keywords": keywords_list,
                            "is_active": True
                        })
                
                await browser.close()
                return jobs
                
            except Exception as e:
                print(f"Error scraping RemoteOK: {e}")
                await browser.close()
                return []
    
    async def scrape_jobgether_enhanced(self, keywords: str = "python") -> List[Dict[str, Any]]:
        """Enhanced JobGether scraper with full schema alignment"""
        url = f"https://jobgether.com/remote-jobs?search={keywords}"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=self.user_agent)
            page = await context.new_page()
            
            try:
                await page.goto(url)
                await page.wait_for_selector("div.new-opportunity", timeout=15000)
                await asyncio.sleep(3)
                
                job_elements = await page.query_selector_all("div.new-opportunity")
                jobs = []
                
                for job_element in job_elements[:10]:
                    # Extract company
                    company_elem = await job_element.query_selector("span.company-name")
                    company = await company_elem.inner_text() if company_elem else ""
                    
                    # Extract role
                    role_elem = await job_element.query_selector("h2")
                    role = await role_elem.inner_text() if role_elem else ""
                    
                    # Extract link
                    link_elem = await job_element.query_selector("a[href]")
                    href = await link_elem.get_attribute("href") if link_elem else ""
                    source_url = f"https://jobgether.com{href}" if href.startswith("/") else href
                    
                    # Navigate to job details page for full description
                    if source_url:
                        detail_page = await context.new_page()
                        try:
                            await detail_page.goto(source_url)
                            await detail_page.wait_for_selector("body", timeout=10000)
                            
                            # Extract full description
                            description_elem = await detail_page.query_selector("div.job-description")
                            description = await description_elem.inner_text() if description_elem else ""
                            
                            # Extract tech stack from tags
                            tech_elems = await detail_page.query_selector_all("div.skill-tag, span.skill")
                            tech_stack = []
                            for tech_elem in tech_elems:
                                tech_text = await tech_elem.inner_text()
                                if tech_text:
                                    tech_stack.append(tech_text.strip())
                            
                            # Extract salary
                            salary_elem = await detail_page.query_selector("div.salary-range, span.salary")
                            salary = await salary_elem.inner_text() if salary_elem else ""
                            
                            # Extract location
                            location_elem = await detail_page.query_selector("div.location, span.location")
                            location = await location_elem.inner_text() if location_elem else "Remote"
                            
                            # Extract job type
                            job_type_elem = await detail_page.query_selector("div.job-type, span.job-type")
                            job_type = await job_type_elem.inner_text() if job_type_elem else "Full-time"
                            
                            # Extract requirements and benefits
                            requirements = self.extract_requirements(description)
                            benefits = self.extract_benefits(description)
                            
                            keywords_list = [kw.strip() for kw in keywords.split(",")]
                            
                            jobs.append({
                                "company": company.strip(),
                                "role": role.strip(),
                                "tech_stack": tech_stack,
                                "job_type": job_type.strip(),
                                "salary": salary.strip(),
                                "location": location.strip(),
                                "description": description.strip(),
                                "requirements": requirements,
                                "benefits": benefits,
                                "source_platform": "JobGether",
                                "source_url": source_url,
                                "posted_date": datetime.now(),
                                "keywords": keywords_list,
                                "is_active": True
                            })
                            
                        except Exception as detail_error:
                            print(f"Error loading job details: {detail_error}")
                        finally:
                            await detail_page.close()
                
                await browser.close()
                return jobs
                
            except Exception as e:
                print(f"Error scraping JobGether: {e}")
                await browser.close()
                return []
    
    def extract_salary(self, text: str) -> str:
        """Extract salary information from text"""
        if not text:
            return ""
        
        # Common salary patterns
        salary_patterns = [
            r'\$[\d,]+\s*(?:k|K)?\s*(?:per\s*(?:year|annum|annually|yr))?',
            r'\$[\d,]+\s*-\s*\$[\d,]+\s*(?:k|K)?',
            r'€[\d,]+\s*(?:k|K)?',
            r'£[\d,]+\s*(?:k|K)?',
            r'\d+\s*(?:k|K)?\s*(?:per\s*(?:year|annum|annually|yr))',
            r'\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP)?'
        ]
        
        for pattern in salary_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return ""
    
    def extract_job_type(self, text: str) -> str:
        """Extract job type from text"""
        if not text:
            return "Full-time"
        
        text_lower = text.lower()
        
        job_types = {
            "full-time": ["full-time", "full time", "fulltime", "permanent"],
            "part-time": ["part-time", "part time", "parttime"],
            "contract": ["contract", "contractor", "freelance"],
            "internship": ["intern", "internship"],
            "temporary": ["temporary", "temp", "seasonal"]
        }
        
        for job_type, keywords in job_types.items():
            if any(keyword in text_lower for keyword in keywords):
                return job_type
        
        return "Full-time"
    
    def extract_requirements(self, description: str) -> Dict[str, Any]:
        """Extract structured requirements from job description"""
        if not description:
            return {}
        
        requirements = {
            "experience": "",
            "skills": [],
            "education": "",
            "certifications": []
        }
        
        # Extract experience
        experience_patterns = [
            r'(\d+)\s*(?:\+)?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience)?',
            r'(?:experience|exp)\s*(?:of\s*)?(\d+)\s*(?:\+)?\s*(?:years?|yrs?)',
            r'(\d+)-(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience)?'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    requirements["experience"] = f"{matches[0][0]}-{matches[0][1]} years"
                else:
                    requirements["experience"] = f"{matches[0]}+ years"
                break
        
        # Extract skills
        common_skills = [
            "python", "javascript", "react", "node", "java", "c++", "c#", "ruby", "php",
            "swift", "kotlin", "go", "rust", "typescript", "angular", "vue", "django",
            "flask", "spring", "express", "mongodb", "postgresql", "mysql", "redis",
            "docker", "kubernetes", "aws", "azure", "gcp", "git", "linux", "bash"
        ]
        
        description_lower = description.lower()
        found_skills = [skill for skill in common_skills if skill in description_lower]
        requirements["skills"] = found_skills
        
        # Extract education
        education_patterns = [
            r'(bachelor|master|phd|doctorate|degree)\s*(?:in\s*\w+)?',
            r'(bs|ms|phd|ba|ma)\s*(?:in\s*\w+)?',
            r'(?:education|degree)\s*(?:required|preferred)?\s*:?\s*([^.]+)'
        ]
        
        for pattern in education_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            if matches:
                requirements["education"] = matches[0] if isinstance(matches[0], str) else " ".join(matches[0])
                break
        
        return requirements
    
    def extract_benefits(self, description: str) -> Dict[str, Any]:
        """Extract structured benefits from job description"""
        if not description:
            return {}
        
        benefits = {
            "health": "",
            "retirement": "",
            "pto": "",
            "remote": False,
            "flexible_hours": False,
            "other": []
        }
        
        description_lower = description.lower()
        
        # Check for remote work
        if any(word in description_lower for word in ["remote", "work from home", "wfh"]):
            benefits["remote"] = True
        
        # Check for flexible hours
        if any(word in description_lower for word in ["flexible hours", "flexible schedule"]):
            benefits["flexible_hours"] = True
        
        # Extract health benefits
        health_patterns = [
            r'(health|medical|dental|vision)\s*(?:insurance|coverage|benefits?)',
            r'(?:healthcare|health)\s*(?:benefits?|coverage)'
        ]
        
        for pattern in health_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            if matches:
                benefits["health"] = "Comprehensive health coverage"
                break
        
        # Extract PTO
        pto_patterns = [
            r'(\d+)\s*(?:days?|weeks?)\s*(?:pto|vacation|paid time off)',
            r'unlimited\s*(?:pto|vacation)',
            r'generous\s*(?:pto|vacation)'
        ]
        
        for pattern in pto_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            if matches:
                benefits["pto"] = matches[0] if isinstance(matches[0], str) else " ".join(matches[0])
                break
        
        return benefits
    
    async def scrape_all_platforms(self, keywords: str = "python") -> List[Dict[str, Any]]:
        """Scrape all platforms and return unified results"""
        tasks = [
            self.scrape_remoteok_enhanced(keywords),
            self.scrape_jobgether_enhanced(keywords)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_jobs = []
        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
            else:
                print(f"Error in scraping: {result}")
        
        return all_jobs

# Test function
async def test_enhanced_scraper():
    scraper = EnhancedJobScraper()
    results = await scraper.scrape_all_platforms("python developer")
    
    print(f"✅ Found {len(results)} jobs")
    for job in results[:3]:
        print(f"\n📝 Job: {job['role']} at {job['company']}")
        print(f"   Tech Stack: {', '.join(job['tech_stack'])}")
        print(f"   Location: {job['location']}")
        print(f"   Salary: {job['salary']}")
        print(f"   Source: {job['source_platform']}")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_enhanced_scraper())
