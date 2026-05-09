import { useState } from 'react';
import { useApplications } from '../hooks/useApplications';
import KanbanBoard from '../components/tracker/KanbanBoard';
import AddApplicationModal from '../components/tracker/AddApplicationModal';
import Button from '../components/shared/Button';
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
      {isLoading && <div>Loading...</div>}
      {error && <div className="text-red-500">Failed to load board</div>}
      {data && <KanbanBoard columns={data.columns} />}

      <AddApplicationModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}