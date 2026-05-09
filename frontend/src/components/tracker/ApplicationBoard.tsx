import { useState } from 'react';
import { useApplications } from '../../hooks/useApplications';
import KanbanBoard from '../../components/tracker/KanbanBoard';
import AddApplicationModal from '../../components/tracker/AddApplicationModal';
import Button from '../../components/shared/Button';
import { Plus } from 'lucide-react';

export default function ApplicationBoard() {
  const { kanbanQuery } = useApplications();
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data, isLoading, error } = kanbanQuery;

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Applications</h1>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus size={18} className="mr-1" /> Add Application
        </Button>
      </div>

      {isLoading && <div className="text-center py-8">Loading board...</div>}
      {error && (
        <div className="text-center py-8 text-red-500">
          Failed to load the board. Please try again.
        </div>
      )}
      {data && !isLoading && !error && <KanbanBoard columns={data.columns} />}
      {data && data.total === 0 && !isLoading && !error && (
        <div className="text-center py-8 text-gray-500">
          No applications yet. Click "Add Application" to get started.
        </div>
      )}

      <AddApplicationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}