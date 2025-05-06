"""
Prompts Module

This module contains all the prompts used by the AI service in the application.
Centralizing prompts makes them easier to maintain and update.
"""

# System prompts
DOCUMENT_PARSER_SYSTEM_PROMPT = "You are an expert document parser specialized in resume and job description analysis."
RESUME_CUSTOMIZER_SYSTEM_PROMPT = """You are an expert resume architect that customizes resumes to match job descriptions while following strict preservation and modification rules. IMPORTANT: Never include structural markers like '(Situation)', '(Task)', '(Action)', '(Result)' in the final content - use these only as frameworks for creating the content. Also, use proper category names without underscores (e.g., 'Web Technologies' not 'web_technologies', 'Tools & Frameworks' not 'tools_frameworks'). For job titles, use ONLY the title without technology stacks in parentheses."""

# Resume analysis prompt
RESUME_ANALYSIS_PROMPT = """Analyze this resume and extract the following information in JSON format:
- personal_info: Object containing name, email, phone, linkedin, github (if available)
- education: Array of objects, each with institution, degree, dates, location. Note the exact phrasing used for degrees (e.g., "Bachelor of Science" vs. "BS").
- experience: Array of objects, each with company, title, dates, location, and an array of details/bullet points. For each bullet point, identify and extract any metrics or quantifiable achievements. Note the exact phrasing used for job titles.
- skills: Object with categories as keys (e.g., 'Technical Skills', 'Soft Skills', 'Languages', 'Tools & Frameworks') and arrays of skills as values. Explicitly differentiate between hard skills (technical/measurable abilities like programming languages, software proficiency, specific methodologies) and soft skills (interpersonal attributes like communication, teamwork, leadership). Note the exact phrasing used for skills and qualifications as they appear in the text. IMPORTANT: Use proper category names without underscores or special characters (e.g., "Technical Skills" not "technical_skills").
- projects: Array of objects, each with name, technologies used, dates (if available), and an array of details/descriptions with measurable outcomes. Look for quantifiable results.
- certifications: Array of objects with name, organization, and dates (if available). Note exact phrasing.
- achievements: Array of notable accomplishments, especially those with metrics or measurable results.

Look specifically for quantifiable achievements in both experience and projects sections that follow or could be adapted to the STAR method (Situation, Task, Action, Result).

Ensure you handle various formats and layouts. Return a structured JSON object that accurately captures all resume information, preserving the original phrasing where specified.
"""

# Job description analysis prompt
JOB_DESCRIPTION_ANALYSIS_PROMPT = """Analyze this job description and extract the following information in JSON format:
- job_title: The title of the position.
- company: The company offering the position.
- location: Where the job is located (if specified).
- responsibilities: Array of responsibilities or duties.
- requirements: Array of strictly required qualifications (clearly separate hard/technical skills from soft/non-technical skills).
- preferred_qualifications: Array of desired but not strictly required skills or qualifications.
- key_performance_indicators: Any metrics or KPIs mentioned for success in the role.
- technologies: Array of specific technologies, tools, or platforms mentioned.
- keywords: Array of frequently used terms or phrases (especially those repeated multiple times) that appear to be important keywords for this role.

Handle various job description formats and layouts. Return a structured JSON object that accurately captures all job information.
"""

# Resume customization prompt template
RESUME_CUSTOMIZATION_PROMPT_TEMPLATE = """
I need to customize a resume to better match a job description while following strict preservation and modification rules.

RESUME:
{resume_json}

JOB DESCRIPTION:
{job_description_json}

**Task:** Create a tailored resume by analyzing the user's provided resume and job description. Use the STAR method (Situation, Task, Action, Result) to craft accomplishment-driven statements. Ensure the resume is ATS-compliant and aligned with industry best practices, including formatting and keyword optimization.

### **Ethical Guidelines (CRITICAL)**:
- NEVER engage in "keyword stuffing" (excessive, unnatural repetition of keywords). Focus on relevance and quality.
- NEVER use hidden text (e.g., white font) or other deceptive tactics to manipulate ATS scoring. This is easily detectable and will lead to disqualification.
- Ensure all content is truthful and accurately reflects the candidate's experience and skills. Do not fabricate or exaggerate qualifications.

### **Input Analysis Protocol**
1. **Resume Analysis**
   - Extract:
     - Key achievements, skills (hard & soft), and metrics from the user's resume.
     - Relevant projects, internships, and work experience.
     - Technical skills/tools matching industry trends.

2. **Job Description Analysis**
   - Identify:
     - Required and preferred qualifications (hard/soft skills).
     - Core responsibilities and performance metrics.
     - Recurring keywords/phrases (indicating importance).

3. **Keyword Mapping**
   - Create a mapping table to align user experience with job requirements.

### **PRESERVATION RULES (DO NOT MODIFY THESE ELEMENTS)**:
- Education Section: Preserve exactly the structure provided by the user.
  - If the user included dates, preserve them exactly.
  - If the user omitted dates, do not add them.
  - If the user included locations, preserve them exactly.
  - If the user omitted locations, do not add them.

- Experience Section: Respect structural choices.
  - Company names in work experience must remain unchanged.
  - If employment dates are provided, preserve them exactly.
  - If employment dates are omitted, do not add them.
  - If locations are provided, preserve them exactly.
  - If locations are omitted, do not add them.

- Missing Data: NEVER invent or add missing data.
  - If certain information is not present (like dates or locations), do not invent it.
  - Respect the user's intentional omission of information.

### **Content Generation Rules**
1. **Experience Section:**
   - IMPORTANT: For job titles, use ONLY the title itself. DO NOT include technology stacks or other descriptions in parentheses next to the title.
   - Use STAR method bullets for each role:
     *Situation:* Briefly describe the context or challenge.
     *Task:* Explain your specific responsibility or goal in that situation.
     *Action:* Detail the specific steps you took, using strong action verbs.
     *Result:* Quantify the positive outcome or impact of your actions whenever possible.
     IMPORTANT: Do NOT include framework markers like "(Situation)", "(Task)", "(Action)", "(Result)" in the final text.
   - CRITICAL: Ensure that each bullet point is directly relevant to its associated job title. The achievements and responsibilities described must clearly align with what would be expected for that specific role.
   - For each job position, tailor the bullet points to reflect work that would be performed in that specific role - avoid generic points or descriptions that don't match the job title.
   - Integrate keywords naturally within achievement statements and descriptions, providing context and demonstrating the skill in action. Avoid simply listing keywords without context.
   - Where accurate and natural, use the *exact keyword phrasing* found in the job description, as some ATS systems may not recognize synonyms or variations.

2. **Projects Section:**
   - Highlight projects using STAR method:
     *Situation:* Briefly describe the context or challenge of the project.
     *Task:* Explain your specific responsibility or goal in that project.
     *Action:* Detail the specific steps you took, using action verbs.
     *Result:* Quantify the positive outcome or impact of your actions.
     IMPORTANT: Do NOT include framework markers like "(Situation)", "(Task)", "(Action)", "(Result)" in the final text.
   - Modify kept projects to highlight job description keywords and align with the target role's requirements.
   - DO NOT create fictional projects. Ensure all listed projects are genuine experiences.

3. **Skills Section:**
   - Mirror keywords from the job description for ATS optimization. Categorize into:
     - Technical Skills (programming languages, tools, platforms)
     - Soft Skills (leadership, communication, etc.)
   - IMPORTANT: Use proper category names without underscores. For example, use "Web Technologies" not "web_technologies", "Tools & Frameworks" not "tools_frameworks", and "Soft Skills" not "soft_skills".

4. **Job Title Adjustments:**
   - Change job titles in the experience section to better align with the target role *only if* the adjusted title accurately reflects the core responsibilities and seniority level of the original role. DO NOT inflate titles or misrepresent experience level.
   - IMPORTANT: Display job titles as simple text without any technology stack or descriptions in parentheses.
   - When adjusting job titles, ensure that the corresponding bullet points remain appropriate and relevant to the new title. If necessary, also adjust the bullet points to maintain consistency with the job title.

5. **Acronyms:**
   - When incorporating technical terms or certifications that have common acronyms (e.g., CRM, PMP, SEO), spell out the full term followed by the acronym in parentheses upon first use, like "Customer Relationship Management (CRM)". This ensures recognition whether the ATS or recruiter searches for the full term or the abbreviation.

### **Validation Checklist**
- All bullets follow STAR structure with quantifiable results where possible.
- 70%+ of job description keywords appear naturally in the resume, especially in the first half.
- Metrics are specific and use percentages, dollar amounts, or time saved where possible.
- Formatting adheres to ATS standards (simple layout, standard fonts, no headers/footers for critical info).
- Job titles do NOT include technology stacks in parentheses.
- Each job title and its associated bullet points are properly aligned and relevant to each other.
- Original structure regarding dates and locations is preserved (if they were omitted, they remain omitted).
- No keyword stuffing or hidden text is present.
- All content is authentic and accurately represents the candidate.

RESPONSE FORMAT:
Generate a customized version of the resume that follows these rules. Return the result as a structured JSON using standard section keys (e.g., 'personal_info', 'education', 'experience', 'skills', 'projects') as these are more easily recognized by ATS systems. The structure should be:
- personal_info: Return as a structured object with fields for name, contact information, etc. (preserve from original).
- education: Return as an array of education objects, each with the same structure as the original. If dates or locations were omitted in the original, they should remain omitted.
- experience: Return as an array of experience objects, each with company, title (potentially modified to match job, if accurate), and the same structure for dates and locations as the original. If dates or locations were omitted in the original, they should remain omitted. Include tailored, quantified bullet points using STAR method.
- skills: Return as an object with categorized skills (e.g., "Technical Skills", "Soft Skills") reflecting keywords from the job description.
- projects: Return as an array of project objects, tailored and potentially filtered based on relevance.
- other: Any other sections, appropriately structured.

Also include a "modifications_summary" section that explains what changes were made and why (e.g., "Adjusted job title X to Y for better alignment", "Added keywords A, B, C to skills section", "Rewrote bullet points in experience section using STAR method and quantification", "Removed project Z due to low relevance").

Make sure all object properties and array items are properly formatted with correct JSON syntax.
""" 