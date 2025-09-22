/**
 * Main App component with routing and authentication provider.
 */

import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import LoginPage from '@/pages/LoginPage';
import SignupPage from '@/pages/SignupPage';
import Button from '@/components/Button';
import TaskList from '@/components/TaskList';
import AddTaskCard from '@/components/AddTaskCard';
import AISummaryModal from '@/components/AISummaryModal';
import { Task, CreateTaskData } from '@/types/task';
import { taskService } from '@/services/taskService';

// Dashboard component with task management
const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isAddTaskModalOpen, setIsAddTaskModalOpen] = useState(false);
  const [isAISummaryModalOpen, setIsAISummaryModalOpen] = useState(false);
  const [aiSummary, setAiSummary] = useState('');
  const [isSummaryLoading, setIsSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  const handleAddTask = async (taskData: CreateTaskData) => {
    // Generate a unique ID for the task
    const newTask: Task = {
      id: crypto.randomUUID(),
      title: taskData.title,
      description: taskData.description,
      priority: taskData.priority,
      status: 'TODO',
      createdAt: new Date(),
      updatedAt: new Date(),
      dueDate: taskData.dueDate,
    };

    setTasks(prevTasks => [...prevTasks, newTask]);
  };

  const handleTaskUpdate = (taskId: string, updates: Partial<Task>) => {
    setTasks(prevTasks => 
      prevTasks.map(task => 
        task.id === taskId ? { ...task, ...updates } : task
      )
    );
  };

  const handleAISummary = async () => {
    setIsSummaryLoading(true);
    setSummaryError(null);
    setAiSummary('');
    setIsAISummaryModalOpen(true);

    try {
      // Filter only incomplete tasks (TODO and IN_PROGRESS)
      const incompleteTasks = tasks.filter(task => 
        task.status === 'TODO' || task.status === 'IN_PROGRESS'
      );
      
      if (incompleteTasks.length === 0) {
        setAiSummary('No incomplete tasks to summarize. All tasks are either completed or cancelled.');
        return;
      }

      // First, try to fetch tasks from API (if available)
      // For now, we'll use the filtered local tasks state
      // In production, you would fetch from API: const apiTasks = await taskService.getTasks();
      const summary = await taskService.getAISummary(incompleteTasks);
      setAiSummary(summary);
    } catch (error: any) {
      console.error('Error generating AI summary:', error);
      setSummaryError(
        error.message || 
        'Failed to generate AI summary. Please try again later.'
      );
    } finally {
      setIsSummaryLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-xl font-bold text-gray-900">TaskPilot Dashboard</h1>
            <div className="flex items-center space-x-4">
              <span className="text-gray-600">Welcome, {user?.username}!</span>
              <button
                onClick={logout}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header with buttons */}
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">My Tasks</h2>
              <p className="text-gray-600 mt-1">
                Manage your tasks and stay organized
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <Button
                onClick={handleAISummary}
                variant="outline"
                className="flex items-center space-x-2"
                disabled={tasks.filter(t => t.status === 'TODO' || t.status === 'IN_PROGRESS').length === 0}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                <span>Summarise with AI</span>
              </Button>
              <Button
                onClick={() => setIsAddTaskModalOpen(true)}
                className="flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                <span>Add Task</span>
              </Button>
            </div>
          </div>

          {/* Task List */}
          <TaskList tasks={tasks} onTaskUpdate={handleTaskUpdate} />

          {/* Add Task Modal */}
          <AddTaskCard
            isOpen={isAddTaskModalOpen}
            onClose={() => setIsAddTaskModalOpen(false)}
            onSubmit={handleAddTask}
          />

          {/* AI Summary Modal */}
          <AISummaryModal
            isOpen={isAISummaryModalOpen}
            onClose={() => setIsAISummaryModalOpen(false)}
            summary={aiSummary}
            isLoading={isSummaryLoading}
            error={summaryError}
          />
        </div>
      </main>
    </div>
  );
};

// Protected Route component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }
  
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

// Public Route component (redirect to dashboard if already authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }
  
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <>{children}</>;
};

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={
        <PublicRoute>
          <LoginPage />
        </PublicRoute>
      } />
      <Route path="/signup" element={
        <PublicRoute>
          <SignupPage />
        </PublicRoute>
      } />
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      } />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
};

export default App;

