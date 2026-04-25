import { fireEvent, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ALICE, createMockServer, renderWithProviders } from '@/test/helpers';
import { PicturePicker } from './PicturePicker';

createMockServer();

const PLAYER = { ...ALICE, account_id: 'acc-1', has_picture: false };

afterEach(() => {
  vi.restoreAllMocks();
});

beforeEach(() => {
  vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock');
});

describe('PicturePicker', () => {
  describe('file validation', () => {
    it('shows error for unsupported file type', async () => {
      whenRendered();
      whenFileSelected(makeFile('photo.gif', 'image/gif'));
      thenErrorVisible('Only JPEG and PNG images are supported');
    });

    it('shows error when file exceeds 5MB', async () => {
      whenRendered();
      whenFileSelected(makeFile('photo.jpg', 'image/jpeg', 6 * 1024 * 1024));
      thenErrorVisible('Image must be smaller than 5MB');
    });

    it('opens crop modal for valid JPEG', async () => {
      whenRendered();
      whenFileSelected(makeFile('photo.jpg', 'image/jpeg'));
      thenCropModalVisible();
    });

    it('opens crop modal for valid PNG', async () => {
      whenRendered();
      whenFileSelected(makeFile('photo.png', 'image/png'));
      thenCropModalVisible();
    });
  });

  describe('cancel', () => {
    it('closes the crop modal', async () => {
      whenRendered();
      whenFileSelected(makeFile('photo.jpg', 'image/jpeg'));
      thenCropModalVisible();
      await whenCancelClicked();
      thenCropModalNotVisible();
    });

    it('clears error when a new valid file is selected then cancelled', async () => {
      whenRendered();
      whenFileSelected(makeFile('photo.gif', 'image/gif'));
      thenErrorVisible('Only JPEG and PNG images are supported');
      whenFileSelected(makeFile('photo.jpg', 'image/jpeg'));
      await whenCancelClicked();
      thenCropModalNotVisible();
      expect(screen.queryByText('Only JPEG and PNG images are supported')).toBeNull();
    });
  });

  function whenRendered() {
    renderWithProviders(<PicturePicker player={PLAYER} onSuccess={vi.fn()} />);
  }

  function whenFileSelected(file: File) {
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    Object.defineProperty(input, 'files', { value: [file], configurable: true });
    fireEvent.change(input);
  }

  async function whenCancelClicked() {
    await userEvent.click(screen.getByRole('button', { name: /cancel/i }));
  }

  function makeFile(name: string, type: string, size = 1024) {
    return new File([new ArrayBuffer(size)], name, { type });
  }

  function thenCropModalVisible() {
    expect(screen.getByText('Crop your picture')).toBeInTheDocument();
  }

  function thenCropModalNotVisible() {
    expect(screen.queryByText('Crop your picture')).toBeNull();
  }

  function thenErrorVisible(message: string) {
    expect(screen.getByText(message)).toBeInTheDocument();
  }
});
