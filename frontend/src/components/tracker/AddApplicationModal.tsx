import { useState } from 'react';
import { useApplications } from '../../hooks/useApplications';
import Modal from '../shared/Modal';
import Input from '../shared/Input';
import Button from '../shared/Button';
import toast from 'react-hot-toast';

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export default function AddApplicationModal({ isOpen, onClose }: Props) {
  const { createMutation } = useApplications();
  const [company, setCompany] = useState('');
  const [role, setRole] = useState('');
  const [notes, setNotes] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!company || !role) return toast.error('Company and role are required');
    createMutation.mutate(
      { company, role_title: role, notes },
      {
        onSuccess: () => {
          toast.success('Application added');
          onClose();
          setCompany('');
          setRole('');
          setNotes('');
        },
      }
    );
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add Application">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input label="Company" value={company} onChange={(e) => setCompany(e.target.value)} required />
        <Input label="Role" value={role} onChange={(e) => setRole(e.target.value)} required />
        <textarea
          placeholder="Notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className="w-full border-gray-300 rounded-md shadow-sm"
          rows={3}
        />
        <div className="flex justify-end gap-2">
          <Button variant="outline" type="button" onClick={onClose}>Cancel</Button>
          <Button type="submit" isLoading={createMutation.isPending}>Add</Button>
        </div>
      </form>
    </Modal>
  );
}