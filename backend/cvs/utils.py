from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from django.http import HttpResponse
import json
import re
from datetime import datetime
import os

class CVPDFGenerator:
    def __init__(self, cv):
        self.cv = cv
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(
            self.buffer, 
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        self.styles = getSampleStyleSheet()
        self.elements = []
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=10,
            textColor=colors.HexColor('#2563eb'),
            alignment=1  # TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#4b5563'),
            spaceAfter=20,
            alignment=1
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.HexColor('#1f2937'),
            borderWidth=1,
            borderColor=colors.HexColor('#e5e7eb'),
            borderPadding=8,
            borderRadius=5,
            backColor=colors.HexColor('#f3f4f6')
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=2,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            spaceAfter=2
        ))
        
        self.styles.add(ParagraphStyle(
            name='DateLocation',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.gray,
            spaceAfter=5
        ))
        
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=4,
            bulletIndent=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4b5563'),
            alignment=1,
            spaceAfter=5
        ))

    def add_header(self):
        """Add personal information header"""
        # Name
        if self.cv.profile and self.cv.profile.user:
            first_name = self.cv.profile.user.first_name or ''
            last_name = self.cv.profile.user.last_name or ''
            name = f"{first_name} {last_name}".strip()
            if not name:
                name = self.cv.profile.user.username or 'Candidate'
            self.elements.append(Paragraph(name.upper(), self.styles['CustomTitle']))
        
        # Professional Title
        if self.cv.profile and self.cv.profile.title:
            self.elements.append(Paragraph(self.cv.profile.title, self.styles['Subtitle']))
        
        # Contact Info
        contact_info = []
        if self.cv.profile and self.cv.profile.location:
            contact_info.append(self.cv.profile.location)
        if self.cv.profile and self.cv.profile.phone:
            contact_info.append(self.cv.profile.phone)
        if self.cv.profile and self.cv.profile.user and self.cv.profile.user.email:
            contact_info.append(self.cv.profile.user.email)
        
        if contact_info:
            self.elements.append(Paragraph(" | ".join(contact_info), self.styles['ContactInfo']))
        
        self.elements.append(Spacer(1, 0.2*inch))

    def add_summary(self):
        """Add professional summary"""
        if self.cv.content and self.cv.content.get('summary'):
            self.elements.append(Paragraph("PROFESSIONAL SUMMARY", self.styles['SectionHeader']))
            self.elements.append(Paragraph(self.cv.content['summary'], self.styles['Normal']))
            self.elements.append(Spacer(1, 0.2*inch))

    def add_work_experience(self):
        """Add work experience section"""
        work_exp = None
        if self.cv.content and self.cv.content.get('work_experience'):
            work_exp = self.cv.content['work_experience']
        elif self.cv.profile and hasattr(self.cv.profile, 'work_experiences'):
            work_exp = [
                {
                    'title': exp.title,
                    'company': exp.company,
                    'location': exp.location,
                    'start_date': exp.start_date.strftime('%Y-%m') if exp.start_date else '',
                    'end_date': 'Present' if exp.current else (exp.end_date.strftime('%Y-%m') if exp.end_date else ''),
                    'description': exp.description
                }
                for exp in self.cv.profile.work_experiences.all()
            ]
        
        if work_exp and len(work_exp) > 0:
            self.elements.append(Paragraph("WORK EXPERIENCE", self.styles['SectionHeader']))
            
            for exp in work_exp:
                title = exp.get('title', '')
                company = exp.get('company', '')
                if title and company:
                    self.elements.append(Paragraph(f"<b>{title}</b> at {company}", self.styles['JobTitle']))
                elif title:
                    self.elements.append(Paragraph(f"<b>{title}</b>", self.styles['JobTitle']))
                
                date_location = []
                if exp.get('location'):
                    date_location.append(exp['location'])
                
                start = exp.get('start_date', '')
                end = exp.get('end_date', '')
                if start or end:
                    date_str = f"{start} - {end}" if start and end else start or end
                    date_location.append(date_str)
                
                if date_location:
                    self.elements.append(Paragraph(" | ".join(date_location), self.styles['DateLocation']))
                
                if exp.get('description'):
                    desc_text = exp['description']
                    if '•' in desc_text:
                        bullets = desc_text.split('•')
                    elif '\n' in desc_text:
                        bullets = desc_text.split('\n')
                    else:
                        bullets = [desc_text]
                    
                    for bullet in bullets:
                        bullet = bullet.strip()
                        if bullet and len(bullet) > 2:
                            self.elements.append(Paragraph(f"• {bullet}", self.styles['BulletPoint']))
                
                self.elements.append(Spacer(1, 0.1*inch))

    def add_education(self):
        """Add education section"""
        education = None
        if self.cv.content and self.cv.content.get('education'):
            education = self.cv.content['education']
        elif self.cv.profile and hasattr(self.cv.profile, 'education'):
            education = [
                {
                    'degree': edu.degree,
                    'institution': edu.institution,
                    'location': edu.location,
                    'start_date': edu.start_date.strftime('%Y-%m') if edu.start_date else '',
                    'end_date': 'Present' if edu.current else (edu.end_date.strftime('%Y-%m') if edu.end_date else ''),
                    'gpa': edu.gpa
                }
                for edu in self.cv.profile.education.all()
            ]
        
        if education and len(education) > 0:
            self.elements.append(Paragraph("EDUCATION", self.styles['SectionHeader']))
            
            for edu in education:
                degree = edu.get('degree', '')
                institution = edu.get('institution', '')
                if degree and institution:
                    self.elements.append(Paragraph(f"<b>{degree}</b> - {institution}", self.styles['JobTitle']))
                elif degree:
                    self.elements.append(Paragraph(f"<b>{degree}</b>", self.styles['JobTitle']))
                
                date_location = []
                if edu.get('location'):
                    date_location.append(edu['location'])
                
                start = edu.get('start_date', '')
                end = edu.get('end_date', '')
                if start or end:
                    date_str = f"{start} - {end}" if start and end else start or end
                    date_location.append(date_str)
                
                if date_location:
                    self.elements.append(Paragraph(" | ".join(date_location), self.styles['DateLocation']))
                
                if edu.get('gpa'):
                    self.elements.append(Paragraph(f"GPA: {edu['gpa']}", self.styles['Normal']))
                
                self.elements.append(Spacer(1, 0.1*inch))

    def add_skills(self):
        """Add skills section"""
        skills = None
        if self.cv.content and self.cv.content.get('skills'):
            skills = self.cv.content['skills']
        elif self.cv.profile and hasattr(self.cv.profile, 'skills'):
            skills = [skill.name for skill in self.cv.profile.skills.all()]
        
        if skills and len(skills) > 0:
            self.elements.append(Paragraph("SKILLS", self.styles['SectionHeader']))
            
            skill_rows = [skills[i:i+3] for i in range(0, len(skills), 3)]
            for row in skill_rows:
                while len(row) < 3:
                    row.append('')
                
                table_data = [[Paragraph(skill, self.styles['Normal']) for skill in row]]
                table = Table(table_data, colWidths=[2*inch, 2*inch, 2*inch])
                table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                self.elements.append(table)
            
            self.elements.append(Spacer(1, 0.1*inch))

    def add_projects(self):
        """Add projects section"""
        projects = None
        if self.cv.content and self.cv.content.get('projects'):
            projects = self.cv.content['projects']
        elif self.cv.profile and hasattr(self.cv.profile, 'projects'):
            projects = [
                {
                    'name': proj.name,
                    'description': proj.description,
                    'technologies': proj.technologies
                }
                for proj in self.cv.profile.projects.all()
            ]
        
        if projects and len(projects) > 0:
            self.elements.append(Paragraph("PROJECTS", self.styles['SectionHeader']))
            
            for project in projects:
                name = project.get('name', '')
                if name:
                    self.elements.append(Paragraph(f"<b>{name}</b>", self.styles['JobTitle']))
                
                if project.get('description'):
                    self.elements.append(Paragraph(project['description'], self.styles['Normal']))
                
                if project.get('technologies'):
                    tech_list = project['technologies']
                    if isinstance(tech_list, list) and len(tech_list) > 0:
                        tech_str = "Technologies: " + ", ".join(tech_list)
                        self.elements.append(Paragraph(tech_str, self.styles['DateLocation']))
                
                self.elements.append(Spacer(1, 0.1*inch))

    def add_certifications(self):
        """Add certifications section"""
        certifications = None
        if self.cv.content and self.cv.content.get('certifications'):
            certifications = self.cv.content['certifications']
        elif self.cv.profile and hasattr(self.cv.profile, 'certifications'):
            certifications = [
                {
                    'name': cert.name,
                    'issuer': cert.issuer
                }
                for cert in self.cv.profile.certifications.all()
            ]
        
        if certifications and len(certifications) > 0:
            self.elements.append(Paragraph("CERTIFICATIONS", self.styles['SectionHeader']))
            
            for cert in certifications:
                name = cert.get('name', '')
                issuer = cert.get('issuer', '')
                
                if name and issuer:
                    self.elements.append(Paragraph(f"• <b>{name}</b> - {issuer}", self.styles['BulletPoint']))
                elif name:
                    self.elements.append(Paragraph(f"• {name}", self.styles['BulletPoint']))
            
            self.elements.append(Spacer(1, 0.1*inch))

    def generate(self):
        """Generate the PDF"""
        try:
            self.add_header()
            self.add_summary()
            self.add_work_experience()
            self.add_education()
            self.add_skills()
            self.add_projects()
            self.add_certifications()
            
            self.doc.build(self.elements)
            
            pdf = self.buffer.getvalue()
            self.buffer.close()
            
            return pdf
        except Exception as e:
            print(f"PDF Generation Error: {e}")
            import traceback
            traceback.print_exc()
            raise


def generate_cv_pdf(cv):
    """Generate PDF for a CV"""
    generator = CVPDFGenerator(cv)
    return generator.generate()


def download_cv_response(cv):
    """Create HTTP response for CV download"""
    try:
        pdf = generate_cv_pdf(cv)
        
        response = HttpResponse(pdf, content_type='application/pdf')
        
        job_title = cv.job_title or 'CV'
        job_title = re.sub(r'[^\w\s-]', '', job_title)
        job_title = re.sub(r'[-\s]+', '_', job_title)
        
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{job_title}_{date_str}.pdf"
        
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(pdf)
        
        return response
        
    except Exception as e:
        print(f"Error creating download response: {e}")
        import traceback
        traceback.print_exc()
        raise


def render_cv_with_template(cv_content, template_obj):
    """
    Render CV content using a custom HTML template
    """
    if not template_obj or not template_obj.html_file:
        return None
    
    try:
        # Read template HTML
        with open(template_obj.html_file.path, 'r', encoding='utf-8') as f:
            template_html = f.read()
        
        # Read CSS if exists
        css_content = ''
        if template_obj.css_file:
            with open(template_obj.css_file.path, 'r', encoding='utf-8') as f:
                css_content = f.read()
        
        # Prepare context data
        context = {
            'fullName': cv_content.get('personal', {}).get('fullName', ''),
            'email': cv_content.get('personal', {}).get('email', ''),
            'phone': cv_content.get('personal', {}).get('phone', ''),
            'location': cv_content.get('personal', {}).get('location', ''),
            'title': cv_content.get('personal', {}).get('title', ''),
            'summary': cv_content.get('summary', ''),
            'workExperience': cv_content.get('work_experience', []),
            'education': cv_content.get('education', []),
            'skills': cv_content.get('skills', []),
            'projects': cv_content.get('projects', []),
            'certifications': cv_content.get('certifications', []),
        }
        
        # Simple placeholder replacement
        for key, value in context.items():
            if isinstance(value, str):
                template_html = template_html.replace(f'{{{{{key}}}}}', value)
            elif isinstance(value, list):
                placeholder = f'{{{{#each {key}}}}}'
                end_placeholder = f'{{{{/each}}}}'
                
                if placeholder in template_html and end_placeholder in template_html:
                    pattern = re.escape(placeholder) + '(.*?)' + re.escape(end_placeholder)
                    match = re.search(pattern, template_html, re.DOTALL)
                    
                    if match:
                        item_template = match.group(1)
                        items_html = ''
                        
                        for item in value:
                            item_html = item_template
                            for item_key, item_value in item.items():
                                if isinstance(item_value, str):
                                    item_html = item_html.replace(f'{{{{{item_key}}}}}', item_value)
                            items_html += item_html
                        
                        template_html = template_html.replace(placeholder + item_template + end_placeholder, items_html)
        
        # Add CSS
        if css_content:
            if '</head>' in template_html:
                template_html = template_html.replace('</head>', f'<style>{css_content}</style></head>')
            else:
                template_html = f'<style>{css_content}</style>\n{template_html}'
        
        return template_html
        
    except Exception as e:
        print(f"Template rendering error: {e}")
        import traceback
        traceback.print_exc()
        return None