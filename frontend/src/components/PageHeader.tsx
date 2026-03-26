interface PageHeaderProps {
  title: React.ReactNode;
  action?: React.ReactNode;
}

export function PageHeader({ title, action }: PageHeaderProps) {
  return (
    <div className="flex items-center justify-between">
      <h1 className="text-2xl font-bold text-white">{title}</h1>
      {action}
    </div>
  );
}
