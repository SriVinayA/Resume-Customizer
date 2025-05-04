import React, { ButtonHTMLAttributes } from 'react';

interface GlassButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
  className?: string;
}

const GlassButton: React.FC<GlassButtonProps> = ({ 
  children, 
  variant = 'primary', 
  className = '',
  ...props 
}) => {
  const baseClasses = 'glassmorphism px-6 py-2 font-medium transition-all duration-300 focus:outline-none';
  
  const variantClasses = {
    primary: 'bg-white/20 hover:bg-white/30',
    secondary: 'bg-black/10 hover:bg-black/20 text-white',
  };

  return (
    <button 
      className={`${baseClasses} ${variantClasses[variant]} ${className}`} 
      {...props}
    >
      {children}
    </button>
  );
};

export default GlassButton; 