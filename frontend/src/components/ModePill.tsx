const MODE_LABELS: Record<string, string> = {
  maxi: 'Maxi Yatzy',
  maxi_sequential: 'Maxi Sequential',
  yatzy: 'Yatzy',
  yatzy_sequential: 'Yatzy Sequential',
};

export function ModePill({ mode }: { mode: string }) {
  return (
    <span className="text-[10px] font-semibold uppercase tracking-[0.06em] border border-[rgba(124,158,248,0.35)] bg-[var(--accent-dim)] text-[var(--accent)] rounded-full px-[7px] py-[2px]">
      {MODE_LABELS[mode] ?? mode}
    </span>
  );
}
