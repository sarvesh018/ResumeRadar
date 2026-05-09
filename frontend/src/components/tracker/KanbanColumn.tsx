import type { KanbanColumn as KanbanColumnType } from '../../types/index';
import ApplicationCard from '../tracker/ApplicationCard';

interface Props {
  column: KanbanColumnType;
}

export default function KanbanColumn({ column }: Props) {
  return (
    <div className="shrink-0 w-72 bg-gray-50 rounded-lg p-3">
      <h3 className="font-semibold text-sm mb-2 text-gray-700 uppercase tracking-wide">
        {column.status} <span className="text-gray-400 ml-1">({column.count})</span>
      </h3>
      <div className="space-y-2">
        {column.applications.map((app) => (
          <ApplicationCard key={app.id} application={app} />
        ))}
      </div>
    </div>
  );
}