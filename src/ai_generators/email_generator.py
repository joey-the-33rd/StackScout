"""Email generator for job application follow-ups."""
from typing import Dict, Any, Optional
from datetime import datetime
from .base_generator import BaseAIGenerator

class EmailGenerator(BaseAIGenerator):
    """AI-powered email generator for job application follow-ups."""
    
    def __init__(self):
        super().__init__()
    
    def generate_follow_up_email(self, user_profile: Dict[str, Any], job_details: Dict[str, Any], 
                               email_type: str = "thank_you", context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a follow-up email for job applications."""
        
        context = context or {}
        email_content = self._create_email_content(user_profile, job_details, email_type, context)
        
        return {
            "email_type": email_type,
            "subject": self._generate_subject(email_type, job_details),
            "body": email_content,
            "recipient": job_details.get('contact_email', 'hiring@company.com'),
            "generated_at": datetime.now().isoformat()
        }
    
    def _create_email_content(self, user_profile: Dict[str, Any], job_details: Dict[str, Any], 
                            email_type: str, context: Dict[str, Any]) -> str:
        """Create the email content based on type."""
        
        if email_type == "thank_you":
            return self._generate_thank_you_email(user_profile, job_details, context)
        elif email_type == "application_follow_up":
            return self._generate_application_follow_up(user_profile, job_details, context)
        elif email_type == "interview_follow_up":
            return self._generate_interview_follow_up(user_profile, job_details, context)
        elif email_type == "status_inquiry":
            return self._generate_status_inquiry(user_profile, job_details, context)
        else:
            return self._generate_custom_email(user_profile, job_details, context)
    
    def _generate_thank_you_email(self, user_profile: Dict[str, Any], job_details: Dict[str, Any], 
                                context: Dict[str, Any]) -> str:
        """Generate thank you email after interview."""
        
        interview_date = context.get('interview_date', 'recently')
        interviewer_name = context.get('interviewer_name', 'the team')
        key_points = context.get('key_points', [])
        
        prompt = f"""
        Write a professional thank you email for {user_profile.get('full_name')} 
        after interviewing for the {job_details.get('title')} position at {job_details.get('company')}.
        
        Interview details:
        - Date: {interview_date}
        - Interviewer: {interviewer_name}
        - Key discussion points: {', '.join(key_points) if key_points else 'role responsibilities and company culture'}
        
        Guidelines:
        - Keep it concise (3-4 paragraphs)
        - Express gratitude for their time
        - Reiterate interest in the position
        - Reference specific conversation points
        - End with next steps
        """
        
        return self.generate_content(prompt, {
            "user": user_profile,
            "job": job_details,
            "context": context
        }, max_tokens=300)
    
    def _generate_application_follow_up(self, user_profile: Dict[str, Any], job_details: Dict[str, Any], 
                                      context: Dict[str, Any]) -> str:
        """Generate follow-up email after application submission."""
        
        application_date = context.get('application_date', 'recently')
        
        prompt = f"""
        Write a professional follow-up email for {user_profile.get('full_name')} 
        regarding the {job_details.get('title')} position at {job_details.get('company')}.
        
        Application submitted: {application_date}
        
        Guidelines:
        - Express continued interest
        - Inquire about application status
        - Keep it brief and professional
        - Include contact information
        """
        
        return self.generate_content(prompt, {
            "user": user_profile,
            "job": job_details,
            "context": context
        }, max_tokens=250)
    
    def _generate_interview_follow_up(self, user_profile: Dict[str, Any], job_details: Dict[str, Any], 
                                    context: Dict[str, Any]) -> str:
        """Generate follow-up email after interview waiting period."""
        
        interview_date = context.get('interview_date', '')
        waiting_period = context.get('waiting_period', 'a week')
        
        prompt = f"""
        Write a professional follow-up email for {user_profile.get('full_name')} 
        after interviewing for the {job_details.get('title')} position at {job_details.get('company')}.
        
        Interview date: {interview_date}
        Waiting period: {waiting_period}
        
        Guidelines:
        - Express continued interest
        - Politely inquire about timeline
        - Reiterate key qualifications
        - Keep it professional and concise
        """
        
        return self.generate_content(prompt, {
            "user": user_profile,
            "job": job_details,
            "context": context
        }, max_tokens=250)
    
    def _generate_status_inquiry(self, user_profile: Dict[str, Any], job_details: Dict[str, Any], 
                               context: Dict[str, Any]) -> str:
        """Generate status inquiry email."""
        
        last_contact = context.get('last_contact', '')
        
        prompt = f"""
        Write a professional status inquiry email for {user_profile.get('full_name')} 
        regarding the {job_details.get('title')} position at {job_details.get('company')}.
        
        Last contact: {last_contact}
        
        Guidelines:
        - Be polite and professional
        - Express continued interest
        - Ask for timeline update
        - Keep it brief
        """
        
        return self.generate_content(prompt, {
            "user": user_profile,
            "job": job_details,
            "context": context
        }, max_tokens=200)
    
    def _generate_custom_email(self, user_profile: Dict[str, Any], job_details: Dict[str, Any], 
                             context: Dict[str, Any]) -> str:
        """Generate custom email based on specific context."""
        
        custom_prompt = context.get('custom_prompt', '')
        
        prompt = f"""
        Write a professional email for {user_profile.get('full_name')} 
        regarding the {job_details.get('title')} position at {job_details.get('company')}.
        
        Custom instructions: {custom_prompt}
        
        Guidelines:
        - Professional tone
        - Clear and concise
        - Include relevant details
        """
        
        return self.generate_content(prompt, {
            "user": user_profile,
            "job": job_details,
            "context": context
        }, max_tokens=300)
    
    def _generate_subject(self, email_type: str, job_details: Dict[str, Any]) -> str:
        """Generate appropriate email subject line."""
        
        job_title = job_details.get('title', 'Position')
        company_name = job_details.get('company', 'Company')
        
        subjects = {
            "thank_you": f"Thank you - {job_title} Interview",
            "application_follow_up": f"Follow-up: {job_title} Application",
            "interview_follow_up": f"Follow-up: {job_title} Interview",
            "status_inquiry": f"Status Update: {job_title} Application"
        }
        
        return subjects.get(email_type, f"Regarding {job_title} at {company_name}")
    
    def generate_email_templates(self, user_profile: Dict[str, Any]) -> Dict[str, str]:
        """Generate reusable email templates for common scenarios."""
        
        templates = {}
        
        # Thank you template
        templates["thank_you"] = self._generate_template("thank_you", user_profile)
        
        # Application follow-up template
        templates["application_follow_up"] = self._generate_template("application_follow_up", user_profile)
        
        # Interview follow-up template
        templates["interview_follow_up"] = self._generate_template("interview_follow_up", user_profile)
        
        return templates
    
    def _generate_template(self, template_type: str, user_profile: Dict[str, Any]) -> str:
        """Generate a reusable email template."""
        
        prompt = f"""
        Create a reusable email template for {template_type} emails.
        
        User: {user_profile.get('full_name', 'Applicant')}
        
        Include placeholders for:
        - Job title: [JOB_TITLE]
        - Company name: [COMPANY_NAME]
        - Interview date: [INTERVIEW_DATE]
        - Interviewer name: [INTERVIEWER_NAME]
        
        Keep it professional and adaptable.
        """
        
        return self.generate_content(prompt, {
            "user": user_profile,
            "type": template_type
        }, max_tokens=300)
