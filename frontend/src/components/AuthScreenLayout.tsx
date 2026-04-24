interface Props {
  children: React.ReactNode;
}

export function AuthScreenLayout({ children }: Props) {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4 py-6">
      <div className="w-full max-w-sm">
        <h1 className="text-2xl font-bold text-center text-foreground mb-5">Yatzy</h1>
        <div className="rounded-[14px] border border-[var(--border)] bg-card overflow-hidden">
          {children}
        </div>
      </div>
    </div>
  );
}
