'use client';

import { useState, useEffect } from 'react';
import JobApplicationForm from "@/components/JobApplicationForm";
import ResultDisplay from "@/components/ResultDisplay";
import { customizeResume, getApiBaseUrl } from "@/services/api";
import GlassCard from '@/components/GlassCard';
import { CustomizeResumeResponse } from '@/types';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<CustomizeResumeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isMounted, setIsMounted] = useState(false);

  // Handle client-side only rendering to avoid hydration errors
  useEffect(() => {
    setIsMounted(true);
  }, []);

  const handleSubmit = async (jobDescription: string, resumeFile: File) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await customizeResume(jobDescription, resumeFile);
      setResult(data);
    } catch (err) {
      console.error('Error:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  // Return null during server-side rendering or first client-side render
  // This prevents hydration errors from browser extensions
  if (!isMounted) {
    return null;
  }

  return (
    <div className="min-h-screen p-4 md:p-8">
      <main className="max-w-7xl mx-auto space-y-16 pb-20">
        <section className="mt-10 text-center">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
            AI-Powered Resume Customization
          </h1>
          <p className="text-lg md:text-xl opacity-80 mb-8 max-w-3xl mx-auto">
            Optimize your resume for specific job descriptions using advanced AI. 
            Get personalized suggestions to improve your chances of landing your dream job.
          </p>
        </section>

        {!result ? (
          <section>
            <h2 className="text-2xl font-bold text-center mb-8">Get Started</h2>
            <JobApplicationForm onSubmit={handleSubmit} isLoading={isLoading} />
            
            {error && (
              <GlassCard className="p-6 mt-6 bg-red-500/10 max-w-4xl mx-auto">
                <h3 className="text-xl font-bold mb-2">Error</h3>
                <p>{error}</p>
              </GlassCard>
            )}
          </section>
        ) : (
          <section>
            <ResultDisplay 
              result={result} 
              onReset={handleReset} 
              apiBaseUrl={getApiBaseUrl()} 
            />
          </section>
        )}

        <section id="about" className="py-10 max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-8">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <GlassCard className="p-6 text-center">
              <div className="text-3xl mb-4">📄</div>
              <h3 className="text-xl font-bold mb-2">Upload</h3>
              <p>Upload your resume and paste the job description you&apos;re applying for.</p>
            </GlassCard>
            
            <GlassCard className="p-6 text-center">
              <div className="text-3xl mb-4">🤖</div>
              <h3 className="text-xl font-bold mb-2">Process</h3>
              <p>Our AI analyzes both documents to identify matches and opportunities for improvement.</p>
            </GlassCard>
            
            <GlassCard className="p-6 text-center">
              <div className="text-3xl mb-4">✨</div>
              <h3 className="text-xl font-bold mb-2">Optimize</h3>
              <p>Get a customized resume and talking points to highlight your relevant experience.</p>
            </GlassCard>
          </div>
        </section>
      </main>

      <footer className="glassmorphism mt-10 p-6 text-center max-w-7xl mx-auto">
        <p>© {new Date().getFullYear()} Resume AI. All rights reserved.</p>
      </footer>
    </div>
  );
}
