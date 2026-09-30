import React from 'react';
import type { Institution } from '../types';
import { TIER } from '../types';

interface DetailPanelProps {
  selected: Institution | null;
}

export function cleanHost(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
}

export const DetailPanel: React.FC<DetailPanelProps> = ({ selected }) => {
  return (
    <div className="detail" id="detail">
      {!selected ? (
        <p className="empty">
          Click a dot on the map, or a name in the list, to see funding, sponsors and any record of controversy.
        </p>
      ) : (
        <>
          <div
            className="eyebrow"
            style={{ '--c': TIER[selected.t].c } as React.CSSProperties}
          >
            <span className="dot" />
            {TIER[selected.t].l} · {selected.s === 'L' ? 'large' : 'small or mid'}
          </div>
          <h2>{selected.n}</h2>
          <p className="city">{selected.c}</p>
          <dl>
            <dt>Money</dt>
            <dd>{selected.f}</dd>
            {selected.w ? (
              <>
                <dt>Note</dt>
                <dd>{selected.w}</dd>
              </>
            ) : null}
            <dt>Sources</dt>
            <dd className="src">
              {(selected.u || []).map((url, i) => (
                <a
                  key={i}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {cleanHost(url)}
                </a>
              ))}
            </dd>
          </dl>
        </>
      )}
    </div>
  );
};
