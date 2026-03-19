import React, { startTransition, useEffect, useMemo, useState } from 'react';
import {
  Activity, Building2, Briefcase, Factory, HeartPulse, Leaf, MapPinned,
  School, ShieldCheck, TramFront, Trees, Zap, MapPin, Coins, Globe, Clock, Trash2
} from 'lucide-react';
import Map, { Marker, NavigationControl } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import './App.css';
import { API_BASE_URL } from './api';
import AuthModal from './components/AuthModal';
import ChatWindow from './components/ChatWindow';

import {
  DEVELOPMENT_SITES, DEVELOPMENT_TYPES, DISTRICTS, STORY_FACTS,
} from './cityModel';
import { simulateCity } from './simulation';

const STORAGE_KEY = 'almaty-twin-city:placements';
const BONUS_KEY = 'almaty-twin-city:bonuses';
const LANG_KEY = 'almaty-twin-city:lang';
const CUSTOM_SITES_KEY = 'almaty-twin-city:custom-sites';

const TRANSLATIONS = {
  ru: {
    subtitle: 'Цифровой двойник Алматы / Хакатон 2026',
    backendOnline: 'Бэкенд подключен', localSim: 'Локальная симуляция',
    cityScore: 'Рейтинг города', summaryTitle: 'Сводка', districtsTitle: 'Районы',
    mapTitle: '3D ГИС Симуляция', mapSubtitle: 'Кликайте в любое место на карте',
    btnReset: 'Сброс', confirmReset: 'Очистить все застройки и сбросить бонусы?',
    siteAnalysis: 'Анализ участка', btnBuild: 'Разместить:', btnClear: 'Очистить объект',
    btnDeletePoint: 'Удалить маркер',
    aiInsights: 'ИИ Анализ', noRisks: 'Критических рисков не обнаружено.',
    recommendations: 'Рекомендации', suitability: 'Совместимость:', bonusEarned: 'EcoCoins получено!',
    loading: 'Загрузка данных...',
    metric_air: 'Воздух', metric_traffic: 'Трафик', metric_green: 'Озеленение',
    metric_housing: 'Жилье', metric_economy: 'Экономика', metric_social: 'Соцсервисы',
    metric_utility: 'Сети', metric_resilience: 'Устойчивость', pts: 'балл', load: 'нагр.',
    customZone: 'Новая зона', customRec: 'Пользовательский участок для застройки.',
    timeMachine: 'Прогноз в будущее', year: 'Год:'
  },
  kk: {
    subtitle: 'Алматының цифрлық егізі / Хакатон 2026',
    backendOnline: 'Бэкенд қосылған', localSim: 'Жергілікті симуляция',
    cityScore: 'Қала рейтингі', summaryTitle: 'Түйіндеме', districtsTitle: 'Аудандар',
    mapTitle: '3D ГИС Симуляция', mapSubtitle: 'Картаның кез келген жерін басыңыз',
    btnReset: 'Қалпына келтіру', confirmReset: 'Барлық құрылыстарды жойып, бонустарды нөлдеу керек пе?',
    siteAnalysis: 'Аумақ анализі', btnBuild: 'Орналастыру:', btnClear: 'Нысанды тазарту',
    btnDeletePoint: 'Маркерді өшіру',
    aiInsights: 'ЖИ Анализі', noRisks: 'Критикалық тәуекелдер анықталған жоқ.',
    recommendations: 'Ұсыныстар', suitability: 'Сәйкестігі:', bonusEarned: 'EcoCoins алынды!',
    loading: 'Деректер жүктелуде...',
    metric_air: 'Ауа сапасы', metric_traffic: 'Кептеліс', metric_green: 'Көгалдандыру',
    metric_housing: 'Тұрғын үй', metric_economy: 'Экономика', metric_social: 'Әлеуметтік',
    metric_utility: 'Желілер', metric_resilience: 'Тұрақтылық', pts: 'ұпай', load: 'жүктеме',
    customZone: 'Жаңа аймақ', customRec: 'Құрылысқа арналған пайдаланушы учаскесі.',
    timeMachine: 'Болашаққа болжам', year: 'Жыл:'
  },
  en: {
    subtitle: 'Digital Twin of Almaty / Hackathon 2026',
    backendOnline: 'Backend Online', localSim: 'Local Simulation',
    cityScore: 'City Score', summaryTitle: 'Summary', districtsTitle: 'Districts',
    mapTitle: '3D GIS Simulation', mapSubtitle: 'Click anywhere on the map to build',
    btnReset: 'Reset', confirmReset: 'Clear all placements and reset bonuses?',
    siteAnalysis: 'Site Analysis', btnBuild: 'Build:', btnClear: 'Clear object',
    btnDeletePoint: 'Delete marker',
    aiInsights: 'AI Insights', noRisks: 'No critical risks detected.',
    recommendations: 'Recommendations', suitability: 'Suitability:', bonusEarned: 'EcoCoins received!',
    loading: 'Loading data...',
    metric_air: 'Air Quality', metric_traffic: 'Traffic', metric_green: 'Greenery',
    metric_housing: 'Housing', metric_economy: 'Economy', metric_social: 'Social',
    metric_utility: 'Utilities', metric_resilience: 'Resilience', pts: 'pts', load: 'load',
    customZone: 'Custom Zone', customRec: 'User-defined development site.',
    timeMachine: 'Future Forecast', year: 'Year:'
  }
};

function loadJSON(key, fallback) {
  if (typeof window === 'undefined') return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch { return fallback; }
}

const MAP_CONFIG = { center: { lng: 76.9415, lat: 43.2551 }, scale: 0.0006 };

const METRIC_META = {
  air: { icon: <Leaf size={16} />, goodHigh: true }, traffic: { icon: <Activity size={16} />, goodHigh: false },
  green: { icon: <Trees size={16} />, goodHigh: true }, housing: { icon: <Building2 size={16} />, goodHigh: true },
  economy: { icon: <Factory size={16} />, goodHigh: true }, social: { icon: <HeartPulse size={16} />, goodHigh: true },
  utility: { icon: <Zap size={16} />, goodHigh: false }, resilience: { icon: <ShieldCheck size={16} />, goodHigh: true },
};

const TYPE_ICONS = {
  none: MapPin, residential: Building2, mixedUse: Briefcase,
  park: Trees, school: School, hospital: HeartPulse,
  transit: TramFront, energy: Zap,
};

function MetricCard({ metricKey, value, delta, t }) {
  const meta = METRIC_META[metricKey];
  const improved = meta.goodHigh ? delta > 0 : delta < 0;
  const tone = delta === 0 ? 'neutral' : (improved ? 'good' : 'bad');
  return (
    <article className={`metric-card metric-card--${tone}`}>
      <div className="metric-card__header">
        <span className="metric-card__label">{meta.icon}{t(`metric_${metricKey}`)}</span>
        <strong>{Math.round(value)}</strong>
      </div>
      <div className="metric-card__bar"><span style={{ width: `${Math.max(6, value)}%` }} /></div>
      <p className="metric-card__delta">{delta > 0 ? '+' : ''}{Math.round(delta)} {metricKey === 'traffic' ? t('load') : t('pts')}</p>
    </article>
  );
}

export default function App() {
  const [selectedTypeId, setSelectedTypeId] = useState('transit');
  const [placements, setPlacements] = useState(() => loadJSON(STORAGE_KEY, {}));
  const [customSites, setCustomSites] = useState(() => loadJSON(CUSTOM_SITES_KEY, []));
  const [simulationYear, setSimulationYear] = useState(2026);

  const [lang, setLang] = useState(() => window.localStorage.getItem(LANG_KEY) || 'ru');
  const t = (key) => TRANSLATIONS[lang][key] || key;

  const [bonuses, setBonuses] = useState(() => parseInt(window.localStorage.getItem(BONUS_KEY)) || 0);
  const [lastBonusEarned, setLastBonusEarned] = useState(null);

  const [remoteSimulation, setRemoteSimulation] = useState(null);
  const [backendStatus, setBackendStatus] = useState('local');
  const [showAuth, setShowAuth] = useState(true);
  const [user, setUser] = useState(null);

  const ALL_SITES = useMemo(() => [...DEVELOPMENT_SITES, ...customSites], [customSites]);
  const [selectedSiteId, setSelectedSiteId] = useState(ALL_SITES[0]?.id);

  const localSimulation = useMemo(() => simulateCity(placements), [placements]);

  const simulation = useMemo(() => {
    const base = remoteSimulation || localSimulation;

    let finalScore = base?.score || 0;
    let finalMetrics = { ...(base?.metrics || {}) };
    let finalDeltas = { ...(base?.deltas || {}) };

    const IMPACTS = {
      park: { air: 4, green: 6, social: 2, traffic: -1, economy: -1, resilience: 2 },
      residential: { housing: 6, traffic: 3, utility: 3, air: -2, social: 1, green: -1 },
      mixedUse: { economy: 4, housing: 3, traffic: 2, utility: 2, social: 2 },
      school: { social: 6, traffic: 1, utility: 1, economy: 1 },
      hospital: { social: 8, traffic: 2, utility: 2, resilience: 3 },
      transit: { traffic: -6, air: 2, economy: 3, social: 2 },
      energy: { utility: -8, resilience: 6, air: -3, economy: 2 }
    };

    Object.entries(placements).forEach(([siteId, typeId]) => {
      if (siteId.startsWith('custom_')) {
        const impacts = IMPACTS[typeId] || {};
        Object.entries(impacts).forEach(([metric, val]) => {
          finalMetrics[metric] = (finalMetrics[metric] || 50) + val;
          finalDeltas[metric] = (finalDeltas[metric] || 0) + val;
          const scoreImpact = METRIC_META[metric]?.goodHigh ? val : -val;
          finalScore += scoreImpact * 0.4;
        });
      }
    });

    Object.keys(finalMetrics).forEach(k => { finalMetrics[k] = Math.max(0, Math.min(100, finalMetrics[k])); });

    const yearsAhead = simulationYear - 2026;
    if (yearsAhead > 0) {
      const trend = finalScore >= 50 ? 1.5 : -2.5;
      finalScore = finalScore + (yearsAhead * trend);
    }

    finalScore = Math.max(0, Math.min(100, Math.round(finalScore)));

    return {
      score: finalScore, summary: base?.summary || t('loading'),
      metrics: finalMetrics, deltas: finalDeltas,
      warnings: base?.warnings || [], opportunities: base?.opportunities || [],
      rankedSites: base?.rankedSites || []
    };
  }, [remoteSimulation, localSimulation, simulationYear, placements, lang]);

  const selectedSite = ALL_SITES.find((s) => s.id === selectedSiteId) || ALL_SITES[0];

  const getLocalized = (item) => {
    if (!item) return '';
    if (typeof item === 'object' && !Array.isArray(item)) return item[lang] || item.ru || '';
    return item;
  };

  const facts = Array.isArray(STORY_FACTS) ? STORY_FACTS : (STORY_FACTS[lang] || []);
  const handleLogin = (username) => { setUser(username); setShowAuth(false); };

  useEffect(() => window.localStorage.setItem(STORAGE_KEY, JSON.stringify(placements)), [placements]);
  useEffect(() => window.localStorage.setItem(CUSTOM_SITES_KEY, JSON.stringify(customSites)), [customSites]);
  useEffect(() => window.localStorage.setItem(BONUS_KEY, bonuses.toString()), [bonuses]);
  useEffect(() => window.localStorage.setItem(LANG_KEY, lang), [lang]);

  useEffect(() => {
    if (lastBonusEarned) {
      const timer = setTimeout(() => setLastBonusEarned(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [lastBonusEarned]);

  useEffect(() => {
    const controller = new AbortController();
    async function syncScenario() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/simulate`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ placements: Object.entries(placements).map(([site_id, type_id]) => ({ site_id, type_id })), lang }),
          signal: controller.signal,
        });
        if (!response.ok) throw new Error();
        const data = await response.json();
        setRemoteSimulation(data.simulation || data);
        setBackendStatus('connected');
      } catch (err) {
        if (err.name !== 'AbortError') { setRemoteSimulation(null); setBackendStatus('local'); }
      }
    }
    syncScenario();
    return () => controller.abort();
  }, [placements, lang]);

  const handleMapClick = (e) => {
    if (!e.lngLat) return;
    const { lng, lat } = e.lngLat;
    const newSiteId = `custom_${Date.now()}`;
    const newSite = {
      id: newSiteId, name: `${t('customZone')} ${customSites.length + 1}`,
      lng: lng, lat: lat, recommendation: t('customRec'), isCustom: true
    };
    setCustomSites(prev => [...prev, newSite]);
    setSelectedSiteId(newSiteId);
    if (selectedTypeId !== 'none') applyPlacement(newSiteId, selectedTypeId);
  };

  const applyPlacement = (siteId, forcedTypeId = null) => {
    const typeToBuild = forcedTypeId || selectedTypeId;
    startTransition(() => {
      setPlacements((prev) => {
        const next = { ...prev };
        if (typeToBuild === 'none') {
          delete next[siteId];
        } else {
          const isNewPlacement = !prev[siteId] || prev[siteId] !== typeToBuild;
          next[siteId] = typeToBuild;
          if (isNewPlacement) {
            let earned = 10;
            if (['park', 'school', 'transit'].includes(typeToBuild)) earned += 15;
            setBonuses(prevBonuses => prevBonuses + earned);
            setLastBonusEarned(earned);
          }
        }
        return next;
      });
    });
  };

  // ФУНКЦИЯ УДАЛЕНИЯ ТОЧКИ
  const deleteCustomSite = (siteId) => {
    startTransition(() => {
      setPlacements(prev => {
        const next = { ...prev };
        delete next[siteId];
        return next;
      });
      setCustomSites(prev => prev.filter(s => s.id !== siteId));
      setSelectedSiteId(DEVELOPMENT_SITES[0]?.id);
    });
  };

  // ВОЗВРАЩАЕМ 3D-ЗДАНИЯ
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

  const yearsAhead = simulationYear - 2026;
  const isFuture = yearsAhead > 0;
  const isBadFuture = isFuture && simulation.score < 50;
  const isGoodFuture = isFuture && simulation.score >= 50;

  const smogOpacity = isBadFuture ? Math.min(0.6, (yearsAhead * 0.08)) : 0;
  const greenOpacity = isGoodFuture ? Math.min(0.3, (yearsAhead * 0.05)) : 0;

  return (
    <div className="app-shell">
      {showAuth && <AuthModal onLogin={handleLogin} />}

      {lastBonusEarned && (
        <div className="bonus-toast">
          <Coins size={20} color="#fbbf24" />
          <span>+{lastBonusEarned} {t('bonusEarned')}</span>
        </div>
      )}

      <header className="topbar">
        <div>
          <p className="eyebrow">{t('subtitle')}</p>
          <h1>ALMATY TWIN CITY</h1>
        </div>
        <div className="topbar__status">

          {/* НОВЫЙ СТИЛЬНЫЙ БЛОК ЯЗЫКОВ */}
          <div className="lang-toggle-group">
            <Globe size={14} color="#94a3b8" />
            <div className="lang-buttons">
              <button className={lang === 'kk' ? 'active' : ''} onClick={() => setLang('kk')}>ҚАЗ</button>
              <button className={lang === 'ru' ? 'active' : ''} onClick={() => setLang('ru')}>РУС</button>
              <button className={lang === 'en' ? 'active' : ''} onClick={() => setLang('en')}>ENG</button>
            </div>
          </div>

          <div className="bonus-badge">
            <Coins size={18} /><strong>{bonuses} EcoCoins</strong>
          </div>
          {user && <span className="user-badge" style={{marginRight: '15px'}}>👤 {user}</span>}
          <span className={`status-pill status-pill--${backendStatus}`}>
            {backendStatus === 'connected' ? t('backendOnline') : t('localSim')}
          </span>
          <strong className="score-card">{t('cityScore')}: {simulation.score}/100</strong>
        </div>
      </header>

      <main className="dashboard">
        <aside className="panel">
          <section className="panel-card time-machine-card">
            <div className="section-heading">
              <span className="eyebrow"><Clock size={16}/> {t('timeMachine')}</span>
              <strong style={{color: isBadFuture ? '#ef4444' : (isGoodFuture ? '#22c55e' : '#f8fafc')}}>
                {simulationYear}
              </strong>
            </div>
            <input
              type="range" className="time-slider"
              min="2026" max="2035" step="1"
              value={simulationYear} onChange={(e) => setSimulationYear(Number(e.target.value))}
            />
            <div className="time-labels"><span>2026</span><span>2035</span></div>
          </section>

          <section className="metrics-grid">
            {Object.keys(METRIC_META).map((key) => (
              <MetricCard key={key} metricKey={key} value={simulation.metrics[key] || 0} delta={simulation.deltas[key] || 0} t={t} />
            ))}
          </section>

          <section className="panel-card districts-section">
             <div className="section-heading"><span className="eyebrow">{t('districtsTitle')}</span><MapPinned size={16}/></div>
             <div className="district-list">
                {DISTRICTS.map(d => (
                  <div key={d.id} className="district-item">
                    <div className="district-swatch" style={{backgroundColor: d.color}} />
                    <div><strong>{getLocalized(d.name)}</strong><p>{getLocalized(d.summary)}</p></div>
                  </div>
                ))}
             </div>
          </section>
        </aside>

        <section className="scene-column">
          <div className="scene-frame">
            <div className="future-overlay" style={{ backgroundColor: `rgba(239, 68, 68, ${smogOpacity})` }} />
            <div className="future-overlay" style={{ backgroundColor: `rgba(34, 197, 94, ${greenOpacity})` }} />

            <Map
              initialViewState={{ longitude: MAP_CONFIG.center.lng, latitude: MAP_CONFIG.center.lat, zoom: 13.8, pitch: 60, bearing: -15 }}
              mapStyle="https://api.maptiler.com/maps/dataviz-dark/style.json?key=NXx3d6NShBcON5h53Scs"
              style={{ width: '100%', height: '100%' }}
              onClick={handleMapClick}
              onLoad={onMapLoad} // <-- ВОТ ТУТ 3D ЗДАНИЯ!
              cursor="crosshair"
            >
              <NavigationControl position="bottom-right" />
              {ALL_SITES.map((site) => {
                const lng = site.isCustom ? site.lng : (MAP_CONFIG.center.lng + site.position[0] * MAP_CONFIG.scale * 1.5);
                const lat = site.isCustom ? site.lat : (MAP_CONFIG.center.lat - site.position[1] * MAP_CONFIG.scale);

                const isSelected = selectedSiteId === site.id;
                const placedTypeId = placements[site.id];
                const typeInfo = placedTypeId ? DEVELOPMENT_TYPES[placedTypeId] : null;
                const markerColor = typeInfo ? typeInfo.color : (site.isCustom ? '#f59e0b' : '#38bdf8');
                const Icon = placedTypeId ? (TYPE_ICONS[placedTypeId] || Building2) : MapPin;

                return (
                  <Marker key={site.id} longitude={lng} latitude={lat} anchor="bottom" onClick={(e) => { e.originalEvent.stopPropagation(); setSelectedSiteId(site.id); }}>
                    {isSelected && <div className="marker-pulse-ring" style={{ border: `2px solid ${markerColor}` }} />}
                    <div className={`map-marker ${isSelected ? 'map-marker--selected' : ''}`} style={{ backgroundColor: markerColor, boxShadow: isSelected ? `0 0 20px ${markerColor}` : '' }}>
                      <Icon color="#fff" size={18} />
                    </div>
                  </Marker>
                );
              })}
            </Map>
            <div className="scene-overlay scene-overlay--top">
              <strong>{t('mapTitle')}</strong>
              <span>{t('mapSubtitle')}</span>
            </div>
          </div>

          <section className="toolbar">
            {Object.values(DEVELOPMENT_TYPES).map((type) => (
              <button key={type.id} className={`tool-chip ${selectedTypeId === type.id ? 'tool-chip--active' : ''}`} onClick={() => setSelectedTypeId(type.id)}>
                <span className="tool-chip__swatch" style={{ backgroundColor: type.color }} />
                <span>{getLocalized(type.shortLabel) || getLocalized(type.label)}</span>
              </button>
            ))}
            <button className="tool-chip tool-chip--ghost" onClick={() => { if(window.confirm(t('confirmReset'))) { setPlacements({}); setCustomSites([]); setBonuses(0); setSimulationYear(2026); setRemoteSimulation(null); } }}>
              {t('btnReset')}
            </button>
          </section>
        </section>

        <aside className="panel">
          <section className="panel-card">
            <div className="section-heading">
              <span className="eyebrow">{t('siteAnalysis')}</span>
              <strong>{selectedSite ? getLocalized(selectedSite.name) : '-'}</strong>
            </div>
            <p className="site-description">{selectedSite ? getLocalized(selectedSite.recommendation) : '-'}</p>
            <div className="action-stack">
              <button className="primary-action" disabled={!selectedSite} onClick={() => applyPlacement(selectedSite.id)}>
                {t('btnBuild')} {getLocalized(DEVELOPMENT_TYPES[selectedTypeId]?.label)}
              </button>

              {/* ЕСЛИ ЭТО ТОЧКА ПОЛЬЗОВАТЕЛЯ - ПОКАЗЫВАЕМ КРАСНУЮ КНОПКУ УДАЛЕНИЯ */}
              {selectedSite?.isCustom ? (
                <button className="secondary-action custom-delete-btn" onClick={() => deleteCustomSite(selectedSite.id)}>
                  <Trash2 size={16} style={{marginRight: '6px'}}/> {t('btnDeletePoint')}
                </button>
              ) : (
                <button className="secondary-action" disabled={!selectedSite} onClick={() => { setSelectedTypeId('none'); applyPlacement(selectedSite.id, 'none'); }}>
                  {t('btnClear')}
                </button>
              )}
            </div>
          </section>

          <section className="panel-card">
            <span className="eyebrow">{t('aiInsights')}</span>
            <div className="insight-block">
              {simulation.warnings.map((w, i) => <p key={i} className="warning-text">{w}</p>)}
              {simulation.opportunities.map((o, i) => <p key={i} className="positive-text">{o}</p>)}
              {simulation.warnings.length === 0 && <p className="positive-text">{t('noRisks')}</p>}
            </div>
          </section>

          {user && <ChatWindow currentUser={user} />}
        </aside>
      </main>
    </div>
  );
}