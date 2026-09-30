import React, { useState, useMemo, useCallback } from 'react';
import type { Institution, Tier, Size } from './types';
import { DATA } from './data/institutions';
import { Header } from './components/Header';
import { GlobeMap } from './components/GlobeMap';
import { DetailPanel } from './components/DetailPanel';
import { Ledger } from './components/Ledger';
import { ListView } from './components/ListView';
import { Footer } from './components/Footer';

export default function App() {
  const [selectedTiers, setSelectedTiers] = useState<Set<Tier>>(
    () => new Set(['A', 'B', 'U'])
  );

  const [selectedSize, setSelectedSize] = useState<Size | 'all'>(() => {
    try {
      const saved = localStorage.getItem('atlas-size');
      if (saved === 'all' || saved === 'S' || saved === 'L') {
        return saved;
      }
    } catch {}
    return 'all';
  });

  const [selected, setSelected] = useState<Institution | null>(null);
  const [activeView, setActiveView] = useState<'globe' | 'list'>('globe');

  const handleToggleView = useCallback((view: 'globe' | 'list') => {
    setActiveView(view);
    if (view === 'list') {
      const listEl = document.querySelector('.listview');
      if (listEl) {
        listEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    } else {
      const mapEl = document.querySelector('.mapwrap');
      if (mapEl) {
        mapEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }, []);

  // Compute counts per tier across entire dataset
  const tierCounts = useMemo<Record<Tier, number>>(() => {
    const counts: Record<Tier, number> = { A: 0, B: 0, U: 0 };
    for (const d of DATA) {
      if (counts[d.t] !== undefined) {
        counts[d.t]++;
      }
    }
    return counts;
  }, []);

  // Filtered institutions
  const visibleInstitutions = useMemo(() => {
    return DATA.filter(
      (d) =>
        selectedTiers.has(d.t) &&
        (selectedSize === 'all' || d.s === selectedSize)
    );
  }, [selectedTiers, selectedSize]);

  // Toggle tier handler
  const handleToggleTier = useCallback((tier: Tier) => {
    setSelectedTiers((prev) => {
      const next = new Set(prev);
      if (next.has(tier)) {
        next.delete(tier);
      } else {
        next.add(tier);
      }
      return next;
    });
  }, []);

  // Select size handler with local storage persistence
  const handleSelectSize = useCallback((size: Size | 'all') => {
    setSelectedSize(size);
    try {
      localStorage.setItem('atlas-size', size);
    } catch {}
  }, []);

  // Ensure institution's tier and size are enabled
  const handleEnsureVisible = useCallback((inst: Institution) => {
    setSelectedTiers((prev) => {
      if (!prev.has(inst.t)) {
        const next = new Set(prev);
        next.add(inst.t);
        return next;
      }
      return prev;
    });

    setSelectedSize((prev) => {
      if (prev !== 'all' && inst.s !== prev) {
        try {
          localStorage.setItem('atlas-size', 'all');
        } catch {}
        return 'all';
      }
      return prev;
    });
  }, []);

  // Selection from Map or Ledger
  const handleSelect = useCallback((inst: Institution | null) => {
    setSelected(inst);
  }, []);

  // Selection from table with smooth scroll to map
  const handleSelectAndScroll = useCallback(
    (inst: Institution) => {
      handleEnsureVisible(inst);
      setSelected(inst);
      const mapwrap = document.querySelector('.mapwrap');
      if (mapwrap) {
        mapwrap.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    },
    [handleEnsureVisible]
  );

  return (
    <div className="app">
      <Header
        selectedTiers={selectedTiers}
        onToggleTier={handleToggleTier}
        tierCounts={tierCounts}
        selectedSize={selectedSize}
        onSelectSize={handleSelectSize}
      />

      <main>
        <GlobeMap
          allInstitutions={DATA}
          visibleInstitutions={visibleInstitutions}
          selected={selected}
          onSelect={handleSelect}
          onEnsureVisible={handleEnsureVisible}
          activeView={activeView}
          onToggleView={handleToggleView}
        />

        <aside>
          <DetailPanel selected={selected} />
          <Ledger
            visibleInstitutions={visibleInstitutions}
            selectedTiers={selectedTiers}
            selected={selected}
            onSelect={handleSelect}
          />
        </aside>
      </main>

      <ListView
        visibleInstitutions={visibleInstitutions}
        selectedTiers={selectedTiers}
        selected={selected}
        onSelectAndScroll={handleSelectAndScroll}
      />

      <Footer />
    </div>
  );
}
