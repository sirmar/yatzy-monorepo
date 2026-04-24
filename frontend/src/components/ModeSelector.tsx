interface Option<T> {
  label: string;
  value: T;
}

interface Props<T> {
  options: Option<T>[];
  selected: T;
  onChange: (value: T) => void;
}

export function ModeSelector<T extends string>({ options, selected, onChange }: Props<T>) {
  return (
    <div className="flex items-center gap-1 bg-[var(--surface-2)] rounded-full p-[3px]">
      {options.map(({ label, value }) => (
        <button
          key={value}
          type="button"
          onClick={() => onChange(value)}
          className={`h-[26px] px-3 rounded-full text-[12px] font-medium cursor-pointer border-none transition-colors ${
            selected === value
              ? 'bg-[var(--accent)] text-white'
              : 'bg-transparent text-[var(--text-muted)] hover:text-foreground'
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
