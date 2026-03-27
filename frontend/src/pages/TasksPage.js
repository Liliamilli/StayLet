import EmptyState from '../components/shared/EmptyState';
import { ListTodo } from 'lucide-react';

export default function TasksPage() {
    return (
        <div data-testid="tasks-page">
            {/* Page header */}
            <div className="mb-8">
                <h1 
                    className="text-2xl font-bold text-slate-900 mb-1"
                    style={{ fontFamily: 'Outfit, sans-serif' }}
                >
                    Tasks
                </h1>
                <p className="text-slate-500">
                    Manage your to-do list and property tasks
                </p>
            </div>

            {/* Empty state */}
            <div className="bg-white rounded-lg border border-slate-200">
                <EmptyState
                    icon={ListTodo}
                    title="No tasks yet"
                    description="Create tasks to track maintenance, inspections, and other property-related activities."
                    actionLabel="Create Task"
                    onAction={() => {}}
                />
            </div>
        </div>
    );
}
