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
  size?: 'sm' | 'md';
  className?: string;
}

export function Avatar({ name, index = 0, size = 'sm', className }: AvatarProps) {
  const colorClass = avatarColors[index % avatarColors.length];
  const initial = name.charAt(0).toUpperCase();
  return (
    <div
      className={cn(
        'flex items-center justify-center rounded-full font-bold flex-shrink-0',
        size === 'sm' ? 'w-[22px] h-[22px] text-[9px]' : 'w-[26px] h-[26px] text-[10px]',
        colorClass,
        className
      )}
    >
      {initial}
    </div>
  );
}

interface AvatarStackProps {
  names: string[];
  size?: 'sm' | 'md';
  className?: string;
}

export function AvatarStack({ names, size = 'md', className }: AvatarStackProps) {
  return (
    <div className={cn('flex items-center', className)}>
      {names.map((name, i) => (
        <Avatar
          key={name}
          name={name}
          index={i}
          size={size}
          className={cn(
            'border-[1.5px] border-[var(--surface)]',
            i > 0 ? (size === 'md' ? '-ml-2' : '-ml-1.5') : ''
          )}
        />
      ))}
    </div>
  );
}
