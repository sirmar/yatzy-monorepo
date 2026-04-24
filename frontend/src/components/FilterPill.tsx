interface Props {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}

export function FilterPill({ active, onClick, children }: Props) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        'text-[11px] font-semibold px-2.5 py-1 rounded-full border cursor-pointer transition-colors',
        active
          ? 'bg-[var(--accent-dim)] border-[var(--accent)] text-[var(--accent)]'
          : 'bg-transparent border-[var(--border-2)] text-[var(--text-muted)] hover:text-foreground hover:border-white/20',
      ].join(' ')}
    >
      {children}
    </button>
  );
}
