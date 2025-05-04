import React, { useState } from 'react';
import GlassCard from './GlassCard';
import GlassButton from './GlassButton';

interface JobApplicationFormProps {
  onSubmit: (jobDescription: string, resumeFile: File) => Promise<void>;
  isLoading: boolean;
}

const JobApplicationForm: React.FC<JobApplicationFormProps> = ({ onSubmit, isLoading }) => {
  const [jobDescription, setJobDescription] = useState('');
  const [resumeFile, setResumeFile] = useState<File | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobDescription || !resumeFile) {
      alert('Please provide both a job description and a resume file');
      return;
    }
    
    try {
      await onSubmit(jobDescription, resumeFile);
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <GlassCard className="p-8 max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="jobDescription" className="block mb-2 font-medium">
            Job Description
          </label>
          <textarea
            id="jobDescription"
            rows={8}
            className="w-full p-3 glassmorphism bg-white/5 outline-none focus:border-white/30"
            placeholder="Paste the job description here"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            required
          />
        </div>
        
        <div>
          <label htmlFor="resumeFile" className="block mb-2 font-medium">
            Upload Resume (PDF)
          </label>
          <div className="flex items-center space-x-4">
            <input
              type="file"
              id="resumeFile"
              accept=".pdf"
              className="hidden"
              onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
              required
            />
            <label 
              htmlFor="resumeFile" 
              className="glassmorphism cursor-pointer p-3 bg-white/5 flex-1 text-center"
            >
              {resumeFile ? resumeFile.name : 'Click to select your resume PDF'}
            </label>
            {resumeFile && (
              <button 
                type="button" 
                className="glassmorphism p-2 bg-red-500/20 hover:bg-red-500/30"
                onClick={() => setResumeFile(null)}
              >
                Clear
              </button>
            )}
          </div>
        </div>

        <div className="flex justify-center pt-4">
          <GlassButton 
            type="submit" 
            className="text-lg py-3 px-12 rounded-full" 
            disabled={isLoading}
          >
            {isLoading ? 'Processing...' : 'Process Application'}
          </GlassButton>
        </div>
      </form>
    </GlassCard>
  );
};

export default JobApplicationForm; 