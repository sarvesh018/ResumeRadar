interface Props {
  message: string;
}

export default function EmptyState({ message }: Props) {
  return <div className="text-center text-gray-500 py-8">{message}</div>;
}