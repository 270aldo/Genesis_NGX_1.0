
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Menu, X } from 'lucide-react';

export const LandingHeader: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="absolute top-0 left-0 right-0 z-50 p-4 sm:p-6">
      <nav className="container mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <span className="text-white font-bold text-sm">N</span>
          </div>
          <span className="text-white font-semibold text-lg sm:text-xl">NGX Agents</span>
        </div>
        
        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center space-x-8">
          <a href="#features" className="text-white/70 hover:text-white transition-colors">
            Features
          </a>
          <a href="#demo" className="text-white/70 hover:text-white transition-colors">
            Demo
          </a>
          <Link to="/sign-in" className="text-white/70 hover:text-white transition-colors">
            Sign In
          </Link>
          <Link to="/sign-up">
            <Button 
              variant="outline" 
              className="glass-premium border-white/20 text-white hover:bg-white/10"
            >
              Get Started
            </Button>
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden text-white hover:bg-white/10"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </Button>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="absolute top-full left-0 right-0 mt-2 mx-4 bg-black/90 backdrop-blur-lg rounded-lg border border-white/10 p-4 md:hidden">
            <div className="flex flex-col space-y-4">
              <a 
                href="#features" 
                className="text-white/70 hover:text-white transition-colors py-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                Features
              </a>
              <a 
                href="#demo" 
                className="text-white/70 hover:text-white transition-colors py-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                Demo
              </a>
              <Link 
                to="/sign-in" 
                className="text-white/70 hover:text-white transition-colors py-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                Sign In
              </Link>
              <Link to="/sign-up" onClick={() => setMobileMenuOpen(false)}>
                <Button 
                  variant="outline" 
                  className="glass-premium border-white/20 text-white hover:bg-white/10 w-full"
                >
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
};
