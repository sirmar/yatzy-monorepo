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
    <div className="flex gap-2">
      {options.map(({ label, value }) => (
        <button
          key={value}
          type="button"
          onClick={() => onChange(value)}
          className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
            selected === value ? 'bg-yellow-400 text-gray-900' : 'text-gray-400 hover:text-white'
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
