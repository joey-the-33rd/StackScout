#!/usr/bin/env python3
"""Test script for AI generators."""

import os
import sys
from src.ai_generators.resume_generator import ResumeGenerator
from src.ai_generators.cover_letter_generator import CoverLetterGenerator
from src.ai_generators.cv_tailor import CVTailor
from src.ai_generators.email_generator import EmailGenerator

def test_resume_generator():
    """Test resume generation."""
    print("Testing Resume Generator...")
    
    try:
        generator = ResumeGenerator()
        
        # Mock user profile
        user_profile = {
            "full_name": "John Doe",
            "title": "Senior Software Engineer",
            "years_experience": 5,
            "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker"],
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "Tech Corp",
                    "duration": "2021-2024",
                    "description": "Led development of scalable web applications",
                    "achievements": ["Reduced load time by 40%", "Led team of 5 developers"]
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Computer Science",
                    "institution": "University of Technology",
                    "year": "2019"
                }
            ],
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "technologies": ["React", "Node.js", "MongoDB"],
                    "description": "Full-stack e-commerce solution",
                    "impact": "Increased sales by 25%"
                }
            ]
        }
        
        resume = generator.generate_resume(user_profile, "ats_friendly")
        print("✅ Resume generated successfully")
        print(f"Resume sections: {list(resume['sections'].keys())}")
        return True
        
    except Exception as e:
        print(f"❌ Resume generation failed: {e}")
        return False

def test_cover_letter_generator():
    """Test cover letter generation."""
    print("\nTesting Cover Letter Generator...")
    
    try:
        generator = CoverLetterGenerator()
        
        user_profile = {
            "full_name": "John Doe",
            "title": "Senior Software Engineer",
            "years_experience": 5,
            "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker"]
        }
        
        job_details = {
            "title": "Senior Software Engineer",
            "description": "We are looking for a senior software engineer with 5+ years of experience in Python and JavaScript.",
            "company": "Tech Corp"
        }
        
        company_info = {
            "name": "Tech Corp",
            "description": "Leading technology company specializing in web applications"
        }
        
        cover_letter = generator.generate_cover_letter(user_profile, job_details, company_info)
        print("✅ Cover letter generated successfully")
        print(f"Cover letter length: {len(cover_letter['cover_letter'])} characters")
        return True
        
    except Exception as e:
        print(f"❌ Cover letter generation failed: {e}")
        return False

def test_cv_tailor():
    """Test CV tailoring."""
    print("\nTesting CV Tailor...")
    
    try:
        tailor = CVTailor()
        
        base_resume = {
            "summary": "Experienced software engineer with 5+ years in web development",
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Corp",
                    "duration": "2021-2024",
                    "description": "Developed web applications using Python and JavaScript"
                }
            ],
            "skills": {
                "Technical": ["Python", "JavaScript", "React"],
                "Soft Skills": ["Leadership", "Communication"]
            }
        }
        
        job_description = "We are seeking a senior Python developer with experience in React and AWS. Must have strong communication skills and leadership experience."
        
        tailored_cv = tailor.tailor_cv(base_resume, job_description)
        print("✅ CV tailored successfully")
        print(f"Keywords matched: {tailored_cv['tailored_resume']['keywords_matched']}")
        return True
        
    except Exception as e:
        print(f"❌ CV tailoring failed: {e}")
        return False

def test_email_generator():
    """Test email generation."""
    print("\nTesting Email Generator...")
    
    try:
        generator = EmailGenerator()
        
        user_profile = {
            "full_name": "John Doe",
            "email": "john.doe@email.com"
        }
        
        job_details = {
            "title": "Senior Software Engineer",
            "company": "Tech Corp"
        }
        
        email = generator.generate_follow_up_email(
            user_profile=user_profile,
            job_details=job_details,
            email_type="thank_you",
            context={"interview_date": "2024-01-15", "interviewer_name": "Jane Smith"}
        )
        
        print("✅ Email generated successfully")
        print(f"Email subject: {email['subject']}")
        return True
        
    except Exception as e:
        print(f"❌ Email generation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing AI Generators...")
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Tests will fail.")
        print("Please set: export OPENAI_API_KEY=your_key_here")
        return
    
    tests = [
        test_resume_generator,
        test_cover_letter_generator,
        test_cv_tailor,
        test_email_generator
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AI generators are working correctly.")
    else:
        print("❌ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
