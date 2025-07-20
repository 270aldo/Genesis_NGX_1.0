
import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { Toaster } from '@/components/ui/toaster';
import { PageLoader } from '@/components/ui/page-loader';

// Lazy loaded pages
const Landing = React.lazy(() => import('./pages/Landing'));
const SignIn = React.lazy(() => import('./pages/SignIn'));
const SignUp = React.lazy(() => import('./pages/SignUp'));
const ForgotPassword = React.lazy(() => import('./pages/ForgotPassword'));
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Settings = React.lazy(() => import('./pages/Settings'));
const Profile = React.lazy(() => import('./pages/Profile'));
const ProgressDashboard = React.lazy(() => import('./pages/ProgressDashboard'));
const TrainingDashboard = React.lazy(() => import('./pages/TrainingDashboard'));
const NutritionDashboard = React.lazy(() => import('./pages/NutritionDashboard'));
const QuickActions = React.lazy(() => import('./pages/QuickActions'));
const ChatLayout = React.lazy(() => import('./components/layout/ChatLayout').then(module => ({ default: module.ChatLayout })));

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
        <Suspense fallback={<PageLoader />}>
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
        </Suspense>
        <Toaster />
      </div>
    </Router>
  );
};

export default App;
