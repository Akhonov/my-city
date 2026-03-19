import React, { startTransition, useEffect, useMemo, useState } from 'react';
import {
  Activity, Building2, Briefcase, Factory, HeartPulse, Leaf, MapPinned,
  School, ShieldCheck, TramFront, Trees, Zap, MapPin, Coins, Globe
} from 'lucide-react';
import Map, { Marker, NavigationControl } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import './App.css';
import { API_BASE_URL } from './api';
import AuthModal from './components/AuthModal';
import ChatWindow from './components/ChatWindow';

// Импортируем твои данные
import {
  DEVELOPMENT_SITES, DEVELOPMENT_TYPES, DISTRICTS, STORY_FACTS,
} from './cityModel';
import { simulateCity } from './simulation';

const STORAGE_KEY = 'almaty-twin-city:placements';
const BONUS_KEY = 'almaty-twin-city:bonuses';
const LANG_KEY = 'almaty-twin-city:lang';

// --- ПОЛНЫЙ СЛОВАРЬ ПЕРЕВОДОВ ---
const TRANSLATIONS = {
  ru: {
    subtitle: 'Цифровой двойник Алматы / Хакатон 2026',
    backendOnline: 'Бэкенд подключен',
    localSim: 'Локальная симуляция',
    cityScore: 'Рейтинг города',
    summaryTitle: 'Сводка',
    districtsTitle: 'Районы',
    mapTitle: '3D ГИС Симуляция',
    mapSubtitle: 'Выберите участок на карте',
    btnReset: 'Сброс',
    confirmReset: 'Очистить все застройки и сбросить бонусы?',
    siteAnalysis: 'Анализ участка',
    btnBuild: 'Разместить:',
    btnClear: 'Очистить участок',
    aiInsights: 'ИИ Анализ',
    noRisks: 'Критических рисков не обнаружено.',
    recommendations: 'Рекомендации',
    suitability: 'Совместимость:',
    bonusEarned: 'EcoCoins получено!',
    loading: 'Загрузка данных...',
    // Метрики
    metric_air: 'Воздух', metric_traffic: 'Трафик', metric_green: 'Озеленение',
    metric_housing: 'Жилье', metric_economy: 'Экономика', metric_social: 'Соцсервисы',
    metric_utility: 'Сети', metric_resilience: 'Устойчивость',
    pts: 'балл', load: 'нагр.',
  },
  kk: {
    subtitle: 'Алматының цифрлық егізі / Хакатон 2026',
    backendOnline: 'Бэкенд қосылған',
    localSim: 'Жергілікті симуляция',
    cityScore: 'Қала рейтингі',
    summaryTitle: 'Түйіндеме',
    districtsTitle: 'Аудандар',
    mapTitle: '3D ГИС Симуляция',
    mapSubtitle: 'Картадан аумақты таңдаңыз',
    btnReset: 'Қалпына келтіру',
    confirmReset: 'Барлық құрылыстарды жойып, бонустарды нөлдеу керек пе?',
    siteAnalysis: 'Аумақ анализі',
    btnBuild: 'Орналастыру:',
    btnClear: 'Аумақты тазарту',
    aiInsights: 'ЖИ Анализі',
    noRisks: 'Критикалық тәуекелдер анықталған жоқ.',
    recommendations: 'Ұсыныстар',
    suitability: 'Сәйкестігі:',
    bonusEarned: 'EcoCoins алынды!',
    loading: 'Деректер жүктелуде...',
    // Метрики
    metric_air: 'Ауа сапасы', metric_traffic: 'Кептеліс', metric_green: 'Көгалдандыру',
    metric_housing: 'Тұрғын үй', metric_economy: 'Экономика', metric_social: 'Әлеуметтік',
    metric_utility: 'Желілер', metric_resilience: 'Тұрақтылық',
    pts: 'ұпай', load: 'жүктеме',
  },
  en: {
    subtitle: 'Digital Twin of Almaty / Hackathon 2026',
    backendOnline: 'Backend Online',
    localSim: 'Local Simulation',
    cityScore: 'City Score',
    summaryTitle: 'Summary',
    districtsTitle: 'Districts',
    mapTitle: '3D GIS Simulation',
    mapSubtitle: 'Select a site on the map',
    btnReset: 'Reset',
    confirmReset: 'Clear all placements and reset bonuses?',
    siteAnalysis: 'Site Analysis',
    btnBuild: 'Build:',
    btnClear: 'Clear site',
    aiInsights: 'AI Insights',
    noRisks: 'No critical risks detected.',
    recommendations: 'Recommendations',
    suitability: 'Suitability:',
    bonusEarned: 'EcoCoins received!',
    loading: 'Loading data...',
    // Метрики
    metric_air: 'Air Quality', metric_traffic: 'Traffic', metric_green: 'Greenery',
    metric_housing: 'Housing', metric_economy: 'Economy', metric_social: 'Social',
    metric_utility: 'Utilities', metric_resilience: 'Resilience',
    pts: 'pts', load: 'load',
  }
};

function loadPlacements() {
  if (typeof window === 'undefined') return {};
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    return JSON.parse(raw);
  } catch { return {}; }
}

const MAP_CONFIG = { center: { lng: 76.9415, lat: 43.2551 }, scale: 0.0006 };

const METRIC_META = {
  air: { icon: <Leaf size={16} />, goodHigh: true },
  traffic: { icon: <Activity size={16} />, goodHigh: false },
  green: { icon: <Trees size={16} />, goodHigh: true },
  housing: { icon: <Building2 size={16} />, goodHigh: true },
  economy: { icon: <Factory size={16} />, goodHigh: true },
  social: { icon: <HeartPulse size={16} />, goodHigh: true },
  utility: { icon: <Zap size={16} />, goodHigh: false },
  resilience: { icon: <ShieldCheck size={16} />, goodHigh: true },
};

const TYPE_ICONS = {
  none: MapPin, residential: Building2, mixedUse: Briefcase,
  park: Trees, school: School, hospital: HeartPulse,
  transit: TramFront, energy: Zap,
};

// Передаем функцию t (переводчик) внутрь карточки
function MetricCard({ metricKey, value, delta, t }) {
  const meta = METRIC_META[metricKey];
  const improved = meta.goodHigh ? delta > 0 : delta < 0;
  const tone = delta === 0 ? 'neutral' : (improved ? 'good' : 'bad');

  return (
    <article className={`metric-card metric-card--${tone}`}>
      <div className="metric-card__header">
        <span className="metric-card__label">{meta.icon}{t(`metric_${metricKey}`)}</span>
        <strong>{value}</strong>
      </div>
      <div className="metric-card__bar">
        <span style={{ width: `${Math.max(6, value)}%` }} />
      </div>
      <p className="metric-card__delta">
        {delta > 0 ? '+' : ''}{delta} {metricKey === 'traffic' ? t('load') : t('pts')}
      </p>
    </article>
  );
}

// --- КАРТА ---
function RealCityMap({ placements, selectedSiteId, onSiteSelect }) {
  const project = (pos) => {
    if (!pos) return [MAP_CONFIG.center.lng, MAP_CONFIG.center.lat];
    return [
      MAP_CONFIG.center.lng + pos[0] * MAP_CONFIG.scale * 1.5,
      MAP_CONFIG.center.lat - pos[1] * MAP_CONFIG.scale
    ];
  };

  return (
    <Map
      initialViewState={{ longitude: MAP_CONFIG.center.lng, latitude: MAP_CONFIG.center.lat, zoom: 13.8, pitch: 60, bearing: -15 }}
      mapStyle="https://api.maptiler.com/maps/dataviz-dark/style.json?key=NXx3d6NShBcON5h53Scs"
      style={{ width: '100%', height: '100%' }}
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
          <Marker key={site.id} longitude={lng} latitude={lat} anchor="bottom" onClick={(e) => { e.originalEvent.stopPropagation(); onSiteSelect(site.id); }}>
            {isSelected && <div className="marker-pulse-ring" style={{ border: `2px solid ${markerColor}` }} />}
            <div className={`map-marker ${isSelected ? 'map-marker--selected' : ''}`} style={{ backgroundColor: markerColor, boxShadow: isSelected ? `0 0 20px ${markerColor}` : '' }}>
              <Icon color="#fff" size={18} />
            </div>
            <div className="map-marker-label">{site.name}</div>
          </Marker>
        );
      })}
    </Map>
  );
}

export default function App() {
  const [selectedTypeId, setSelectedTypeId] = useState('transit');
  const [selectedSiteId, setSelectedSiteId] = useState(DEVELOPMENT_SITES[0].id);
  const [placements, setPlacements] = useState(() => loadPlacements());

  const [lang, setLang] = useState(() => window.localStorage.getItem(LANG_KEY) || 'ru');
  const t = (key) => TRANSLATIONS[lang][key] || key;

  const [bonuses, setBonuses] = useState(() => parseInt(window.localStorage.getItem(BONUS_KEY)) || 0);
  const [lastBonusEarned, setLastBonusEarned] = useState(null);

  const [remoteSimulation, setRemoteSimulation] = useState(null);
  const [backendStatus, setBackendStatus] = useState('local');
  const [showAuth, setShowAuth] = useState(true);
  const [user, setUser] = useState(null);

  const localSimulation = useMemo(() => simulateCity(placements), [placements]);

  const simulation = useMemo(() => {
    const base = remoteSimulation || localSimulation;
    return {
      score: base?.score || 0,
      summary: base?.summary || t('loading'),
      metrics: base?.metrics || {},
      deltas: base?.deltas || {},
      warnings: base?.warnings || [],
      opportunities: base?.opportunities || [],
      rankedSites: base?.rankedSites || []
    };
  }, [remoteSimulation, localSimulation, lang]);

  const selectedSite = DEVELOPMENT_SITES.find((s) => s.id === selectedSiteId) || DEVELOPMENT_SITES[0];

  // Функция для безопасного получения локализованного текста из cityModel
  const getLocalized = (item) => {
    if (!item) return '';
    if (typeof item === 'object' && !Array.isArray(item)) return item[lang] || item.ru || '';
    return item;
  };

  // Получаем факты с учетом языка
  const facts = Array.isArray(STORY_FACTS) ? STORY_FACTS : (STORY_FACTS[lang] || []);

  const handleLogin = (username) => { setUser(username); setShowAuth(false); };

  useEffect(() => window.localStorage.setItem(STORAGE_KEY, JSON.stringify(placements)), [placements]);
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
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            placements: Object.entries(placements).map(([site_id, type_id]) => ({ site_id, type_id })),
            lang: lang // ПЕРЕДАЕМ ВЫБРАННЫЙ ЯЗЫК НА БЭКЕНД!
          }),
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
  }, [placements, lang]); // Запрос будет уходить заново при смене языка

  const applyPlacement = (siteId) => {
    startTransition(() => {
      setPlacements((prev) => {
        const next = { ...prev };
        if (selectedTypeId === 'none') {
          delete next[siteId];
        } else {
          const isNewPlacement = !prev[siteId] || prev[siteId] !== selectedTypeId;
          next[siteId] = selectedTypeId;
          if (isNewPlacement) {
            let earned = 10;
            if (['park', 'school', 'transit'].includes(selectedTypeId)) earned += 15;
            setBonuses(prevBonuses => prevBonuses + earned);
            setLastBonusEarned(earned);
          }
        }
        return next;
      });
    });
  };

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
          <div className="lang-switcher">
            <Globe size={16} color="#94a3b8" />
            <select value={lang} onChange={(e) => setLang(e.target.value)}>
              <option value="kk">ҚАЗ</option>
              <option value="ru">РУС</option>
              <option value="en">ENG</option>
            </select>
          </div>
          <div className="bonus-badge">
            <Coins size={18} />
            <strong>{bonuses} EcoCoins</strong>
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
          <section className="panel-card hero-card">
            <span className="eyebrow">{t('summaryTitle')}</span>
            <p>{simulation.summary}</p>
            <ul className="fact-list">
              {facts.map((f, i) => <li key={i}>{f}</li>)}
            </ul>
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
            <RealCityMap placements={placements} selectedSiteId={selectedSiteId} onSiteSelect={setSelectedSiteId} />
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
            <button className="tool-chip tool-chip--ghost" onClick={() => { if(window.confirm(t('confirmReset'))) { setPlacements({}); setBonuses(0); setRemoteSimulation(null); } }}>
              {t('btnReset')}
            </button>
          </section>
        </section>

        <aside className="panel">
          <section className="panel-card">
            <div className="section-heading">
              <span className="eyebrow">{t('siteAnalysis')}</span>
              <strong>{getLocalized(selectedSite.name)}</strong>
            </div>
            <p className="site-description">{getLocalized(selectedSite.recommendation)}</p>
            <div className="action-stack">
              <button className="primary-action" onClick={() => applyPlacement(selectedSite.id)}>
                {t('btnBuild')} {getLocalized(DEVELOPMENT_TYPES[selectedTypeId]?.label)}
              </button>
              <button className="secondary-action" onClick={() => { setSelectedTypeId('none'); applyPlacement(selectedSite.id); }}>{t('btnClear')}</button>
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

          <section className="panel-card">
            <span className="eyebrow">{t('recommendations')}</span>
            <div className="recommendation-list">
              {simulation.rankedSites.slice(0, 3).map((item) => (
                <button key={item.siteId} className="recommendation-item" onClick={() => setSelectedSiteId(item.siteId)}>
                  <div><strong>{item.siteName}</strong><span>{item.suggestedTypeLabel}</span></div>
                  <b>{t('suitability')} {item.suitability}%</b>
                </button>
              ))}
            </div>
          </section>

          {user && <ChatWindow currentUser={user} />}
        </aside>
      </main>
    </div>
  );
}