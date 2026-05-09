import type { KanbanColumn as KanbanColumnType } from '../../types/index';
import KanbanColumnComponent from '../tracker/KanbanColumn';

interface Props {
  columns: KanbanColumnType[];
}

export default function KanbanBoard({ columns }: Props) {
  return (
    <div className="flex gap-4 overflow-x-auto pb-4">
      {columns.map((col) => (
        <KanbanColumnComponent key={col.status} column={col} />
      ))}
    </div>
  );
}