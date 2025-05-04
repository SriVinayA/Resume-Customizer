import { CustomizeResumeResponse } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/**
 * Customize resume with job description and resume
 */
export const customizeResume = async (jobDescription: string, resumeFile: File): Promise<CustomizeResumeResponse> => {
  const formData = new FormData();
  formData.append('job_description_text', jobDescription);
  formData.append('resume', resumeFile);

  const response = await fetch(`${API_BASE_URL}/customize-resume/`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to customize resume');
  }

  return response.json();
};

export const getApiBaseUrl = (): string => {
  return API_BASE_URL;
}; 