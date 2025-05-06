import React from 'react';
import GlassCard from './GlassCard';
import GlassButton from './GlassButton';
import { CustomizeResumeResponse } from '@/types';

interface ResultDisplayProps {
  result: CustomizeResumeResponse | null;
  onReset: () => void;
  apiBaseUrl: string;
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({ result, onReset, apiBaseUrl }) => {
  if (!result) return null;

  const handleDownloadPdf = () => {
    if (result.s3_pdf_url) {
      // Use S3 URL if available
      window.open(`${apiBaseUrl}/download-pdf/?s3_url=${encodeURIComponent(result.s3_pdf_url)}`, '_blank');
    } else if (result.pdf_path) {
      // Fall back to local path
      window.open(`${apiBaseUrl}/download-pdf/?path=${result.pdf_path}`, '_blank');
    }
  };

  const handleViewPdf = () => {
    if (result.s3_pdf_url) {
      // Use S3 URL if available
      window.open(`${apiBaseUrl}/view-pdf/?s3_url=${encodeURIComponent(result.s3_pdf_url)}`, '_blank');
    } else if (result.pdf_path) {
      // Fall back to local path
      window.open(`${apiBaseUrl}/view-pdf/?path=${result.pdf_path}`, '_blank');
    }
  };

  const handleEditInOverleaf = async () => {
    if (!result.s3_pdf_url && !result.pdf_path) return;

    try {
      let latexUrl = '';
      
      // Determine which URL to use for LaTeX
      if (result.s3_pdf_url) {
        latexUrl = `${apiBaseUrl}/view-latex/?s3_url=${encodeURIComponent(result.s3_pdf_url)}`;
      } else if (result.pdf_path) {
        latexUrl = `${apiBaseUrl}/view-latex/?path=${result.pdf_path}`;
      }

      // Fetch the LaTeX content
      const response = await fetch(latexUrl);
      
      if (!response.ok) {
        throw new Error('Failed to fetch LaTeX content');
      }
      
      const latexContent = await response.text();
      
      // Create a form to post to Overleaf
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = 'https://www.overleaf.com/docs';
      form.target = '_blank';
      
      // Add the LaTeX content as a base64 encoded "snip_uri"
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'snip_uri';
      
      // Encode the LaTeX content
      const encodedContent = btoa(unescape(encodeURIComponent(latexContent)));
      input.value = `data:application/x-tex;base64,${encodedContent}`;
      
      form.appendChild(input);
      document.body.appendChild(form);
      
      // Submit the form
      form.submit();
      
      // Clean up the form
      document.body.removeChild(form);
    } catch (error) {
      console.error('Error preparing for Overleaf:', error);
      alert('Error preparing for Overleaf: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Result Header */}
      <GlassCard className="p-6 text-center">
        <h2 className="text-2xl font-bold mb-4">
          {result.success ? 'Resume Processing Complete!' : 'Processing Error'}
        </h2>
        <p className="opacity-80">
          {result.success 
            ? 'Your resume has been processed and customized to match the job description.' 
            : 'There was an error processing your resume. Please try again.'}
        </p>
      </GlassCard>

      {/* Results Section */}
      {result.success && (
        <>
          {/* Actions */}
          <div className="flex flex-wrap gap-4 justify-center">
            {result.pdf_path && (
              <>
                <GlassButton onClick={handleViewPdf} className="py-2 px-6">
                  View PDF Resume
                </GlassButton>
                <GlassButton onClick={handleDownloadPdf} className="py-2 px-6">
                  Download PDF Resume
                </GlassButton>
                <GlassButton 
                  onClick={handleEditInOverleaf} 
                  className="py-2 px-6 bg-green-500/20 hover:bg-green-500/30"
                >
                  Edit in Overleaf 🍃
                </GlassButton>
              </>
            )}
            <GlassButton onClick={onReset} variant="secondary" className="py-2 px-6">
              Process Another Resume
            </GlassButton>
          </div>

          {/* Modifications Summary */}
          {result.modifications_summary && (
            <GlassCard className="p-6">
              <h3 className="text-xl font-bold mb-3">Modifications Summary</h3>
              <p className="whitespace-pre-line">{result.modifications_summary}</p>
            </GlassCard>
          )}

          {/* Matching Skills */}
          {result.customized_resume?.skills && (
            <GlassCard className="p-6">
              <h3 className="text-xl font-bold mb-3">Skills</h3>
              <div className="space-y-4">
                {/* Handle both flat and nested skills structures */}
                {Object.entries(result.customized_resume.skills).map(([category, skills]) => {
                  // Check if skills is an object (nested categories) or an array
                  if (typeof skills === 'object' && !Array.isArray(skills)) {
                    // Handle nested categories (like Technical Skills containing sub-categories)
                    return (
                      <div key={category} className="space-y-3">
                        <h4 className="font-bold">{category}</h4>
                        {Object.entries(skills).map(([subCategory, subSkills]) => (
                          <div key={`${category}-${subCategory}`} className="ml-4">
                            <h5 className="font-medium mb-2">{subCategory}</h5>
                            <div className="flex flex-wrap gap-2">
                              {Array.isArray(subSkills) && subSkills.map((skill, idx) => (
                                <span 
                                  key={idx} 
                                  className="glassmorphism bg-green-500/10 px-3 py-1 rounded-full"
                                >
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    );
                  } else if (Array.isArray(skills)) {
                    // Handle flat categories (like Soft Skills)
                    return (
                      <div key={category}>
                        <h4 className="font-medium mb-2">{category}</h4>
                        <div className="flex flex-wrap gap-2">
                          {skills.map((skill, idx) => (
                            <span 
                              key={idx} 
                              className="glassmorphism bg-green-500/10 px-3 py-1 rounded-full"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    );
                  }
                  return null;
                })}
              </div>
            </GlassCard>
          )}

          {/* Experience Highlights */}
          {result.customized_resume?.experience && result.customized_resume.experience.length > 0 && (
            <GlassCard className="p-6">
              <h3 className="text-xl font-bold mb-3">Experience Highlights</h3>
              <div className="space-y-6">
                {result.customized_resume.experience.map((exp, idx) => (
                  <div key={idx} className="space-y-2">
                    <h4 className="font-bold">{exp.title} at {exp.company}</h4>
                    <p className="text-sm opacity-80">{exp.dates}{exp.location ? ` • ${exp.location}` : ''}</p>
                    {exp.details && exp.details.length > 0 && (
                      <ul className="list-disc pl-5 space-y-1">
                        {exp.details.slice(0, 3).map((detail, detailIdx) => (
                          <li key={detailIdx}>{detail}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            </GlassCard>
          )}
        </>
      )}
    </div>
  );
};

export default ResultDisplay; 