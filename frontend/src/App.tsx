
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { Toaster } from '@/components/ui/toaster';

// Pages
import Landing from './pages/Landing';
import SignIn from './pages/SignIn';
import SignUp from './pages/SignUp';
import ForgotPassword from './pages/ForgotPassword';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import Profile from './pages/Profile';
import ProgressDashboard from './pages/ProgressDashboard';
import TrainingDashboard from './pages/TrainingDashboard';
import NutritionDashboard from './pages/NutritionDashboard';
import QuickActions from './pages/QuickActions';
import { ChatLayout } from './components/layout/ChatLayout';

// Mock user for development
const mockUser = {
  id: '1',
  email: 'user@example.com',
  name: 'NGX User',
  avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face',
  createdAt: new Date('2024-01-01'),
  subscription: 'pro' as const,
  tokens: 500
};

const App: React.FC = () => {
  const { user, setUser } = useAuthStore();

  // Auto-login for development
  React.useEffect(() => {
    if (!user) {
      setUser(mockUser);
    }
  }, [user, setUser]);

  const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    return user ? <>{children}</> : <Navigate to="/signin" />;
  };

  const PublicRoute = ({ children }: { children: React.ReactNode }) => {
    return !user ? <>{children}</> : <Navigate to="/dashboard" />;
  };

  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/signin" element={
            <PublicRoute>
              <SignIn />
            </PublicRoute>
          } />
          <Route path="/signup" element={
            <PublicRoute>
              <SignUp />
            </PublicRoute>
          } />
          <Route path="/forgot-password" element={
            <PublicRoute>
              <ForgotPassword />
            </PublicRoute>
          } />

          {/* Protected Routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          
          <Route path="/dashboard/progress" element={
            <ProtectedRoute>
              <ProgressDashboard />
            </ProtectedRoute>
          } />
          
          <Route path="/dashboard/training" element={
            <ProtectedRoute>
              <TrainingDashboard />
            </ProtectedRoute>
          } />
          
          <Route path="/dashboard/nutrition" element={
            <ProtectedRoute>
              <NutritionDashboard />
            </ProtectedRoute>
          } />
          
          <Route path="/quick-actions" element={
            <ProtectedRoute>
              <QuickActions />
            </ProtectedRoute>
          } />
          
          <Route path="/settings" element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          } />

          <Route path="/profile" element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } />

          {/* Chat Routes */}
          <Route path="/chat" element={
            <ProtectedRoute>
              <ChatLayout />
            </ProtectedRoute>
          } />
          
          <Route path="/chat/:agentId" element={
            <ProtectedRoute>
              <ChatLayout />
            </ProtectedRoute>
          } />
        </Routes>
        <Toaster />
      </div>
    </Router>
  );
};

export default App;
