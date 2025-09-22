/**
 * TaskList component - displays tasks in a list format.
 */

import React, { useState } from 'react';
import { Task, TaskPriority, TaskStatus } from '@/types/task';
import ConfirmationModal from '@/components/ConfirmationModal';

interface TaskListProps {
  tasks: Task[];
  onTaskUpdate?: (taskId: string, updates: Partial<Task>) => void;
}

const TaskList: React.FC<TaskListProps> = ({ tasks, onTaskUpdate }) => {
  const [confirmModal, setConfirmModal] = useState<{
    isOpen: boolean;
    taskId: string;
    newStatus: TaskStatus;
  }>({ isOpen: false, taskId: '', newStatus: 'TODO' });

  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-green-100 text-green-800';
      case 'IN_PROGRESS':
        return 'bg-blue-100 text-blue-800';
      case 'CANCELLED':
        return 'bg-red-100 text-red-800';
      case 'TODO':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusDisplayText = (status: TaskStatus) => {
    switch (status) {
      case 'TODO':
        return 'To Do';
      case 'IN_PROGRESS':
        return 'In Progress';
      case 'COMPLETED':
        return 'Completed';
      case 'CANCELLED':
        return 'Cancelled';
      default:
        return status;
    }
  };

  const handleStatusChange = (taskId: string, newStatus: TaskStatus) => {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;

    // Prevent changing from CANCELLED status
    if (task.status === 'CANCELLED') {
      return;
    }

    // Show confirmation for CANCELLED status
    if (newStatus === 'CANCELLED') {
      setConfirmModal({ isOpen: true, taskId, newStatus });
      return;
    }

    // Update task status directly for other statuses
    onTaskUpdate?.(taskId, { status: newStatus, updatedAt: new Date() });
  };

  const handleConfirmStatusChange = () => {
    onTaskUpdate?.(confirmModal.taskId, { 
      status: confirmModal.newStatus, 
      updatedAt: new Date() 
    });
    setConfirmModal({ isOpen: false, taskId: '', newStatus: 'TODO' });
  };

  const getAvailableStatuses = (currentStatus: TaskStatus): TaskStatus[] => {
    // CANCELLED is final state - no changes allowed
    if (currentStatus === 'CANCELLED') {
      return [currentStatus];
    }
    
    // All other statuses can transition to any status
    return ['TODO', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'];
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(date);
  };

  if (tasks.length === 0) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No tasks yet</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating your first task.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Your Tasks</h3>
        <div className="space-y-4">
          {tasks.map((task) => (
            <div
              key={task.id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-gray-900 truncate">
                    {task.title}
                  </h4>
                  {task.description && (
                    <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                      {task.description}
                    </p>
                  )}
                  <div className="mt-2 flex items-center space-x-2">
                    <select
                      value={task.status}
                      onChange={(e) => handleStatusChange(task.id, e.target.value as TaskStatus)}
                      disabled={task.status === 'CANCELLED'}
                      className={`text-xs font-medium px-2.5 py-0.5 rounded-full border-0 focus:ring-2 focus:ring-primary-500 ${getStatusColor(task.status)} ${task.status === 'CANCELLED' ? 'cursor-not-allowed opacity-75' : 'cursor-pointer'}`}
                    >
                      {getAvailableStatuses(task.status).map((status) => (
                        <option key={status} value={status}>
                          {getStatusDisplayText(status)}
                        </option>
                      ))}
                    </select>
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(
                        task.priority
                      )}`}
                    >
                      {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)} Priority
                    </span>
                  </div>
                  <div className="mt-2 flex items-center text-xs text-gray-500 space-x-4">
                    <span>Created {formatDate(task.createdAt)}</span>
                    {task.dueDate && (
                      <span className="flex items-center">
                        <svg className="mr-1 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        Due {formatDate(task.dueDate)}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                    title="Edit task"
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    className="text-gray-400 hover:text-red-600 transition-colors"
                    title="Delete task"
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Confirmation Modal */}
      <ConfirmationModal
        isOpen={confirmModal.isOpen}
        onClose={() => setConfirmModal({ isOpen: false, taskId: '', newStatus: 'TODO' })}
        onConfirm={handleConfirmStatusChange}
        title="Cancel Task"
        message="Are you sure you want to cancel this task? This action cannot be undone."
        confirmText="Yes, Cancel Task"
        cancelText="No, Keep Task"
        isDestructive={true}
      />
    </div>
  );
};

export default TaskList;

