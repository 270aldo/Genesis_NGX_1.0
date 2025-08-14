/**
 * Virtual List Component - High Performance List Rendering
 * =====================================================
 *
 * This component renders large lists efficiently by only rendering
 * visible items in the viewport, significantly improving performance.
 */

import React, { useMemo, useCallback, useRef, useState, useEffect } from 'react';
import { cn } from '@/lib/utils';

export interface VirtualListProps<T> {
  items: T[];
  itemHeight: number;
  containerHeight?: number;
  className?: string;
  overscan?: number;
  renderItem: (item: T, index: number, style: React.CSSProperties) => React.ReactNode;
  onScroll?: (scrollTop: number) => void;
  estimatedItemSize?: number;
}

/**
 * Virtual List Component with smooth scrolling and performance optimizations
 */
export function VirtualList<T>({
  items,
  itemHeight,
  containerHeight = 400,
  className,
  overscan = 3,
  renderItem,
  onScroll,
  estimatedItemSize
}: VirtualListProps<T>) {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  // Calculate visible range
  const visibleRange = useMemo(() => {
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      items.length,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );

    return { startIndex, endIndex };
  }, [scrollTop, itemHeight, containerHeight, items.length, overscan]);

  // Generate visible items with proper styling
  const visibleItems = useMemo(() => {
    const { startIndex, endIndex } = visibleRange;
    return items.slice(startIndex, endIndex).map((item, index) => {
      const actualIndex = startIndex + index;
      const style: React.CSSProperties = {
        position: 'absolute',
        top: actualIndex * itemHeight,
        left: 0,
        right: 0,
        height: itemHeight,
      };

      return {
        item,
        index: actualIndex,
        style,
        key: `virtual-item-${actualIndex}`,
      };
    });
  }, [items, visibleRange, itemHeight]);

  // Handle scroll events with throttling
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const newScrollTop = e.currentTarget.scrollTop;
    setScrollTop(newScrollTop);
    onScroll?.(newScrollTop);
  }, [onScroll]);

  // Total height calculation
  const totalHeight = items.length * itemHeight;

  return (
    <div
      ref={containerRef}
      className={cn(
        'relative overflow-auto',
        'scrollbar-thin scrollbar-track-gray-100 scrollbar-thumb-gray-300',
        className
      )}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
    >
      {/* Virtual container with full height */}
      <div style={{ height: totalHeight, position: 'relative' }}>
        {visibleItems.map(({ item, index, style, key }) => (
          <div key={key} style={style}>
            {renderItem(item, index, style)}
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Dynamic Virtual List with variable item heights
 */
export interface DynamicVirtualListProps<T> extends Omit<VirtualListProps<T>, 'itemHeight'> {
  getItemHeight: (index: number) => number;
  defaultItemHeight?: number;
}

export function DynamicVirtualList<T>({
  items,
  getItemHeight,
  defaultItemHeight = 50,
  containerHeight = 400,
  className,
  overscan = 3,
  renderItem,
  onScroll,
}: DynamicVirtualListProps<T>) {
  const [scrollTop, setScrollTop] = useState(0);
  const [itemHeights, setItemHeights] = useState<Map<number, number>>(new Map());
  const containerRef = useRef<HTMLDivElement>(null);

  // Calculate cumulative heights for positioning
  const cumulativeHeights = useMemo(() => {
    const heights: number[] = [0];
    for (let i = 0; i < items.length; i++) {
      const height = itemHeights.get(i) || getItemHeight(i) || defaultItemHeight;
      heights.push(heights[i] + height);
    }
    return heights;
  }, [items.length, itemHeights, getItemHeight, defaultItemHeight]);

  // Find visible range using binary search for efficiency
  const visibleRange = useMemo(() => {
    const findIndex = (offset: number) => {
      let start = 0;
      let end = cumulativeHeights.length - 1;

      while (start < end) {
        const mid = Math.floor((start + end) / 2);
        if (cumulativeHeights[mid] < offset) {
          start = mid + 1;
        } else {
          end = mid;
        }
      }

      return Math.max(0, start - 1);
    };

    const startIndex = Math.max(0, findIndex(scrollTop) - overscan);
    const endIndex = Math.min(
      items.length,
      findIndex(scrollTop + containerHeight) + overscan + 1
    );

    return { startIndex, endIndex };
  }, [scrollTop, containerHeight, cumulativeHeights, overscan, items.length]);

  const visibleItems = useMemo(() => {
    const { startIndex, endIndex } = visibleRange;
    return items.slice(startIndex, endIndex).map((item, index) => {
      const actualIndex = startIndex + index;
      const top = cumulativeHeights[actualIndex];
      const height = cumulativeHeights[actualIndex + 1] - top;

      const style: React.CSSProperties = {
        position: 'absolute',
        top,
        left: 0,
        right: 0,
        height,
      };

      return {
        item,
        index: actualIndex,
        style,
        key: `dynamic-virtual-item-${actualIndex}`,
      };
    });
  }, [items, visibleRange, cumulativeHeights]);

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const newScrollTop = e.currentTarget.scrollTop;
    setScrollTop(newScrollTop);
    onScroll?.(newScrollTop);
  }, [onScroll]);

  const totalHeight = cumulativeHeights[cumulativeHeights.length - 1] || 0;

  return (
    <div
      ref={containerRef}
      className={cn(
        'relative overflow-auto',
        'scrollbar-thin scrollbar-track-gray-100 scrollbar-thumb-gray-300',
        className
      )}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        {visibleItems.map(({ item, index, style, key }) => (
          <div key={key} style={style}>
            {renderItem(item, index, style)}
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Windowed Grid Component for 2D virtualization
 */
export interface VirtualGridProps<T> {
  items: T[];
  itemWidth: number;
  itemHeight: number;
  columnsCount: number;
  containerWidth?: number;
  containerHeight?: number;
  className?: string;
  overscan?: number;
  renderItem: (item: T, index: number, style: React.CSSProperties) => React.ReactNode;
}

export function VirtualGrid<T>({
  items,
  itemWidth,
  itemHeight,
  columnsCount,
  containerWidth = 800,
  containerHeight = 400,
  className,
  overscan = 1,
  renderItem,
}: VirtualGridProps<T>) {
  const [scrollTop, setScrollTop] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);

  const rowCount = Math.ceil(items.length / columnsCount);

  const visibleRange = useMemo(() => {
    const startRow = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endRow = Math.min(
      rowCount,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );

    const startCol = Math.max(0, Math.floor(scrollLeft / itemWidth) - overscan);
    const endCol = Math.min(
      columnsCount,
      Math.ceil((scrollLeft + containerWidth) / itemWidth) + overscan
    );

    return { startRow, endRow, startCol, endCol };
  }, [scrollTop, scrollLeft, itemHeight, itemWidth, containerHeight, containerWidth, overscan, rowCount, columnsCount]);

  const visibleItems = useMemo(() => {
    const { startRow, endRow, startCol, endCol } = visibleRange;
    const visible: Array<{
      item: T;
      index: number;
      style: React.CSSProperties;
      key: string;
    }> = [];

    for (let row = startRow; row < endRow; row++) {
      for (let col = startCol; col < endCol; col++) {
        const index = row * columnsCount + col;
        if (index >= items.length) continue;

        const style: React.CSSProperties = {
          position: 'absolute',
          top: row * itemHeight,
          left: col * itemWidth,
          width: itemWidth,
          height: itemHeight,
        };

        visible.push({
          item: items[index],
          index,
          style,
          key: `grid-item-${row}-${col}`,
        });
      }
    }

    return visible;
  }, [items, visibleRange, itemHeight, itemWidth, columnsCount]);

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
    setScrollLeft(e.currentTarget.scrollLeft);
  }, []);

  const totalWidth = columnsCount * itemWidth;
  const totalHeight = rowCount * itemHeight;

  return (
    <div
      className={cn(
        'relative overflow-auto',
        'scrollbar-thin scrollbar-track-gray-100 scrollbar-thumb-gray-300',
        className
      )}
      style={{ width: containerWidth, height: containerHeight }}
      onScroll={handleScroll}
    >
      <div style={{ width: totalWidth, height: totalHeight, position: 'relative' }}>
        {visibleItems.map(({ item, index, style, key }) => (
          <div key={key} style={style}>
            {renderItem(item, index, style)}
          </div>
        ))}
      </div>
    </div>
  );
}

// Export utility hooks
export { useDebounce, useThrottle } from '@/utils/performanceOptimizations';
