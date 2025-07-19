import { useLocation } from "react-router-dom";
import { useEffect } from "react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-black grok-gradient relative overflow-hidden flex items-center justify-center">
      {/* Floating orbs */}
      <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-violet-700/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      
      <div className="text-center relative z-10">
        <h1 className="text-6xl font-bold mb-4 text-white">404</h1>
        <p className="text-xl text-white/60 mb-8">Oops! Page not found</p>
        <a href="/" className="text-purple-400 hover:text-purple-300 underline text-lg transition-colors">
          Return to Home
        </a>
      </div>
    </div>
  );
};

export default NotFound;
