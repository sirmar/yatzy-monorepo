interface Props extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  hint?: string;
  inputClassName?: string;
}

export function FormField({ label, hint, inputClassName, id, ...inputProps }: Props) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-[12px] font-medium text-[var(--text-muted)]">
        {label}
      </label>
      <input
        id={id}
        className={
          inputClassName ??
          'h-9 bg-[var(--surface-2)] border border-[var(--border-2)] rounded-lg px-2.5 text-[13px] text-foreground outline-none transition-colors focus:border-[var(--accent)]'
        }
        {...inputProps}
      />
      {hint && <div className="text-[11px] text-[var(--text-dim)]">{hint}</div>}
    </div>
  );
}
