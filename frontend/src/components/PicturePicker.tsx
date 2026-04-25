import { useRef, useState } from 'react';
import ReactCrop, { type Crop, centerCrop, makeAspectCrop } from 'react-image-crop';
import 'react-image-crop/dist/ReactCrop.css';
import { apiClient } from '@/api';
import type { components } from '@/api/schema';
import { Avatar } from './Avatar';

type Player = components['schemas']['Player'];

interface Props {
  player: Player;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  onSuccess: (updated: Player) => void;
}

function getCroppedBlob(image: HTMLImageElement, crop: Crop): Promise<Blob> {
  const canvas = document.createElement('canvas');
  const scaleX = image.naturalWidth / image.width;
  const scaleY = image.naturalHeight / image.height;
  canvas.width = crop.width;
  canvas.height = crop.height;
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('No canvas context');
  ctx.drawImage(
    image,
    crop.x * scaleX,
    crop.y * scaleY,
    crop.width * scaleX,
    crop.height * scaleY,
    0,
    0,
    crop.width,
    crop.height
  );
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => (blob ? resolve(blob) : reject(new Error('Canvas empty'))),
      'image/jpeg',
      0.95
    );
  });
}

export function PicturePicker({ player, size = 'md', className, onSuccess }: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  const [srcUrl, setSrcUrl] = useState<string | null>(null);
  const [crop, setCrop] = useState<Crop>();
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!['image/jpeg', 'image/png'].includes(file.type)) {
      setError('Only JPEG and PNG images are supported');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError('Image must be smaller than 5MB');
      return;
    }
    setError(null);
    setSrcUrl(URL.createObjectURL(file));
    setCrop(undefined);
  }

  function handleImageLoad(e: React.SyntheticEvent<HTMLImageElement>) {
    const { width, height } = e.currentTarget;
    const side = Math.min(width, height);
    setCrop(
      centerCrop(makeAspectCrop({ unit: 'px', width: side }, 1, width, height), width, height)
    );
  }

  async function handleConfirm() {
    if (!imgRef.current || !crop) return;
    setUploading(true);
    setError(null);
    try {
      const blob = await getCroppedBlob(imgRef.current, crop);
      const form = new FormData();
      form.append('picture', blob, 'picture.jpg');
      const { data, error: apiError } = await apiClient.POST('/players/{player_id}/picture', {
        params: { path: { player_id: player.id } },
        body: form as never,
        bodySerializer: () => form,
      });
      if (apiError || !data) {
        setError('Upload failed');
        return;
      }
      setSrcUrl(null);
      onSuccess(data);
    } catch {
      setError('Upload failed');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  }

  function handleCancel() {
    setSrcUrl(null);
    setCrop(undefined);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  }

  return (
    <>
      <button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        className="cursor-pointer focus:outline-none"
        aria-label="Change profile picture"
      >
        <Avatar
          name={player.name}
          playerId={player.id}
          hasPicture={player.has_picture}
          size={size}
          className={className}
        />
      </button>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png"
        onChange={handleFileChange}
        className="hidden"
      />
      {error && !srcUrl && <div className="text-[12px] text-[#f06560] mt-1">{error}</div>}
      {srcUrl && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="flex flex-col gap-4 p-5 bg-[var(--surface-2)] border border-[var(--border-2)] rounded-[16px] shadow-[0_8px_32px_rgba(0,0,0,0.5)] max-w-sm w-full mx-4">
            <div className="text-[14px] font-semibold text-foreground">Crop your picture</div>
            <ReactCrop crop={crop} onChange={(c) => setCrop(c)} aspect={1} circularCrop>
              <img
                ref={imgRef}
                src={srcUrl}
                alt="Crop preview"
                onLoad={handleImageLoad}
                className="max-h-72 w-full object-contain"
              />
            </ReactCrop>
            {error && <div className="text-[12px] text-[#f06560]">{error}</div>}
            <div className="flex gap-2 justify-end">
              <button
                type="button"
                onClick={handleCancel}
                className="h-[34px] px-4 text-[13px] font-medium text-[var(--text-muted)] bg-[var(--surface)] border border-[var(--border-2)] rounded-lg cursor-pointer hover:text-foreground"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirm}
                disabled={uploading || !crop}
                className="h-[34px] px-4 text-[13px] font-medium text-white bg-[#7c9ef8] rounded-lg cursor-pointer disabled:opacity-50"
              >
                {uploading ? 'Uploading…' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
