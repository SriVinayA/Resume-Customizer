import React, { ReactNode } from 'react';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
}

const GlassCard: React.FC<GlassCardProps> = ({ children, className = '' }) => {
  return (
    <div className={`glassmorphism-card ${className}`} suppressHydrationWarning>
      {children}
    </div>
  );
};

export default GlassCard; 