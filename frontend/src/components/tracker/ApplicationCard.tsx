import type { Application } from '../../types/index';
import { useState } from 'react';
import { useApplications } from '../../hooks/useApplications';
import toast from 'react-hot-toast';

interface Props {
  application: Application;
}

export default function ApplicationCard({ application }: Props) {
  const { updateStatusMutation } = useApplications();
  const [showDropdown, setShowDropdown] = useState(false);

  const handleStatusChange = (newStatus: string) => {
    updateStatusMutation.mutate(
      { id: application.id, status: newStatus },
      { onSuccess: () => toast.success(`Moved to ${newStatus}`) }
    );
    setShowDropdown(false);
  };

  return (
    <div className="bg-white p-3 rounded shadow-sm border border-gray-200">
      <div className="flex justify-between items-start">
        <div>
          <p className="font-medium text-sm">{application.role_title}</p>
          <p className="text-xs text-gray-500">{application.company}</p>
        </div>
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          className="text-xs bg-gray-100 px-2 py-1 rounded"
        >
          {application.status}
        </button>
      </div>
      {showDropdown && (
        <div className="mt-2 space-y-1">
          {application.allowed_transitions.map(status => (
            <button
              key={status}
              onClick={() => handleStatusChange(status)}
              className="block w-full text-left text-xs px-2 py-1 hover:bg-indigo-50 rounded"
            >
              Move to {status}
            </button>
          ))}
        </div>
      )}
      {application.match_score && (
        <div className="mt-1 text-xs text-gray-400">Match: {(application.match_score*100).toFixed(0)}%</div>
      )}
    </div>
  );
}