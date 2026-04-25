import { useState } from 'react';
import { usePlayerNames } from '@/hooks/PlayerNamesContext';
import { cn } from '@/lib/utils';

const avatarColors = [
  'bg-[rgba(124,158,248,0.2)] text-[#7c9ef8]',
  'bg-[rgba(94,203,138,0.2)] text-[#5ecb8a]',
  'bg-[rgba(240,180,41,0.2)] text-[#f0b429]',
  'bg-[rgba(240,101,96,0.2)] text-[#f06560]',
];

interface AvatarProps {
  name: string;
  index?: number;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  playerId?: number;
  hasPicture?: boolean;
}

export function Avatar({
  name,
  index = 0,
  size = 'sm',
  className,
  playerId,
  hasPicture,
}: AvatarProps) {
  const [imgError, setImgError] = useState(false);

  const sizeClass =
    size === 'sm'
      ? 'w-[22px] h-[22px] text-[9px]'
      : size === 'lg'
        ? 'w-[36px] h-[36px] text-[13px]'
        : 'w-[26px] h-[26px] text-[10px]';

  if (playerId && hasPicture && !imgError) {
    return (
      <img
        src={`/media/players/${playerId}.jpg`}
        alt={name}
        onError={() => setImgError(true)}
        className={cn('rounded-full object-cover flex-shrink-0', sizeClass, className)}
      />
    );
  }

  const colorClass = avatarColors[index % avatarColors.length];
  return (
    <div
      className={cn(
        'flex items-center justify-center rounded-full font-bold flex-shrink-0',
        sizeClass,
        colorClass,
        className
      )}
    >
      {name.charAt(0).toUpperCase()}
    </div>
  );
}

interface AvatarStackProps {
  playerIds: number[];
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function AvatarStack({ playerIds, size = 'md', className }: AvatarStackProps) {
  const { names, pictures } = usePlayerNames();
  return (
    <div className={cn('flex items-center', className)}>
      {playerIds.map((id, i) => (
        <Avatar
          key={id}
          name={names[id] ?? String(id)}
          index={i}
          size={size}
          playerId={id}
          hasPicture={pictures[id] ?? false}
          className={cn(
            'border-[1.5px] border-[var(--surface)]',
            i > 0 ? (size === 'lg' ? '-ml-2.5' : size === 'md' ? '-ml-2' : '-ml-1.5') : ''
          )}
        />
      ))}
    </div>
  );
}
