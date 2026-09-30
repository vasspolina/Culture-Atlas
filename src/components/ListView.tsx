import React from 'react';
import type { Institution, Tier } from '../types';
import { TIER } from '../types';
import { cleanHost } from './DetailPanel';

interface ListViewProps {
  visibleInstitutions: Institution[];
  selectedTiers: Set<Tier>;
  selected: Institution | null;
  onSelectAndScroll: (inst: Institution) => void;
}

export const ListView: React.FC<ListViewProps> = ({
  visibleInstitutions,
  selectedTiers,
  selected,
  onSelectAndScroll,
}) => {
  const groups = (['A', 'B', 'U'] as Tier[]).filter((t) => selectedTiers.has(t));

  return (
    <section className="listview" id="listview" aria-label="List of institutions">
      <h2>
        Every institution on the globe
        <span className="count">{visibleInstitutions.length}</span>
      </h2>

      {groups.map((t) => {
        const rows = visibleInstitutions
          .filter((d) => d.t === t)
          .sort((a, b) => a.c.localeCompare(b.c) || a.n.localeCompare(b.n));

        if (rows.length === 0) return null;

        return (
          <React.Fragment key={t}>
            <h3 style={{ '--c': TIER[t].c } as React.CSSProperties}>
              <span className="dot" />
              {TIER[t].l} · {rows.length}
            </h3>
            <div className="tablewrap">
              <table>
                <thead>
                  <tr>
                    <th>Institution</th>
                    <th>Where</th>
                    <th>Size</th>
                    <th>Money</th>
                    <th>Note</th>
                    <th>Sources</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((d) => {
                    const isCurrent = selected?.n === d.n;
                    return (
                      <tr key={d.n}>
                        <td className="name">
                          <button
                            type="button"
                            aria-current={isCurrent}
                            onClick={() => onSelectAndScroll(d)}
                          >
                            {d.n}
                          </button>
                        </td>
                        <td className="where">{d.c}</td>
                        <td className="size">{d.s === 'L' ? 'large' : 'small'}</td>
                        <td className="money">{d.f}</td>
                        <td className="note">{d.w}</td>
                        <td className="src">
                          {(d.u || []).map((url, i) => (
                            <a
                              key={i}
                              href={url}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              {cleanHost(url)}
                            </a>
                          ))}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </React.Fragment>
        );
      })}
    </section>
  );
};
