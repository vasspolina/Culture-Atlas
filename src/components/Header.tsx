import React from 'react';
import type { Tier, Size } from '../types';
import { TIER } from '../types';
import { PWAInstallPrompt } from './PWAInstallPrompt';

interface HeaderProps {
  selectedTiers: Set<Tier>;
  onToggleTier: (tier: Tier) => void;
  tierCounts: Record<Tier, number>;
  selectedSize: Size | 'all';
  onSelectSize: (size: Size | 'all') => void;
}

export const Header: React.FC<HeaderProps> = ({
  selectedTiers,
  onToggleTier,
  tierCounts,
  selectedSize,
  onSelectSize,
}) => {
  return (
    <header>
      <div className="controls">
        <PWAInstallPrompt />
        <div className="chips" role="group" aria-label="Show tiers">
          {(['A', 'B', 'U'] as Tier[]).map((t) => {
            const isPressed = selectedTiers.has(t);
            return (
              <button
                key={t}
                type="button"
                className="chip"
                data-tier={t}
                aria-pressed={isPressed}
                style={{ '--c': TIER[t].c } as React.CSSProperties}
                onClick={() => onToggleTier(t)}
              >
                <span className="dot" />
                {TIER[t].l} <span className="n">{tierCounts[t] ?? 0}</span>
              </button>
            );
          })}
        </div>
        <div className="seg" role="group" aria-label="Institution size">
          <button
            type="button"
            data-size="all"
            aria-pressed={selectedSize === 'all'}
            onClick={() => onSelectSize('all')}
          >
            All sizes
          </button>
          <button
            type="button"
            data-size="S"
            aria-pressed={selectedSize === 'S'}
            onClick={() => onSelectSize('S')}
          >
            Small and mid
          </button>
          <button
            type="button"
            data-size="L"
            aria-pressed={selectedSize === 'L'}
            onClick={() => onSelectSize('L')}
          >
            Large
          </button>
        </div>
      </div>
    </header>
  );
};
