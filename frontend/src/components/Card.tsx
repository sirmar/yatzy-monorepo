interface Props extends React.HTMLAttributes<HTMLDivElement> {}

export function Card({ className, ...props }: Props) {
  return (
    <div
      className={`bg-[var(--surface)] border border-[var(--border)] rounded-[14px] ${className ?? ''}`}
      {...props}
    />
  );
}
