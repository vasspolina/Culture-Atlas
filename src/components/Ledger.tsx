import React, { useEffect, useRef } from 'react';
import type { Institution, Tier } from '../types';
import { TIER } from '../types';

interface LedgerProps {
  visibleInstitutions: Institution[];
  selectedTiers: Set<Tier>;
  selected: Institution | null;
  onSelect: (inst: Institution) => void;
}

export const Ledger: React.FC<LedgerProps> = ({
  visibleInstitutions,
  selectedTiers,
  selected,
  onSelect,
}) => {
  const ledgerRef = useRef<HTMLDivElement>(null);
  const activeBtnRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    if (activeBtnRef.current) {
      activeBtnRef.current.scrollIntoView({ block: 'nearest' });
    }
  }, [selected]);

  const groups = (['A', 'B', 'U'] as Tier[]).filter((t) => selectedTiers.has(t));

  const hasAnyItems = groups.some((t) =>
    visibleInstitutions.some((d) => d.t === t)
  );

  return (
    <div className="ledger" id="ledger" ref={ledgerRef}>
      {!hasAnyItems ? (
        <p className="none">
          Nothing matches. Clear the search or switch a tier back on.
        </p>
      ) : (
        groups.map((t) => {
          const rows = visibleInstitutions
            .filter((d) => d.t === t)
            .sort((a, b) => a.c.localeCompare(b.c) || a.n.localeCompare(b.n));

          if (rows.length === 0) return null;

          return (
            <React.Fragment key={t}>
              <h3>
                {TIER[t].l} · {rows.length}
              </h3>
              <ul>
                {rows.map((d) => {
                  const isCurrent = selected?.n === d.n;
                  const cityName = d.c.split(',')[0];
                  return (
                    <li key={d.n}>
                      <button
                        type="button"
                        ref={isCurrent ? activeBtnRef : undefined}
                        aria-current={isCurrent}
                        style={{ '--c': TIER[t].c } as React.CSSProperties}
                        onClick={() => onSelect(d)}
                      >
                        <span className={`dot ${d.s}`} />
                        <span>{d.n}</span>
                        <span className="where">{cityName}</span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </React.Fragment>
          );
        })
      )}
    </div>
  );
};
