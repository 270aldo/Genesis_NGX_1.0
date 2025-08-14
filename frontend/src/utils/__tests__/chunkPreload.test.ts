import { preloadChunk, clearChunkCache, isChunkPreloaded } from '../chunkPreload';

// Mock dynamic import
const mockImport = jest.fn();
Object.defineProperty(global, 'import', {
  value: mockImport,
  writable: true
});

describe('chunkPreload', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    clearChunkCache();
  });

  describe('preloadChunk', () => {
    it('preloads chunk successfully', async () => {
      const mockModule = { default: jest.fn() };
      mockImport.mockResolvedValueOnce(mockModule);

      await preloadChunk('test-chunk');

      expect(mockImport).toHaveBeenCalledWith('test-chunk');
    });

    it('handles preload errors gracefully', async () => {
      mockImport.mockRejectedValueOnce(new Error('Chunk not found'));

      await expect(preloadChunk('missing-chunk')).resolves.not.toThrow();
    });

    it('caches preloaded chunks', async () => {
      const mockModule = { default: jest.fn() };
      mockImport.mockResolvedValueOnce(mockModule);

      await preloadChunk('cached-chunk');

      expect(isChunkPreloaded('cached-chunk')).toBe(true);
    });

    it('does not preload already cached chunks', async () => {
      const mockModule = { default: jest.fn() };
      mockImport.mockResolvedValueOnce(mockModule);

      await preloadChunk('duplicate-chunk');
      await preloadChunk('duplicate-chunk');

      expect(mockImport).toHaveBeenCalledTimes(1);
    });
  });

  describe('isChunkPreloaded', () => {
    it('returns false for non-preloaded chunks', () => {
      expect(isChunkPreloaded('never-loaded')).toBe(false);
    });

    it('returns true for preloaded chunks', async () => {
      const mockModule = { default: jest.fn() };
      mockImport.mockResolvedValueOnce(mockModule);

      await preloadChunk('loaded-chunk');

      expect(isChunkPreloaded('loaded-chunk')).toBe(true);
    });
  });

  describe('clearChunkCache', () => {
    it('clears all cached chunks', async () => {
      const mockModule = { default: jest.fn() };
      mockImport.mockResolvedValue(mockModule);

      await preloadChunk('chunk1');
      await preloadChunk('chunk2');

      expect(isChunkPreloaded('chunk1')).toBe(true);
      expect(isChunkPreloaded('chunk2')).toBe(true);

      clearChunkCache();

      expect(isChunkPreloaded('chunk1')).toBe(false);
      expect(isChunkPreloaded('chunk2')).toBe(false);
    });
  });
});
