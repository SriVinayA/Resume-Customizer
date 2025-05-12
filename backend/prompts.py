"""
Prompts Module

This module contains all the prompts used by the AI service in the application.
Centralizing prompts makes them easier to maintain and update.
"""

# System prompts
DOCUMENT_PARSER_SYSTEM_PROMPT = "You are an expert document parser specialized in resume and job description analysis."
RESUME_CUSTOMIZER_SYSTEM_PROMPT = """You are an expert resume architect and ATS optimization specialist that customizes resumes to match job descriptions while following strict preservation and modification rules. 

Your primary goal is to significantly increase the resume's ATS compatibility score by strategically incorporating keywords and phrases from the job description, restructuring content for maximum relevance, and highlighting quantifiable achievements.

IMPORTANT: 
- Never include structural markers like '(Situation)', '(Task)', '(Action)', '(Result)' in the final content - use these only as frameworks for creating the content. 
- Use proper category names without underscores (e.g., 'Web Technologies' not 'web_technologies', 'Tools & Frameworks' not 'tools_frameworks'). 
- For job titles, use ONLY the title without technology stacks in parentheses.
- Your customizations must significantly improve the resume's chances of passing through ATS filters by achieving at least a 30% increase in keyword relevance and content alignment."""

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

**Task:** Create a tailored resume by customizing the provided resume JSON to better match the job description JSON. Use the STAR method (Situation, Task, Action, Result) to craft accomplishment-driven statements. Ensure the resume is ATS-compliant and aligned with industry best practices, including formatting and keyword optimization.

**PRIORITIZATION (CRITICAL):**
1. Accuracy and truthfulness above all - never fabricate experience or qualifications
2. Preserve all structural elements as specified in the preservation rules
3. Relevance to the job description by naturally integrating keywords from the job description JSON
4. Highlight quantifiable achievements using the STAR method based on the candidate's actual experience in the resume JSON
5. Optimize for ATS by using exact keyword matches where natural and appropriate

### **Ethical Guidelines (CRITICAL)**:
- NEVER engage in "keyword stuffing" (excessive, unnatural repetition of keywords). Focus on relevance and quality.
- NEVER use hidden text (e.g., white font) or other deceptive tactics to manipulate ATS scoring. This is easily detectable and will lead to disqualification.
- Ensure all content is truthful and accurately reflects the candidate's experience and skills. Do not fabricate or exaggerate qualifications.

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
   - Rewrite the experience bullet points from the input resume JSON using the STAR method. Ensure each rewritten bullet point accurately reflects the candidate's original achievement while integrating relevant keywords from the job description and quantifying results where possible. Focus on highlighting aspects of the candidate's *actual* experience that match the job requirements.
   - CRITICAL: Ensure that each bullet point is directly relevant to its associated job title. The achievements and responsibilities described must clearly align with what would be expected for that specific role.
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
   - Analyze all skills present in the input `resume_json` and the keywords/requirements listed in the `job_description_json`.
   - Organize technical skills into meaningful categories that align with the job description. Examples of technical skill categories include:
     - Programming Languages (e.g., Python, Java, C++, Go)
     - Databases (e.g., PostgreSQL, MySQL, MongoDB, Redis)
     - Cloud Services (e.g., AWS, Azure, GCP)
     - DevOps Tools (e.g., Docker, Kubernetes, Terraform)
     - Frameworks (e.g., React, Django, Spring)
     - Data Tools (e.g., PowerBI, Tableau, PySpark)
   - **CRITICAL: Each technical skill should appear in ONLY ONE category to avoid duplication.**
   - Add a final "Soft Skills" category that includes interpersonal and professional attributes like:
     - Communication
     - Leadership
     - Problem-solving
     - Teamwork
     - Analytical Thinking
   - Ensure skills relevant to the job description are prominently included.
   - **Output Format:** The final skills section in the customized resume should be formatted as follows:
     ```
     [Technical Category 1]: [skill1, skill2, skill3, ...]
     [Technical Category 2]: [skill4, skill5, skill6, ...]
     ...
     Soft Skills: [soft skill1, soft skill2, soft skill3, ...]
     ```
   - Technical skills like "Data Analysis", "System Observability", "Performance Optimization", and "Automation" should be categorized as technical skills, not soft skills.
   - Use clear, industry-standard category names for technical skills (e.g., "Programming Languages", "Cloud & Infrastructure", "Databases").
   - **CRITICAL: Remove duplicate entries within each list.**

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
- skills: Return as an object with categorized technical skills followed by soft skills. Each technical skill category should be a key with an array of skills as its value. Include a "Soft Skills" key with an array of soft skills.
- projects: Return as an array of project objects, tailored and potentially filtered based on relevance.
- other: Any other sections, appropriately structured.

Also include a "modifications_summary" section that explains what changes were made and why (e.g., "Adjusted job title X to Y for better alignment", "Added keywords A, B, C to skills section", "Rewrote bullet points in experience section using STAR method and quantification", "Removed project Z due to low relevance").

Make sure all object properties and array items are properly formatted with correct JSON syntax.
""" 

# ATS evaluation prompt
ATS_EVALUATION_PROMPT = """
Evaluate this resume against the provided job description to determine its ATS (Applicant Tracking System) compatibility score and provide actionable improvements. 
**Your primary goal is to assess how well the resume aligns with the specific job description provided. A low degree of relevance or a significant mismatch in keywords, skills, and experience should result in a correspondingly low score.**

RESUME:
{resume_json}

JOB DESCRIPTION:
{job_description_json}

Analyze the resume for its compatibility with Applicant Tracking Systems using the following criteria. **Critically evaluate each point, especially concerning the direct relevance to the job description.**

1.  **Keyword Matching (40% of score weight):**
    *   How effectively does the resume incorporate essential keywords, phrases, and terminology directly from the job description?
    *   Are keywords used naturally and in relevant contexts?
    *   What percentage of critical job-specific keywords are present? A resume with >85% keyword coverage should score high in this category.
    *   **A low match rate for critical keywords should significantly decrease the score.**

2.  **Content Relevance (30% of score weight):**
    *   How well do the candidate's listed experiences, responsibilities, and achievements align with the requirements and duties outlined in the job description?
    *   Is the career trajectory and skill set presented in the resume a strong fit for the target role?
    *   **If the resume's content is largely unrelated to the job description, the score must be low.**

3.  **Technical Skills Alignment (20% of score weight):**
    *   Does the resume clearly list ALL technical skills that are explicitly mentioned or strongly implied in the job description?
    *   Is there a clear demonstration of proficiency in required technologies or tools?
    *   **Missing key technical skills required by the job should heavily impact the score.**

4.  **Formatting and Impact (10% of score weight):**
    *   Is the resume well-structured with clear section headings and bullet points?
    *   Does it use quantifiable metrics and achievements relevant to the job?
    *   Is the formatting ATS-friendly (avoiding tables, images, columns that can confuse parsers)?

SCORING GUIDELINES:
- 90-100: Exceptional match - nearly all keywords present with highly relevant experience
- 75-89: Strong match - most key requirements covered with aligned experience
- 60-74: Good match - covers many requirements but has some gaps
- 40-59: Moderate match - covers some requirements but significant areas missing
- Below 40: Poor match - fundamental mismatch between resume and job description

Return a JSON response with:
1.  "score": A numeric score between 0-100 representing ATS compatibility. 
    *   **This score MUST heavily reflect the degree of alignment between the resume and the job description.**
    *   **For original resumes: Assign appropriate scores based on existing alignment, typically below 50 for partially mismatched content.**
    *   **For optimized resumes: If properly customized with relevant keywords and content, scores should be at least 30-40 points higher than unoptimized versions. Well-optimized resumes should achieve scores of 75+.**

2.  "improvements": An array of specific, actionable suggestions for improving the resume's alignment with THIS job description and ATS performance.

3.  "keyword_match_analysis": An object containing:
    *   "matched_keywords": Array of crucial keywords from the job description found in the resume.
    *   "missing_keywords": Array of important keywords from the job description that are missing or underrepresented in the resume.
    *   "keyword_match_percentage": Numeric percentage (0-100) of key job description terms found in the resume.

4.  "section_scores": An object with scores (0-100) for each major section, reflecting their relevance and quality against the job description:
    *   "skills_score": Rating of skills section against job requirements.
    *   "experience_score": Rating of experience section against job requirements.
    *   "education_score": Rating of education section against job requirements.
    *   "overall_format_score": Rating of overall formatting and ATS-friendliness.

Provide clear, actionable suggestions focused on enhancing the resume's chances for THIS specific job.
""" 