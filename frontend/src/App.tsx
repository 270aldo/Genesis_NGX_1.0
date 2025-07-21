
import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { Toaster } from '@/components/ui/toaster';
import { PageLoader } from '@/components/ui/page-loader';
import { lazyWithPreload } from '@/utils/lazyWithPreload';
import { LazyBoundary } from '@/components/ui/lazy-loading';
import { ChunkProvider } from '@/components/providers/ChunkProvider';

// Lazy loaded pages with preload support
const Landing = lazyWithPreload(() => import('./pages/Landing'));
const SignIn = lazyWithPreload(() => import('./pages/SignIn'));
const SignUp = lazyWithPreload(() => import('./pages/SignUp'));
const ForgotPassword = lazyWithPreload(() => import('./pages/ForgotPassword'));
const Dashboard = lazyWithPreload(() => import('./pages/Dashboard'));
const Settings = lazyWithPreload(() => import('./pages/Settings'));
const Profile = lazyWithPreload(() => import('./pages/Profile'));
const ProgressDashboard = lazyWithPreload(() => import('./pages/ProgressDashboard'));
const TrainingDashboard = lazyWithPreload(() => import('./pages/TrainingDashboard'));
const NutritionDashboard = lazyWithPreload(() => import('./pages/NutritionDashboard'));
const QuickActions = lazyWithPreload(() => import('./pages/QuickActions'));
const ChatLayout = lazyWithPreload(() => import('./components/layout/ChatLayout').then(module => ({ default: module.ChatLayout })));

// Preload critical routes on idle
if ('requestIdleCallback' in window) {
  requestIdleCallback(() => {
    Dashboard.preload();
    ChatLayout.preload();
  });
}

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
      <ChunkProvider>
        <div className="App">
          <LazyBoundary fallback={<PageLoader />}>
            <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Landing.Component />} />
          <Route path="/signin" element={
            <PublicRoute>
              <SignIn.Component />
            </PublicRoute>
          } />
          <Route path="/signup" element={
            <PublicRoute>
              <SignUp.Component />
            </PublicRoute>
          } />
          <Route path="/forgot-password" element={
            <PublicRoute>
              <ForgotPassword.Component />
            </PublicRoute>
          } />

          {/* Protected Routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard.Component />
            </ProtectedRoute>
          } />
          
          <Route path="/dashboard/progress" element={
            <ProtectedRoute>
              <ProgressDashboard.Component />
            </ProtectedRoute>
          } />
          
          <Route path="/dashboard/training" element={
            <ProtectedRoute>
              <TrainingDashboard.Component />
            </ProtectedRoute>
          } />
          
          <Route path="/dashboard/nutrition" element={
            <ProtectedRoute>
              <NutritionDashboard.Component />
            </ProtectedRoute>
          } />
          
          <Route path="/quick-actions" element={
            <ProtectedRoute>
              <QuickActions.Component />
            </ProtectedRoute>
          } />
          
          <Route path="/settings" element={
            <ProtectedRoute>
              <Settings.Component />
            </ProtectedRoute>
          } />

          <Route path="/profile" element={
            <ProtectedRoute>
              <Profile.Component />
            </ProtectedRoute>
          } />

          {/* Chat Routes */}
          <Route path="/chat" element={
            <ProtectedRoute>
              <ChatLayout.Component />
            </ProtectedRoute>
          } />
          
          <Route path="/chat/:agentId" element={
            <ProtectedRoute>
              <ChatLayout.Component />
            </ProtectedRoute>
          } />
        </Routes>
          </LazyBoundary>
          <Toaster />
        </div>
      </ChunkProvider>
    </Router>
  );
};

export default App;
