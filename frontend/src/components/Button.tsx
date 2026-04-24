interface Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost' | 'danger';
  size?: 'md' | 'sm';
}

const base = 'cursor-pointer border-none transition-all font-semibold';

const variants = {
  primary:
    'bg-[var(--accent)] text-white hover:scale-[1.03] hover:shadow-[0_0_18px_rgba(124,158,248,0.35)] active:scale-[0.97] disabled:opacity-50 disabled:cursor-not-allowed',
  ghost:
    'bg-transparent border border-[var(--border-2)] text-[var(--text-muted)] font-medium hover:bg-[var(--surface-2)] hover:text-foreground hover:border-white/20',
  danger:
    'bg-transparent border border-[var(--border-2)] text-[var(--text-muted)] font-medium hover:bg-[rgba(240,101,96,0.08)] hover:text-[var(--red)] hover:border-transparent',
};

const sizes = {
  md: 'h-9 px-4 rounded-lg text-[13px]',
  sm: 'h-8 px-3 rounded-lg text-[12px]',
};

export function Button({ variant = 'primary', size = 'md', className, ...props }: Props) {
  return (
    <button
      className={`${base} ${variants[variant]} ${sizes[size]} ${className ?? ''}`}
      {...props}
    />
  );
}
