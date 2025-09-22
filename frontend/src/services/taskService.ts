/**
 * Task service for API calls to the backend
 */

import axios from 'axios';
import { Task, CreateTaskData, UpdateTaskData } from '@/types/task';

const API_BASE_URL = '/api/v1';

const taskApi = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests if available
taskApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const taskService = {
  // Get all tasks for the current user
  getTasks: async (): Promise<Task[]> => {
    const response = await taskApi.get('/tasks');
    return response.data.map((task: any) => ({
      ...task,
      createdAt: new Date(task.createdAt),
      updatedAt: new Date(task.updatedAt),
      dueDate: task.dueDate ? new Date(task.dueDate) : undefined,
    }));
  },

  // Create a new task
  createTask: async (taskData: CreateTaskData): Promise<Task> => {
    const response = await taskApi.post('/tasks', taskData);
    return {
      ...response.data,
      createdAt: new Date(response.data.createdAt),
      updatedAt: new Date(response.data.updatedAt),
      dueDate: response.data.dueDate ? new Date(response.data.dueDate) : undefined,
    };
  },

  // Update a task
  updateTask: async (taskId: string, updates: UpdateTaskData): Promise<Task> => {
    const response = await taskApi.put(`/tasks/${taskId}`, updates);
    return {
      ...response.data,
      createdAt: new Date(response.data.createdAt),
      updatedAt: new Date(response.data.updatedAt),
      dueDate: response.data.dueDate ? new Date(response.data.dueDate) : undefined,
    };
  },

  // Delete a task
  deleteTask: async (taskId: string): Promise<void> => {
    await taskApi.delete(`/tasks/${taskId}`);
  },

  // Get AI summary of active tasks
  getAISummary: async (tasks: Task[]): Promise<string> => {
    // Filter tasks to only include TODO and IN_PROGRESS
    const activeTasks = tasks.filter(
      task => task.status === 'TODO' || task.status === 'IN_PROGRESS'
    );

    if (activeTasks.length === 0) {
      throw new Error('No active tasks to summarize');
    }

    // Prepare task data for AI summarization
    const taskData = activeTasks.map(task => ({
      title: task.title,
      description: task.description || '',
      priority: task.priority,
      status: task.status,
      dueDate: task.dueDate,
    }));

    const response = await taskApi.post('/ai/summarize-tasks', taskData);

    return response.data.summary;
  },
};

export default taskService;

