export function PageLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-[860px] mx-auto px-4 pt-1 pb-16 flex flex-col gap-4">{children}</div>
    </div>
  );
}
