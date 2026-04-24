interface Props {
  error?: string | null;
}

export function ErrorMessage({ error }: Props) {
  if (!error) return null;
  return <p className="text-[12px] text-[var(--red)]">{error}</p>;
}
