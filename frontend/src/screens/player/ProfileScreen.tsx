import { Pencil } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { apiClient } from '@/api';
import type { components } from '@/api/schema';
import { Card } from '@/components/Card';
import { PageLayout } from '@/components/PageLayout';
import { PicturePicker } from '@/components/PicturePicker';
import { useAuth } from '@/hooks/AuthContext';
import { usePlayer } from '@/hooks/PlayerContext';
import { useFormSubmit } from '@/hooks/useFormSubmit';
import { formatDate } from '@/lib/format';
import { cn } from '@/lib/utils';
import { ChangePasswordForm } from './ChangePasswordForm';
import { DeleteAccountSection } from './DeleteAccountSection';

type Player = components['schemas']['Player'];
type PlayerStats = components['schemas']['PlayerStats'];
type ModeStats = components['schemas']['ModeStats'];

const MODE_LABELS: Record<string, string> = {
  maxi: 'Maxi Yatzy',
  maxi_sequential: 'Maxi Sequential',
  yatzy: 'Yatzy',
  yatzy_sequential: 'Yatzy Sequential',
};

const MODE_KEYS = ['maxi', 'maxi_sequential', 'yatzy', 'yatzy_sequential'] as const;

function useClickOutside(ref: React.RefObject<HTMLElement | null>, handler: () => void) {
  useEffect(() => {
    function listener(e: MouseEvent) {
      if (!ref.current || ref.current.contains(e.target as Node)) return;
      handler();
    }
    document.addEventListener('mousedown', listener);
    return () => document.removeEventListener('mousedown', listener);
  }, [ref, handler]);
}

function IdentityPanel({
  player,
  memberSince,
  onSaveName,
  onPlayerUpdated,
}: {
  player: Player;
  memberSince: string;
  onSaveName: (name: string) => Promise<void>;
  onPlayerUpdated: (updated: Player) => void;
}) {
  const [open, setOpen] = useState(false);
  const [editName, setEditName] = useState(player.name);
  const [saving, setSaving] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useClickOutside(ref, () => setOpen(false));

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!editName.trim() || editName.trim() === player.name) {
      setOpen(false);
      return;
    }
    setSaving(true);
    try {
      await onSaveName(editName.trim());
    } finally {
      setSaving(false);
      setOpen(false);
    }
  }

  return (
    <Card className="flex items-center gap-4 h-[78px] px-4">
      <PicturePicker
        player={player}
        size="md"
        className="w-11 h-11 text-[17px] border-2 border-[rgba(124,158,248,0.4)]"
        onSuccess={onPlayerUpdated}
      />
      <div className="flex flex-col gap-[3px] flex-1 min-w-0">
        <div className="text-[17px] font-bold text-foreground truncate">{player.name}</div>
        <div className="text-[12px] text-[var(--text-muted)]">
          Member since {formatDate(memberSince)}
        </div>
      </div>
      <div ref={ref} className="relative flex-shrink-0">
        <button
          type="button"
          onClick={() => {
            setEditName(player.name);
            setOpen((v) => !v);
          }}
          className="flex items-center gap-1.5 h-[30px] px-3 bg-[var(--surface-2)] border border-[var(--border-2)] rounded-lg text-[12px] font-medium text-[var(--text-muted)] cursor-pointer transition-colors hover:text-foreground hover:border-white/20"
        >
          <Pencil aria-hidden="true" width="12" height="12" />
          Edit
        </button>
        {open && (
          <form
            onSubmit={handleSave}
            className="absolute top-[calc(100%+6px)] right-0 w-60 flex flex-col gap-2.5 p-3.5 bg-[var(--surface-2)] border border-[var(--border-2)] rounded-[12px] shadow-[0_8px_32px_rgba(0,0,0,0.4)] z-10"
          >
            <div className="flex flex-col gap-1">
              <label
                htmlFor="edit-display-name"
                className="text-[11px] font-medium text-[var(--text-muted)]"
              >
                Display name
              </label>
              <input
                id="edit-display-name"
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                maxLength={32}
                className="h-8 bg-[var(--surface)] border border-[var(--border-2)] rounded-lg px-2.5 text-[13px] text-foreground outline-none transition-colors focus:border-[var(--accent)]"
              />
            </div>
            <button
              type="submit"
              disabled={saving}
              className="h-8 bg-[var(--accent)] text-white border-none rounded-lg text-[12px] font-semibold cursor-pointer transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
            >
              Save
            </button>
          </form>
        )}
      </div>
    </Card>
  );
}

function StatsGrid({ stats }: { stats: PlayerStats }) {
  const totals = MODE_KEYS.reduce(
    (acc, k) => {
      const m = stats[k] as ModeStats;
      acc.games += m.games_played;
      if (m.high_score != null && m.high_score > acc.best) acc.best = m.high_score;
      if (m.average_score != null) {
        acc.avgSum += m.average_score * m.games_played;
        acc.avgCount += m.games_played;
      }
      return acc;
    },
    { games: 0, best: 0, avgSum: 0, avgCount: 0 }
  );

  const avg = totals.avgCount > 0 ? Math.round(totals.avgSum / totals.avgCount) : null;

  return (
    <div>
      <div
        className="grid gap-px bg-[var(--border)] rounded-[10px] overflow-hidden mb-3"
        style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}
      >
        {[
          { label: 'Games', val: totals.games, sub: 'all time' },
          { label: 'Best score', val: totals.best || '—', sub: 'all modes' },
          { label: 'Avg score', val: avg ?? '—', sub: 'all modes' },
          {
            label: 'Bonuses',
            val: MODE_KEYS.reduce((s, k) => s + (stats[k] as ModeStats).bonus_count, 0),
            sub: 'all time',
          },
        ].map(({ label, val, sub }) => (
          <div key={label} className="bg-[var(--surface-2)] p-3 flex flex-col gap-1">
            <div className="text-[10px] font-bold uppercase tracking-[0.08em] text-[var(--text-dim)]">
              {label}
            </div>
            <div className="text-[20px] font-bold text-foreground leading-none">{val}</div>
            <div className="text-[11px] text-[var(--text-muted)]">{sub}</div>
          </div>
        ))}
      </div>

      <table className="w-full border-collapse">
        <thead>
          <tr>
            {['Mode', 'Games', 'Best', 'Avg'].map((h, i) => (
              <th
                key={h}
                className={cn(
                  'text-[10px] font-bold uppercase tracking-[0.08em] text-[var(--text-dim)] pb-[7px] px-2',
                  i === 0 ? 'text-left' : 'text-right'
                )}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {MODE_KEYS.map((k) => {
            const m = stats[k] as ModeStats;
            return (
              <tr key={k}>
                <td className="text-[12px] font-medium text-foreground py-[7px] px-2 border-t border-[var(--border)]">
                  {MODE_LABELS[k]}
                </td>
                <td className="text-[12px] font-medium text-[var(--text-muted)] py-[7px] px-2 text-right border-t border-[var(--border)]">
                  {m.games_played}
                </td>
                <td className="text-[12px] font-medium text-[var(--green)] py-[7px] px-2 text-right border-t border-[var(--border)]">
                  {m.high_score ?? '—'}
                </td>
                <td className="text-[12px] font-medium text-[var(--text-muted)] py-[7px] px-2 text-right border-t border-[var(--border)]">
                  {m.average_score != null ? Math.round(m.average_score) : '—'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function AccountPanel({ email }: { email: string }) {
  const [openSection, setOpenSection] = useState<'password' | 'delete' | null>(null);

  function toggle(section: 'password' | 'delete') {
    setOpenSection((v) => (v === section ? null : section));
  }

  return (
    <Card className="px-4 py-3">
      <div className="text-[11px] font-bold uppercase tracking-[0.08em] text-[var(--text-dim)] mb-1">
        Account
      </div>

      <div className="flex items-center justify-between gap-4 py-2.5 border-b border-[var(--border)]">
        <div className="flex flex-col gap-0.5">
          <div className="text-[12px] font-semibold text-foreground">Email</div>
          <div className="text-[12px] text-[var(--text-muted)]">{email}</div>
        </div>
      </div>

      <div className="border-b border-[var(--border)]">
        <div className="flex items-center justify-between gap-4 py-2.5">
          <div className="flex flex-col gap-0.5">
            <div className="text-[12px] font-semibold text-foreground">Password</div>
          </div>
          <button
            type="button"
            onClick={() => toggle('password')}
            className="text-[12px] font-medium text-[var(--text-muted)] bg-none border border-[var(--border-2)] rounded-[7px] px-3 py-1 cursor-pointer flex-shrink-0 transition-colors hover:bg-[var(--surface-2)] hover:text-foreground hover:border-white/20"
          >
            Change
          </button>
        </div>
        {openSection === 'password' && (
          <div className="pb-3">
            <ChangePasswordForm onDone={() => setOpenSection(null)} />
          </div>
        )}
      </div>

      <div>
        <div className="flex items-center justify-between gap-4 py-2.5">
          <div className="flex flex-col gap-0.5">
            <div className="text-[12px] font-semibold text-foreground">Delete account</div>
            <div className="text-[12px] text-[var(--text-muted)]">
              Permanently remove your account and all data
            </div>
          </div>
          <button
            type="button"
            onClick={() => toggle('delete')}
            className="text-[12px] font-medium text-[var(--text-muted)] bg-none border border-[var(--border-2)] rounded-[7px] px-3 py-1 cursor-pointer flex-shrink-0 transition-colors hover:bg-[rgba(240,101,96,0.08)] hover:text-[var(--red)] hover:border-transparent"
          >
            Delete
          </button>
        </div>
        {openSection === 'delete' && (
          <div className="pb-3">
            <DeleteAccountSection onCancel={() => setOpenSection(null)} />
          </div>
        )}
      </div>
    </Card>
  );
}

export function ProfileScreen() {
  const { player, setPlayer } = usePlayer();
  const { user } = useAuth();
  const { submit } = useFormSubmit();
  const [stats, setStats] = useState<PlayerStats | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    if (!player) return;
    apiClient
      .GET('/players/{player_id}/stats', {
        params: { path: { player_id: player.id } },
        signal: controller.signal,
      })
      .then(({ data }) => {
        if (data) setStats(data);
      });
    return () => controller.abort();
  }, [player]);

  async function handleSaveName(name: string) {
    if (!player) return;
    await submit(async () => {
      const { data, error } = await apiClient.PUT('/players/{player_id}', {
        params: { path: { player_id: player.id } },
        body: { name },
      });
      if (error || !data) throw error ?? new Error('Failed to update');
      setPlayer(data);
    });
  }

  if (!player) return null;

  return (
    <PageLayout>
      <IdentityPanel
        player={player}
        memberSince={stats?.member_since ?? new Date().toISOString()}
        onSaveName={handleSaveName}
        onPlayerUpdated={setPlayer}
      />

      {stats && (
        <Card className="p-4">
          <StatsGrid stats={stats} />
        </Card>
      )}

      <AccountPanel email={user?.email ?? ''} />
    </PageLayout>
  );
}
