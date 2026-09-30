import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import * as topojson from 'topojson-client';
import type { Institution } from '../types';
import { TIER } from '../types';
import topoData from '../data/world-topo.json';
import countriesData from '../data/countries.json';
import citiesData from '../data/cities.json';

interface CountryItem {
  id: string;
  name: string;
  lo: number;
  la: number;
  area: number;
}

interface CityItem {
  name: string;
  country: string;
  count: number;
  lo: number;
  la: number;
}

interface GlobeMapProps {
  allInstitutions: Institution[];
  visibleInstitutions: Institution[];
  selected: Institution | null;
  onSelect: (inst: Institution | null, shouldFocus?: boolean) => void;
  onEnsureVisible: (inst: Institution) => void;
  activeView?: 'globe' | 'list';
  onToggleView?: (view: 'globe' | 'list') => void;
}

const HOME: [number, number] = [30, -38];
const ZMIN = 1;
const ZMAX = 80;

export const GlobeMap: React.FC<GlobeMapProps> = ({
  allInstitutions,
  visibleInstitutions,
  selected,
  onSelect,
  onEnsureVisible,
  activeView = 'globe',
  onToggleView,
}) => {
  const wrapRef = useRef<HTMLDivElement>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const tipRef = useRef<HTMLDivElement>(null);
  const scalebarRef = useRef<HTMLDivElement>(null);
  const scalelabelRef = useRef<HTMLSpanElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Institution[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [isSpinning, setIsSpinning] = useState(true);

  // References to keep state accessible in D3 / event callbacks
  const stateRef = useRef<{
    visible: Institution[];
    selected: Institution | null;
    zoom: number;
    w: number;
    h: number;
    r: number;
    spinning: boolean;
    reducedMotion: boolean;
  }>({
    visible: visibleInstitutions,
    selected,
    zoom: 1,
    w: 0,
    h: 0,
    r: 0,
    spinning: true,
    reducedMotion: false,
  });

  // Keep stateRef in sync
  useEffect(() => {
    stateRef.current.visible = visibleInstitutions;
    stateRef.current.selected = selected;
  }, [visibleInstitutions, selected]);

  // D3 elements refs
  const d3Refs = useRef<{
    svg: d3.Selection<SVGSVGElement, unknown, null, undefined> | null;
    projection: d3.GeoProjection | null;
    pathGenerator: d3.GeoPath | null;
    sphere: d3.Selection<SVGPathElement, unknown, null, undefined> | null;
    atmosphereGlow: d3.Selection<SVGPathElement, unknown, null, undefined> | null;
    rimHighlight: d3.Selection<SVGPathElement, unknown, null, undefined> | null;
    grat: d3.Selection<SVGPathElement, unknown, null, undefined> | null;
    land: d3.Selection<SVGGElement, unknown, null, undefined> | null;
    shade: d3.Selection<SVGPathElement, unknown, null, undefined> | null;
    countriesGroup: d3.Selection<SVGGElement, unknown, null, undefined> | null;
    citiesGroup: d3.Selection<SVGGElement, unknown, null, undefined> | null;
    dots: d3.Selection<SVGGElement, unknown, null, undefined> | null;
    labels: d3.Selection<SVGGElement, unknown, null, undefined> | null;
    draw: () => void;
    flyTo: (lo: number, la: number, z: number) => void;
    animateZoom: (z: number, pt: [number, number] | null, ms: number) => void;
    stopMotion: () => void;
  } | null>(null);

  // Initialize D3 Map
  useEffect(() => {
    if (!mapContainerRef.current || !wrapRef.current) return;

    // Check reduced motion
    const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    stateRef.current.reducedMotion = reduced;
    stateRef.current.spinning = !reduced;
    setIsSpinning(!reduced);

    // Clear previous
    mapContainerRef.current.innerHTML = '';

    const wrapEl = wrapRef.current;
    const tipEl = tipRef.current;

    // Create SVG
    const svg = d3
      .select(mapContainerRef.current)
      .append('svg')
      .attr('role', 'application')
      .attr('tabindex', 0)
      .attr('aria-label', 'Globe with institutions marked by sponsor tier. Drag to turn, scroll to zoom, arrow keys to move.');

    const svgEl = svg.node()!;

    // Defs & Gradients for Illuminated Neon Blue & Green 3D Sphere
    const defs = svg.append('defs');

    // Bloom glow filter for the globe atmosphere
    const bloom = defs.append('filter').attr('id', 'globeBloom').attr('x', '-30%').attr('y', '-30%').attr('width', '160%').attr('height', '160%');
    bloom.append('feGaussianBlur').attr('stdDeviation', '18').attr('result', 'coloredBlur');
    const merge = bloom.append('feMerge');
    merge.append('feMergeNode').attr('in', 'coloredBlur');
    merge.append('feMergeNode').attr('in', 'SourceGraphic');

    // Ocean Gradient: Deep cobalt to electric cyan
    const oceanGrad = defs
      .append('radialGradient')
      .attr('id', 'oceanGrad')
      .attr('cx', '50%')
      .attr('cy', '45%')
      .attr('r', '55%');
    oceanGrad.append('stop').attr('offset', '0%').attr('stop-color', '#00264d');
    oceanGrad.append('stop').attr('offset', '70%').attr('stop-color', '#001124');
    oceanGrad.append('stop').attr('offset', '100%').attr('stop-color', '#00050d');

    // Land Gradient: Electric blue to neon green
    const landGrad = defs
      .append('radialGradient')
      .attr('id', 'landGrad')
      .attr('cx', '50%')
      .attr('cy', '45%')
      .attr('r', '60%');
    landGrad.append('stop').attr('offset', '0%').attr('stop-color', '#00ffaa').attr('stop-opacity', 0.95);
    landGrad.append('stop').attr('offset', '55%').attr('stop-color', '#0099ff').attr('stop-opacity', 0.92);
    landGrad.append('stop').attr('offset', '100%').attr('stop-color', '#0033aa').attr('stop-opacity', 0.88);

    // Sunlit directional shade
    const grad = defs
      .append('radialGradient')
      .attr('id', 'shade')
      .attr('cx', '35%')
      .attr('cy', '28%')
      .attr('r', '74%');

    grad.append('stop').attr('offset', '0%').attr('stop-color', '#00ffc4').attr('stop-opacity', 0.28);
    grad.append('stop').attr('offset', '48%').attr('stop-color', '#0077ff').attr('stop-opacity', 0.05);
    grad.append('stop').attr('offset', '75%').attr('stop-color', '#000814').attr('stop-opacity', 0.4);
    grad.append('stop').attr('offset', '100%').attr('stop-color', '#000000').attr('stop-opacity', 0.85);

    // Atmosphere outer halo in glowing electric cyan-blue and neon green
    const atmoGrad = defs
      .append('radialGradient')
      .attr('id', 'atmo')
      .attr('cx', '50%')
      .attr('cy', '50%')
      .attr('r', '50%');

    atmoGrad.append('stop').attr('offset', '75%').attr('stop-color', '#00ffff').attr('stop-opacity', 0);
    atmoGrad.append('stop').attr('offset', '88%').attr('stop-color', '#00ff87').attr('stop-opacity', 0.25);
    atmoGrad.append('stop').attr('offset', '96%').attr('stop-color', '#0077ff').attr('stop-opacity', 0.45);
    atmoGrad.append('stop').attr('offset', '100%').attr('stop-color', '#00ffff').attr('stop-opacity', 0);

    // Rim inner neon light
    const rimGrad = defs
      .append('radialGradient')
      .attr('id', 'rim')
      .attr('cx', '50%')
      .attr('cy', '50%')
      .attr('r', '50%');

    rimGrad.append('stop').attr('offset', '80%').attr('stop-color', '#000000').attr('stop-opacity', 0);
    rimGrad.append('stop').attr('offset', '94%').attr('stop-color', '#00ff87').attr('stop-opacity', 0.4);
    rimGrad.append('stop').attr('offset', '100%').attr('stop-color', '#00ffff').attr('stop-opacity', 0.65);

    const g = svg.append('g');
    const sphere = g.append('path').attr('class', 'sphere');
    const grat = g.append('path').attr('class', 'grat');
    const land = g.append('g').attr('class', 'land');
    const shade = g.append('path').attr('class', 'shade').attr('fill', 'url(#shade)');
    const rimHighlight = g.append('path').attr('class', 'rim-highlight').attr('fill', 'url(#rim)');
    const atmosphereGlow = g.append('path').attr('class', 'atmosphere-glow').attr('fill', 'url(#atmo)');

    // Geographic text layers
    const countriesGroup = g.append('g').attr('class', 'countries-layer');
    const dots = g.append('g').attr('class', 'dots');
    const labels = g.append('g').attr('class', 'labels');
    const citiesGroup = g.append('g').attr('class', 'cities-layer');

    const projection = d3.geoOrthographic().rotate(HOME).clipAngle(90).precision(0.4);
    const pathGenerator = d3.geoPath(projection);

    // Load TopoJSON features
    const countries = (
      topojson.feature(topoData as any, (topoData as any).objects.world) as any
    ).features;
    const graticule = d3.geoGraticule10();

    land.selectAll('path').data(countries).join('path');

    const clampLat = (v: number) => Math.max(-90, Math.min(90, v));
    const degPerPx = () => 90 / (stateRef.current.r * stateRef.current.zoom);

    function screenPoint(lo: number, la: number): [number, number] | null {
      const p = projection([lo, la]);
      if (!p) return null;
      const rot = projection.rotate();
      const dist = d3.geoDistance([lo, la], [-rot[0], -rot[1]]);
      return dist < Math.PI / 2 - 0.02 ? (p as [number, number]) : null;
    }

    const typedCountries = countriesData as CountryItem[];
    const typedCities = citiesData as CityItem[];

    function drawCountryLabels() {
      const zoom = stateRef.current.zoom;
      // Show country names: larger countries when zoomed out, smaller countries when zoomed in
      let candidateCountries: CountryItem[] = [];
      if (zoom < 2.0) {
        candidateCountries = typedCountries.filter((c) => c.area > 0.035);
      } else if (zoom < 4.5) {
        candidateCountries = typedCountries.filter((c) => c.area > 0.008);
      } else if (zoom < 9.0) {
        candidateCountries = typedCountries.filter((c) => c.area > 0.002);
      } else {
        candidateCountries = typedCountries;
      }

      const showCountries: { c: CountryItem; p: [number, number] }[] = [];
      for (const item of candidateCountries) {
        const p = screenPoint(item.lo, item.la);
        if (!p) continue;
        showCountries.push({ c: item, p });
      }

      countriesGroup
        .selectAll<SVGTextElement, { c: CountryItem; p: [number, number] }>('text')
        .data(showCountries, (d: any) => d.c.id)
        .join('text')
        .attr('class', 'country-lbl')
        .attr('x', (d) => d.p[0])
        .attr('y', (d) => d.p[1])
        .style('font-family', '"PP Telegraf", "Telegraf", "Inter", sans-serif')
        .style('font-weight', '300')
        .style('fill', '#ffffff')
        .style('stroke', 'none')
        .style('font-size', (d) => {
          if (d.c.area > 0.15) return `${Math.min(18, 12 + zoom * 0.8)}px`;
          if (d.c.area > 0.05) return `${Math.min(15, 11 + zoom * 0.6)}px`;
          return `${Math.min(13, 10 + zoom * 0.4)}px`;
        })
        .style('opacity', () => {
          if (zoom > 15) return 0.4;
          if (zoom > 8) return 0.65;
          return 0.85;
        })
        .text((d) => d.c.name);
    }

    function drawCityLabels() {
      const zoom = stateRef.current.zoom;
      // Show prominent floating city badges at all zoom levels, starting with major global hubs like in the reference image
      let candidateCities: CityItem[] = [];
      if (zoom < 1.8) {
        // Show major world hubs like Los Angeles, New York, London, Tokyo, Seoul, Paris, etc.
        candidateCities = typedCities.filter((c) => c.count >= 2 || ['Tokyo', 'Seoul', 'Shanghai', 'Sydney', 'Mumbai', 'Los Angeles', 'New York', 'London', 'Paris', 'Berlin'].includes(c.name));
      } else if (zoom < 4.0) {
        candidateCities = typedCities.filter((c) => c.count >= 2);
      } else if (zoom < 7.0) {
        candidateCities = typedCities.filter((c) => c.count >= 1);
      } else {
        candidateCities = typedCities;
      }

      const showCities: { city: CityItem; p: [number, number] }[] = [];
      const placed: [number, number, number, number][] = [];

      for (const city of candidateCities) {
        const p = screenPoint(city.lo, city.la);
        if (!p) continue;

        const nameText = zoom >= 6 && city.country ? `${city.name}` : city.name;
        const w = Math.max(72, nameText.length * 9 + 36);
        const h = 26;
        const x0 = p[0] - w / 2;
        const y0 = p[1] - 13;

        const collides = placed.some(
          (b) => x0 < b[0] + b[2] + 6 && x0 + w > b[0] - 6 && y0 < b[1] + b[3] + 6 && y0 + h > b[1] - 6
        );
        if (collides) continue;

        placed.push([x0, y0, w, h]);
        showCities.push({ city, p });
      }

      // Draw floating city pills like reference design
      const pillGroups = citiesGroup
        .selectAll<SVGGElement, { city: CityItem; p: [number, number] }>('g.city-pill')
        .data(showCities, (d: any) => d.city.name)
        .join('g')
        .attr('class', 'city-pill')
        .attr('transform', (d) => `translate(${d.p[0]}, ${d.p[1]})`)
        .on('click', (e, d) => {
          e.stopPropagation();
          stopMotion();
          flyTo(d.city.lo, d.city.la, Math.max(stateRef.current.zoom, 3.2));
        });

      pillGroups.selectAll('*').remove();

      pillGroups.each(function (d) {
        const gPill = d3.select(this);
        const nameText = zoom >= 6 && d.city.country ? `${d.city.name}` : d.city.name;

        // Render text first to measure exact rendered bounding box
        const textNode = gPill
          .append('text')
          .attr('text-anchor', 'start')
          .attr('dominant-baseline', 'central')
          .text(nameText);

        let bbox = { width: nameText.length * 9, height: 16 };
        try {
          const domText = textNode.node();
          if (domText) {
            const measured = domText.getBBox();
            if (measured && measured.width > 0) {
              bbox = measured;
            }
          }
        } catch {
          // fallback to approx
        }

        const totalW = Math.max(72, Math.ceil(bbox.width) + 36);
        const totalH = 26;

        // Dark pill background with border inserted before text
        gPill
          .insert('rect', 'text')
          .attr('x', -totalW / 2)
          .attr('y', -totalH / 2)
          .attr('width', totalW)
          .attr('height', totalH);

        // Small indicator square inserted before text
        gPill
          .insert('rect', 'text')
          .attr('class', 'indicator')
          .attr('x', -totalW / 2 + 8)
          .attr('y', -2.5);

        // Position text with generous padding after indicator
        textNode
          .attr('x', -totalW / 2 + 20)
          .attr('y', 0.5);
      });
    }

    function drawDots() {
      const visible = stateRef.current.visible;
      const selected = stateRef.current.selected;

      dots
        .selectAll<SVGCircleElement, Institution>('circle')
        .data(visible, (d: any) => d.n)
        .join('circle')
        .attr('class', (d) => `dot t-${d.t}${selected?.n === d.n ? ' is-selected' : ''}`)
        .attr('r', (d) => (d.s === 'L' ? 11.2 : 5.85))
        .each(function (d) {
          const p = screenPoint(d.lo, d.la);
          d3.select(this)
            .attr('cx', p ? p[0] : 0)
            .attr('cy', p ? p[1] : 0)
            .attr('display', p ? null : 'none');
        });

      dots.selectAll('circle.is-selected').raise();
    }

    function drawLabels() {
      const zoom = stateRef.current.zoom;
      const visible = stateRef.current.visible;
      const selected = stateRef.current.selected;

      const pool =
        zoom >= 3.5
          ? visible.filter((d) => zoom >= 9 || d.s === 'L' || d.n === selected?.n)
          : selected
          ? [selected]
          : [];

      const rank = (d: Institution) => (d.n === selected?.n ? 0 : d.s === 'L' ? 1 : 2);
      const placed: [number, number, number, number][] = [];
      const show: Institution[] = [];

      const sorted = pool.slice().sort((a, b) => rank(a) - rank(b) || a.n.localeCompare(b.n));

      for (const d of sorted) {
        const p = screenPoint(d.lo, d.la);
        if (!p) continue;
        const r = d.s === 'L' ? 14 : 9;
        const x0 = p[0] + r + 6;
        const y0 = p[1] - 8;
        const w = d.n.length * 7 + 4;
        const h = 19;

        const collides = placed.some(
          (b) => x0 < b[0] + b[2] && x0 + w > b[0] && y0 < b[1] + b[3] && y0 + h > b[1]
        );
        if (collides) continue;

        placed.push([x0, y0, w, h]);
        show.push(d);
      }

      labels
        .selectAll<SVGTextElement, Institution>('text')
        .data(show, (d: any) => d.n)
        .join('text')
        .attr('class', (d) => `lbl${selected?.n === d.n ? ' is-selected' : ''}`)
        .text((d) => d.n)
        .each(function (d) {
          const p = screenPoint(d.lo, d.la);
          const r = d.s === 'L' ? 14 : 9;
          d3.select(this)
            .attr('x', p ? p[0] + r + 6 : 0)
            .attr('y', p ? p[1] + 5 : 0)
            .attr('display', p ? null : 'none');
        });
    }

    function drawScale() {
      if (!scalebarRef.current || !scalelabelRef.current) return;
      const R = stateRef.current.r;
      const zoom = stateRef.current.zoom;
      const W = stateRef.current.w;

      const pxPerKm = (R * zoom) / 6371;
      const steps = [20000, 10000, 5000, 2000, 1000, 500, 200, 100, 50, 20, 10, 5, 2, 1];
      const maxPx = Math.min(180, W * 0.3);
      const km = steps.find((k) => k * pxPerKm <= maxPx) || 1;

      scalebarRef.current.style.width = km * pxPerKm + 'px';
      scalelabelRef.current.textContent =
        km >= 1000 ? (km / 1000).toLocaleString() + ',000 km' : km + ' km';
    }

    function draw() {
      const sph = pathGenerator({ type: 'Sphere' } as any);
      sphere.attr('d', sph);
      grat.attr('d', stateRef.current.zoom < 12 ? pathGenerator(graticule as any) : null);
      land.selectAll('path').attr('d', pathGenerator as any);
      shade.attr('d', sph);
      rimHighlight.attr('d', sph);
      atmosphereGlow.attr('d', sph);
      drawCountryLabels();
      drawDots();
      drawLabels();
      drawCityLabels();
      citiesGroup.raise();
      drawScale();
    }

    function size() {
      const rect = wrapEl.getBoundingClientRect();
      const W = Math.max(200, rect.width);
      const H = Math.max(200, rect.height);
      const R = Math.min(W, H) / 2 - 12;

      stateRef.current.w = W;
      stateRef.current.h = H;
      stateRef.current.r = R;

      svg.attr('width', W).attr('height', H).attr('viewBox', `0 0 ${W} ${H}`);
      projection.translate([W / 2, H / 2]).scale(R * stateRef.current.zoom);
      draw();
    }

    function zoomAt(z: number, pt: [number, number] | null) {
      z = Math.max(ZMIN, Math.min(ZMAX, z));
      const geo = pt ? projection.invert?.(pt) : null;
      stateRef.current.zoom = z;
      projection.scale(stateRef.current.r * z);

      if (geo && isFinite(geo[0]) && isFinite(geo[1])) {
        for (let i = 0; i < 3; i++) {
          const q = projection(geo);
          if (!q) break;
          const k = degPerPx();
          const r = projection.rotate();
          projection.rotate([
            r[0] + (pt![0] - q[0]) * k,
            clampLat(r[1] - (pt![1] - q[1]) * k),
          ]);
        }
      }
      draw();
    }

    // Spin animation
    let lastTime: number | null = null;
    let animId: number | null = null;

    function frame(t: number) {
      if (!stateRef.current.spinning) {
        lastTime = null;
        return;
      }
      if (lastTime != null) {
        const r = projection.rotate();
        r[0] += (t - lastTime) * 0.004;
        projection.rotate(r);
        draw();
      }
      lastTime = t;
      animId = requestAnimationFrame(frame);
    }

    function setSpin(on: boolean) {
      stateRef.current.spinning = on;
      setIsSpinning(on);
      if (on) {
        lastTime = null;
        animId = requestAnimationFrame(frame);
      }
    }

    let inertiaId: number | null = null;
    function stopInertia() {
      if (inertiaId) {
        cancelAnimationFrame(inertiaId);
        inertiaId = null;
      }
    }

    function stopMotion() {
      setSpin(false);
      stopInertia();
      d3.select(svgEl).interrupt();
    }

    function animateZoom(z: number, pt: [number, number] | null, ms: number) {
      stopMotion();
      const z0 = stateRef.current.zoom;
      const z1 = Math.max(ZMIN, Math.min(ZMAX, z));
      d3.transition()
        .duration(stateRef.current.reducedMotion ? 0 : ms)
        .ease(d3.easeCubicOut)
        .tween('zoom', () => (t: number) => {
          zoomAt(z0 * Math.pow(z1 / z0, t), pt);
        });
    }

    function flyTo(lo: number, la: number, z: number) {
      stopMotion();
      const a = projection.rotate();
      const b: [number, number] = [-lo, -la];
      let dl = b[0] - a[0];
      dl = ((dl + 540) % 360) - 180;
      b[0] = a[0] + dl;

      const ip = d3.interpolate(a, b);
      const z0 = stateRef.current.zoom;
      const z1 = Math.max(ZMIN, Math.min(ZMAX, z));
      const far = Math.min(Math.abs(dl) + Math.abs(b[1] - a[1]), 180) / 180;
      const zmid = Math.min(z0, z1, Math.max(ZMIN, 1.4 + (1 - far) * Math.min(z0, z1)));
      const lz0 = Math.log(z0);
      const lzm = Math.log(zmid);
      const lz1 = Math.log(z1);

      d3.transition()
        .duration(stateRef.current.reducedMotion ? 0 : 900 + 600 * far)
        .ease(d3.easeCubicInOut)
        .tween('fly', () => (t: number) => {
          projection.rotate(ip(t));
          const lz =
            t < 0.5 ? lz0 + (lzm - lz0) * (t / 0.5) : lzm + (lz1 - lzm) * ((t - 0.5) / 0.5);
          stateRef.current.zoom = Math.exp(lz);
          projection.scale(stateRef.current.r * stateRef.current.zoom);
          draw();
        });
    }

    // Pointer event handling
    const pointers = new Map<number, [number, number]>();
    let r0: [number, number, number] | null = null;
    let p0: [number, number] | null = null;
    let moves: [number, number, number][] = [];
    let pinch: { d: number; mid: [number, number] } | null = null;

    function local(e: PointerEvent | MouseEvent): [number, number] {
      const b = svgEl.getBoundingClientRect();
      return [e.clientX - b.left, e.clientY - b.top];
    }

    function pinchState() {
      const [pA, pB] = [...pointers.values()];
      return {
        d: Math.hypot(pA[0] - pB[0], pA[1] - pB[1]),
        mid: [(pA[0] + pB[0]) / 2, (pA[1] + pB[1]) / 2] as [number, number],
      };
    }

    const onPointerDown = (e: PointerEvent) => {
      if (e.button !== 0 && e.pointerType === 'mouse') return;
      try {
        svgEl.setPointerCapture(e.pointerId);
      } catch {}
      pointers.set(e.pointerId, local(e));
      stopMotion();

      if (pointers.size === 1) {
        r0 = projection.rotate();
        p0 = local(e);
        moves = [[performance.now(), ...p0]];
        svg.classed('dragging', true);
        pinch = null;
      } else if (pointers.size === 2) {
        pinch = pinchState();
        r0 = null;
      }
    };

    const onPointerMove = (e: PointerEvent) => {
      if (!pointers.has(e.pointerId)) return;
      pointers.set(e.pointerId, local(e));

      if (pointers.size === 1 && r0 && p0) {
        const p = local(e);
        const k = degPerPx();
        projection.rotate([
          r0[0] + (p[0] - p0[0]) * k,
          clampLat(r0[1] - (p[1] - p0[1]) * k),
        ]);
        moves.push([performance.now(), p[0], p[1]]);
        if (moves.length > 6) moves.shift();
        draw();
      } else if (pointers.size === 2 && pinch) {
        const ps = pinchState();
        const k = degPerPx();
        const r = projection.rotate();
        projection.rotate([
          r[0] + (ps.mid[0] - pinch.mid[0]) * k,
          clampLat(r[1] - (ps.mid[1] - pinch.mid[1]) * k),
        ]);
        zoomAt(stateRef.current.zoom * (ps.d / pinch.d), ps.mid);
        pinch = ps;
      }
    };

    const endPointer = (e: PointerEvent) => {
      if (!pointers.has(e.pointerId)) return;
      pointers.delete(e.pointerId);

      if (pointers.size === 0) {
        svg.classed('dragging', false);
        if (r0 && moves.length > 1 && !stateRef.current.reducedMotion) {
          const a = moves[0];
          const b = moves[moves.length - 1];
          const dt = Math.max(1, b[0] - a[0]);
          let vx = (b[1] - a[1]) / dt;
          let vy = (b[2] - a[2]) / dt;

          if (Math.hypot(vx, vy) > 0.08) {
            let prev = performance.now();
            const step = (now: number) => {
              const el = now - prev;
              prev = now;
              const k = degPerPx();
              const r = projection.rotate();
              projection.rotate([r[0] + vx * el * k, clampLat(r[1] - vy * el * k)]);
              draw();
              vx *= Math.pow(0.94, el / 16);
              vy *= Math.pow(0.94, el / 16);
              if (Math.hypot(vx, vy) > 0.01) {
                inertiaId = requestAnimationFrame(step);
              } else {
                inertiaId = null;
              }
            };
            inertiaId = requestAnimationFrame(step);
          }
        }
        r0 = null;
        pinch = null;
      } else if (pointers.size === 1) {
        const [, p] = [...pointers.entries()][0];
        r0 = projection.rotate();
        p0 = p;
        moves = [[performance.now(), ...p]];
        pinch = null;
      }
    };

    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      stopMotion();
      const f = Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0018));
      zoomAt(stateRef.current.zoom * f, local(e));
    };

    const onDblClick = (e: MouseEvent) => {
      e.preventDefault();
      animateZoom(stateRef.current.zoom * 2, local(e), 300);
    };

    const onKeyDown = (e: KeyboardEvent) => {
      const step = 12 / stateRef.current.zoom;
      const r = projection.rotate();
      const map: Record<string, [number, number]> = {
        ArrowLeft: [step, 0],
        ArrowRight: [-step, 0],
        ArrowUp: [0, step],
        ArrowDown: [0, -step],
      };

      if (map[e.key]) {
        e.preventDefault();
        stopMotion();
        projection.rotate([r[0] + map[e.key][0], clampLat(r[1] + map[e.key][1])]);
        draw();
      } else if (e.key === '+' || e.key === '=') {
        e.preventDefault();
        animateZoom(stateRef.current.zoom * 1.6, [stateRef.current.w / 2, stateRef.current.h / 2], 250);
      } else if (e.key === '-' || e.key === '_') {
        e.preventDefault();
        animateZoom(stateRef.current.zoom / 1.6, [stateRef.current.w / 2, stateRef.current.h / 2], 250);
      } else if (e.key === 'Escape') {
        onSelect(null);
      }
    };

    // Attach interaction listeners to SVG
    svgEl.addEventListener('pointerdown', onPointerDown);
    svgEl.addEventListener('pointermove', onPointerMove);
    svgEl.addEventListener('pointerup', endPointer);
    svgEl.addEventListener('pointercancel', endPointer);
    svgEl.addEventListener('lostpointercapture', endPointer);
    svgEl.addEventListener('wheel', onWheel, { passive: false });
    svgEl.addEventListener('dblclick', onDblClick);
    svgEl.addEventListener('keydown', onKeyDown);

    // Tooltip and Dot Click
    dots
      .on('mouseover', (e: MouseEvent) => {
        const target = e.target as SVGElement;
        const d = d3.select<SVGElement, Institution>(target).datum();
        if (!d || !tipEl) return;
        tipEl.innerHTML = `<strong>${d.n}</strong><small>${d.c} · ${TIER[d.t].l}</small>`;
        tipEl.classList.add('on');
      })
      .on('mousemove', (e: MouseEvent) => {
        if (!tipEl) return;
        const [x, y] = d3.pointer(e, wrapEl);
        tipEl.style.left = `${x}px`;
        tipEl.style.top = `${y}px`;
      })
      .on('mouseout', () => {
        if (tipEl) tipEl.classList.remove('on');
      })
      .on('click', (e: MouseEvent) => {
        const target = e.target as SVGElement;
        const d = d3.select<SVGElement, Institution>(target).datum();
        if (d) {
          onSelect(d, false);
        }
      });

    // Save refs for control buttons and updates
    d3Refs.current = {
      svg,
      projection,
      pathGenerator,
      sphere,
      atmosphereGlow,
      rimHighlight,
      grat,
      land,
      shade,
      countriesGroup,
      citiesGroup,
      dots,
      labels,
      draw,
      flyTo,
      animateZoom,
      stopMotion,
    };

    // Start auto spin if motion is allowed
    if (!reduced) {
      animId = requestAnimationFrame(frame);
    }

    // Initial resize
    size();

    // Resize observer
    let ro: ResizeObserver | null = null;
    if (window.ResizeObserver) {
      ro = new ResizeObserver(size);
      ro.observe(wrapEl);
    }
    window.addEventListener('resize', size);

    return () => {
      if (animId) cancelAnimationFrame(animId);
      if (inertiaId) cancelAnimationFrame(inertiaId);
      if (ro) ro.disconnect();
      window.removeEventListener('resize', size);
      svgEl.removeEventListener('pointerdown', onPointerDown);
      svgEl.removeEventListener('pointermove', onPointerMove);
      svgEl.removeEventListener('pointerup', endPointer);
      svgEl.removeEventListener('pointercancel', endPointer);
      svgEl.removeEventListener('lostpointercapture', endPointer);
      svgEl.removeEventListener('wheel', onWheel);
      svgEl.removeEventListener('dblclick', onDblClick);
      svgEl.removeEventListener('keydown', onKeyDown);
    };
  }, []);

  // Re-draw when visibleInstitutions or selected change
  useEffect(() => {
    if (d3Refs.current) {
      d3Refs.current.draw();
    }
  }, [visibleInstitutions, selected]);

  // When selected changes and we should focus on it
  const prevSelectedRef = useRef<Institution | null>(null);
  useEffect(() => {
    if (selected && selected !== prevSelectedRef.current && d3Refs.current) {
      d3Refs.current.flyTo(selected.lo, selected.la, Math.max(stateRef.current.zoom, 6));
    }
    prevSelectedRef.current = selected;
  }, [selected]);

  // Zoom control buttons
  const handleZoomIn = () => {
    if (d3Refs.current) {
      const W = stateRef.current.w;
      const H = stateRef.current.h;
      d3Refs.current.animateZoom(stateRef.current.zoom * 1.6, [W / 2, H / 2], 250);
    }
  };

  const handleZoomOut = () => {
    if (d3Refs.current) {
      const W = stateRef.current.w;
      const H = stateRef.current.h;
      d3Refs.current.animateZoom(stateRef.current.zoom / 1.6, [W / 2, H / 2], 250);
    }
  };

  const handleZoomReset = () => {
    if (d3Refs.current) {
      d3Refs.current.flyTo(-HOME[0], -HOME[1], 1);
    }
  };

  const handleToggleSpin = () => {
    if (d3Refs.current) {
      const nextSpin = !isSpinning;
      stateRef.current.spinning = nextSpin;
      setIsSpinning(nextSpin);
      if (nextSpin) {
        d3Refs.current.draw();
      }
    }
  };

  // Search input handling
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSearchQuery(val);
    const q = val.trim().toLowerCase();
    if (!q) {
      setSearchResults([]);
      setShowResults(false);
      return;
    }

    const hit = allInstitutions.filter((d) => (d.n + ' ' + d.c).toLowerCase().includes(q));
    hit.sort(
      (a, b) =>
        Number(b.n.toLowerCase().startsWith(q)) - Number(a.n.toLowerCase().startsWith(q)) ||
        a.n.localeCompare(b.n)
    );
    setSearchResults(hit.slice(0, 8));
    setShowResults(true);
  };

  const handleSelectSearchResult = (inst: Institution) => {
    setSearchQuery(inst.n);
    setShowResults(false);
    onEnsureVisible(inst);
    onSelect(inst, true);
  };

  const handleSearchKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      if (searchResults.length > 0) {
        handleSelectSearchResult(searchResults[0]);
      }
    } else if (e.key === 'Escape') {
      setShowResults(false);
    }
  };

  // Click outside search
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('.searchbox')) {
        setShowResults(false);
      }
    };
    document.addEventListener('pointerdown', handleClickOutside);
    return () => document.removeEventListener('pointerdown', handleClickOutside);
  }, []);

  return (
    <div className="mapwrap" ref={wrapRef}>
      <div id="map" ref={mapContainerRef} />

      <div className="searchbox">
        <input
          id="q"
          ref={searchInputRef}
          type="search"
          placeholder="Search institutions and cities"
          aria-label="Search institutions and cities"
          autoComplete="off"
          value={searchQuery}
          onChange={handleSearchChange}
          onFocus={() => searchResults.length > 0 && setShowResults(true)}
          onKeyDown={handleSearchKeyDown}
        />
        {showResults && searchResults.length > 0 && (
          <ul className="results" id="results">
            {searchResults.map((d) => (
              <li key={d.n}>
                <button
                  type="button"
                  style={{ '--c': TIER[d.t].c } as React.CSSProperties}
                  onClick={() => handleSelectSearchResult(d)}
                >
                  <span className="dot" />
                  <span>
                    {d.n}
                    <span className="where">{d.c}</span>
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Side of map title & view toggle matching user screenshot */}
      <div className="map-side-brand">
        <h2 className="brand-name">CULTURE ATLAS</h2>
        <div className="view-pill-toggle" role="group" aria-label="Map view mode">
          <button
            type="button"
            className={`pill-btn ${activeView === 'globe' ? 'active' : ''}`}
            onClick={() => onToggleView && onToggleView('globe')}
            aria-pressed={activeView === 'globe'}
          >
            GLOBE VIEW
          </button>
          <span className="pill-indicator" />
          <button
            type="button"
            className={`pill-btn ${activeView === 'list' ? 'active' : ''}`}
            onClick={() => onToggleView && onToggleView('list')}
            aria-pressed={activeView === 'list'}
          >
            CITY LIST
          </button>
        </div>
      </div>

      <div className="tools">
        <button
          id="zin"
          type="button"
          aria-label="Zoom in"
          title="Zoom in"
          onClick={handleZoomIn}
        >
          +
        </button>
        <button
          id="zout"
          type="button"
          aria-label="Zoom out"
          title="Zoom out"
          onClick={handleZoomOut}
        >
          &minus;
        </button>
        <button
          id="zreset"
          type="button"
          aria-label="Reset the view"
          title="Reset the view"
          onClick={handleZoomReset}
        >
          &#9678;
        </button>
        <button
          id="spin"
          type="button"
          aria-label="Spin the globe"
          aria-pressed={isSpinning}
          title="Spin"
          onClick={handleToggleSpin}
        >
          &#8635;
        </button>
      </div>

      <div className="scalebar" aria-hidden="true">
        <div className="bar" id="scalebar" ref={scalebarRef} />
        <span id="scalelabel" ref={scalelabelRef} />
      </div>

      <div id="tip" ref={tipRef} role="tooltip" />
    </div>
  );
};
