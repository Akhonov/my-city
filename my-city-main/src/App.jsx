import React, { startTransition, useEffect, useMemo, useState } from 'react';
import {
  Activity,
  Building2,
  Briefcase,
  Factory,
  HeartPulse,
  Leaf,
  MapPinned,
  School,
  ShieldCheck,
  TramFront,
  Trees,
  Zap,
  MapPin,
} from 'lucide-react';
import Map, { Marker, NavigationControl } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import './App.css';

// Импортируем твои данные и логику
import {
  DEVELOPMENT_SITES,
  DEVELOPMENT_TYPES,
  DISTRICTS,
  STORY_FACTS,
} from './cityModel';
import { simulateCity } from './simulation';

const STORAGE_KEY = 'almaty-twin-city:placements';

function loadPlacements() {
  if (typeof window === 'undefined') {
    return {};
  }

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return {};
    }

    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      return {};
    }

    return Object.fromEntries(
      Object.entries(parsed).filter(([siteId, typeId]) =>
        DEVELOPMENT_SITES.some((site) => site.id === siteId) &&
        typeof typeId === 'string' &&
        DEVELOPMENT_TYPES[typeId]
      )
    );
  } catch {
    return {};
  }
}

function normalizeSimulationResponse(data, fallback) {
  if (!data || typeof data !== 'object') {
    return fallback;
  }

  return {
    ...fallback,
    ...data,
    metrics: { ...fallback.metrics, ...(data.metrics ?? {}) },
    baseline: { ...fallback.baseline, ...(data.baseline ?? {}) },
    deltas: { ...fallback.deltas, ...(data.deltas ?? {}) },
    warnings: Array.isArray(data.warnings) ? data.warnings : fallback.warnings,
    opportunities: Array.isArray(data.opportunities) ? data.opportunities : fallback.opportunities,
    placements: Array.isArray(data.placements) ? data.placements : fallback.placements,
    rankedSites: Array.isArray(data.rankedSites) ? data.rankedSites : fallback.rankedSites,
    score: Number.isFinite(data.score) ? data.score : fallback.score,
    summary: typeof data.summary === 'string' ? data.summary : fallback.summary,
  };
}

// --- НАСТРОЙКИ КАРТЫ ---
const MAP_CONFIG = {
  center: { lng: 76.9415, lat: 43.2551 }, // Центр Алматы (Абая-Назарбаева)
  scale: 0.0006 // Коэффициент пересчета твоих координат в GPS
};

const METRIC_META = {
  air: { label: 'Воздух', icon: <Leaf size={16} />, goodHigh: true },
  traffic: { label: 'Трафик', icon: <Activity size={16} />, goodHigh: false },
  green: { label: 'Озеленение', icon: <Trees size={16} />, goodHigh: true },
  housing: { label: 'Жилье', icon: <Building2 size={16} />, goodHigh: true },
  economy: { label: 'Экономика', icon: <Factory size={16} />, goodHigh: true },
  social: { label: 'Соцсервисы', icon: <HeartPulse size={16} />, goodHigh: true },
  utility: { label: 'Сети', icon: <Zap size={16} />, goodHigh: false },
  resilience: { label: 'Устойчивость', icon: <ShieldCheck size={16} />, goodHigh: true },
};

const TYPE_ICONS = {
  none: MapPin,
  residential: Building2,
  mixedUse: Briefcase,
  park: Trees,
  school: School,
  hospital: HeartPulse,
  transit: TramFront,
  energy: Zap,
};

// --- ВСПОМОГАТЕЛЬНЫЕ КОМПОНЕНТЫ ---
function MetricCard({ metricKey, value, delta }) {
  const meta = METRIC_META[metricKey];
  const improved = meta.goodHigh ? delta > 0 : delta < 0;
  const tone = delta === 0 ? 'neutral' : (improved ? 'good' : 'bad');

  return (
    <article className={`metric-card metric-card--${tone}`}>
      <div className="metric-card__header">
        <span className="metric-card__label">{meta.icon}{meta.label}</span>
        <strong>{value}</strong>
      </div>
      <div className="metric-card__bar">
        <span style={{ width: `${Math.max(6, value)}%` }} />
      </div>
      <p className="metric-card__delta">
        {delta > 0 ? '+' : ''}{delta} {metricKey === 'traffic' ? 'load' : 'pts'}
      </p>
    </article>
  );
}

function RealCityMap({ placements, selectedSiteId, activeTypeId, onSiteSelect, onBuildSite }) {
  // Функция превращения [x, y] из cityModel в [lng, lat]
  const project = (pos) => {
    if (!pos) return [MAP_CONFIG.center.lng, MAP_CONFIG.center.lat];
    return [
      MAP_CONFIG.center.lng + pos[0] * MAP_CONFIG.scale * 1.5, // Немного растягиваем по горизонтали
      MAP_CONFIG.center.lat - pos[1] * MAP_CONFIG.scale // Инвертируем Y, так как в картах широта растет вверх
    ];
  };

  const onMapLoad = (e) => {
    const map = e.target;
    if (!map.getLayer('3d-buildings')) {
      map.addLayer({
        id: '3d-buildings',
        source: 'maptiler_planet',
        'source-layer': 'building',
        type: 'fill-extrusion',
        minzoom: 13,
        paint: {
          'fill-extrusion-color': '#1e293b',
          'fill-extrusion-height': ['*', ['coalesce', ['get', 'render_height'], 0], 1.2],
          'fill-extrusion-base': ['coalesce', ['get', 'render_min_height'], 0],
          'fill-extrusion-opacity': 0.6
        }
      });
    }
  };

  return (
    <Map
      initialViewState={{
        longitude: MAP_CONFIG.center.lng,
        latitude: MAP_CONFIG.center.lat,
        zoom: 13.8,
        pitch: 60,
        bearing: -15
      }}
      mapStyle="https://api.maptiler.com/maps/dataviz-dark/style.json?key=NXx3d6NShBcON5h53Scs"
      style={{ width: '100%', height: '100%' }}
      onLoad={onMapLoad}
    >
      <NavigationControl position="bottom-right" />

      {DEVELOPMENT_SITES.map((site) => {
        const [lng, lat] = project(site.position);
        const isSelected = selectedSiteId === site.id;
        const placedTypeId = placements[site.id];
        const typeInfo = placedTypeId ? DEVELOPMENT_TYPES[placedTypeId] : null;
        const markerColor = typeInfo ? typeInfo.color : '#38bdf8';
        const Icon = placedTypeId ? (TYPE_ICONS[placedTypeId] || Building2) : MapPin;

        return (
          <Marker
            key={site.id}
            longitude={lng}
            latitude={lat}
            anchor="bottom"
            onClick={(e) => {
              e.originalEvent.stopPropagation();
              onSiteSelect(site.id);
            }}
          >
            {isSelected && <div className="marker-pulse-ring" style={{ border: `2px solid ${markerColor}` }} />}
            <div
              className={`map-marker ${isSelected ? 'map-marker--selected' : ''}`}
              style={{ backgroundColor: markerColor, boxShadow: isSelected ? `0 0 20px ${markerColor}` : '' }}
            >
              <Icon color="#fff" size={18} />
            </div>
            <div className="map-marker-label">{site.name}</div>
          </Marker>
        );
      })}
    </Map>
  );
}

// --- ГЛАВНЫЙ КОМПОНЕНТ APP ---
export default function App() {
  const [selectedTypeId, setSelectedTypeId] = useState('transit');
  const [selectedSiteId, setSelectedSiteId] = useState(DEVELOPMENT_SITES[0].id);
  const [placements, setPlacements] = useState(loadPlacements);
  const [remoteSimulation, setRemoteSimulation] = useState(null);
  const [backendStatus, setBackendStatus] = useState('local');

  const localSimulation = useMemo(() => simulateCity(placements), [placements]);
  const simulation = useMemo(
    () => normalizeSimulationResponse(remoteSimulation, localSimulation),
    [remoteSimulation, localSimulation]
  );
  const selectedSite = DEVELOPMENT_SITES.find((s) => s.id === selectedSiteId) || DEVELOPMENT_SITES[0];

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(placements));
  }, [placements]);

  useEffect(() => {
    const controller = new AbortController();
    async function syncScenario() {
      try {
        const response = await fetch('/api/simulate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            placements: Object.entries(placements).map(([site_id, type_id]) => ({ site_id, type_id })),
          }),
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error(`Simulation request failed with ${response.status}`);
        }
        const data = await response.json();
        setRemoteSimulation(normalizeSimulationResponse(data, localSimulation));
        setBackendStatus('connected');
      } catch {
        setRemoteSimulation(null);
        setBackendStatus('local');
      }
    }
    syncScenario();
    return () => controller.abort();
  }, [placements]);

  const applyPlacement = (siteId) => {
    startTransition(() => {
      setPlacements((prev) => {
        const next = { ...prev };
        if (selectedTypeId === 'none') {
          delete next[siteId];
        } else {
          next[siteId] = selectedTypeId;
        }
        return next;
      });
    });
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Digital Twin of Almaty / Hackathon 2026</p>
          <h1>ALMATY TWIN CITY</h1>
        </div>
        <div className="topbar__status">
          <span className={`status-pill status-pill--${backendStatus}`}>
            {backendStatus === 'connected' ? 'Backend Online' : 'Local Simulation'}
          </span>
          <strong className="score-card">City Score: {simulation.score}/100</strong>
        </div>
      </header>

      <main className="dashboard">
        {/* Левая панель */}
        <aside className="panel">
          <section className="panel-card hero-card">
            <span className="eyebrow">Summary</span>
            <p>{simulation.summary}</p>
            <ul className="fact-list">
              {STORY_FACTS.map((f, i) => <li key={i}>{f}</li>)}
            </ul>
          </section>

          <section className="metrics-grid">
            {Object.keys(METRIC_META).map((key) => (
              <MetricCard
                key={key}
                metricKey={key}
                value={simulation.metrics[key]}
                delta={simulation.deltas[key]}
              />
            ))}
          </section>

          <section className="panel-card districts-section">
             <div className="section-heading"><span className="eyebrow">Districts</span><MapPinned size={16}/></div>
             <div className="district-list">
                {DISTRICTS.map(d => (
                  <div key={d.id} className="district-item">
                    <div className="district-swatch" style={{backgroundColor: d.color}} />
                    <div><strong>{d.name}</strong><p>{d.summary}</p></div>
                  </div>
                ))}
             </div>
          </section>
        </aside>

        {/* Карта */}
        <section className="scene-column">
          <div className="scene-frame">
            <RealCityMap
              placements={placements}
              selectedSiteId={selectedSiteId}
              onSiteSelect={setSelectedSiteId}
            />
            <div className="scene-overlay scene-overlay--top">
              <strong>3D GIS Simulation</strong>
              <span>Нажмите на маркер, затем кнопку «Разместить» справа</span>
            </div>
          </div>

          <section className="toolbar">
            {Object.values(DEVELOPMENT_TYPES).map((type) => (
              <button
                key={type.id}
                className={`tool-chip ${selectedTypeId === type.id ? 'tool-chip--active' : ''}`}
                onClick={() => setSelectedTypeId(type.id)}
              >
                <span className="tool-chip__swatch" style={{ backgroundColor: type.color }} />
                <span>{type.shortLabel}</span>
              </button>
            ))}
            <button
              className="tool-chip tool-chip--ghost"
              onClick={() => {
                setPlacements({});
                setRemoteSimulation(null);
              }}
            >
              Reset
            </button>
          </section>
        </section>

        {/* Правая панель */}
        <aside className="panel">
          <section className="panel-card">
            <div className="section-heading">
              <span className="eyebrow">Site Analysis</span>
              <strong>{selectedSite.name}</strong>
            </div>
            <p className="site-description">{selectedSite.recommendation}</p>
            <div className="site-stats">
               <span>Transit: {Math.round(selectedSite.context.transitAccess * 100)}%</span>
               <span>Green: {Math.round(selectedSite.context.greenDeficit * 100)}%</span>
            </div>
            <div className="action-stack">
              <button className="primary-action" onClick={() => applyPlacement(selectedSite.id)}>
                Разместить: {DEVELOPMENT_TYPES[selectedTypeId]?.label}
              </button>
              <button className="secondary-action" onClick={() => {
                setSelectedTypeId('none');
                applyPlacement(selectedSite.id);
              }}>Очистить участок</button>
            </div>
          </section>

          <section className="panel-card">
            <span className="eyebrow">AI Insights</span>
            <div className="insight-block">
              {simulation.warnings.map((w, i) => <p key={i} className="warning-text">{w}</p>)}
              {simulation.opportunities.map((o, i) => <p key={i} className="positive-text">{o}</p>)}
              {simulation.warnings.length === 0 && <p className="positive-text">Критических рисков не обнаружено.</p>}
            </div>
          </section>

          <section className="panel-card">
            <span className="eyebrow">Recommendations</span>
            <div className="recommendation-list">
              {simulation.rankedSites.slice(0, 3).map((item) => (
                <button key={item.siteId} className="recommendation-item" onClick={() => setSelectedSiteId(item.siteId)}>
                  <div><strong>{item.siteName}</strong><span>{item.suggestedTypeLabel}</span></div>
                  <b>Suitability: {item.suitability}%</b>
                </button>
              ))}
            </div>
          </section>
        </aside>
      </main>
    </div>
  );
}
