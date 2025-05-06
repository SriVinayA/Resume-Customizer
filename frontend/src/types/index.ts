export interface ResumeSection {
  [key: string]: string | string[] | unknown;
}

export interface ParsedResume {
  personal_info: {
    name?: string;
    email?: string;
    phone?: string;
    linkedin?: string;
    github?: string;
    [key: string]: string | undefined;
  };
  education: Array<{
    institution: string;
    degree: string;
    dates: string;
    location?: string;
    [key: string]: string | undefined;
  }>;
  experience: Array<{
    company: string;
    title: string;
    dates: string;
    location?: string;
    details?: string[];
    [key: string]: string | string[] | undefined;
  }>;
  skills: {
    [category: string]: string[] | {
      [subCategory: string]: string[];
    };
  };
  projects?: Array<{
    name: string;
    technologies: string | string[];
    dates?: string;
    details?: string[];
    [key: string]: string | string[] | undefined;
  }>;
  certifications?: Array<{
    name: string;
    organization: string;
    dates?: string;
    [key: string]: string | undefined;
  }>;
  achievements?: string[];
  [key: string]: unknown;
}

export interface JobDescription {
  overview?: string;
  responsibilities?: string;
  requirements?: string;
  qualifications?: string;
  preferred_skills?: string;
  [key: string]: string | undefined;
}

export interface CustomizeResumeResponse {
  success: boolean;
  customized_resume?: ParsedResume;
  pdf_path?: string;
  s3_pdf_url?: string;
  json_path?: string;
  s3_json_url?: string;
  modifications_summary?: string;
  [key: string]: unknown | boolean | string | ParsedResume | undefined;
} 