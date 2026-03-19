import { BASELINE_METRICS, DEVELOPMENT_SITES, DEVELOPMENT_TYPES } from './cityModel';

const clamp = (value, min = 0, max = 100) => Math.min(max, Math.max(min, Math.round(value)));

const TYPE_IMPACTS = {
  residential: { air: -3, traffic: 8, green: -2, housing: 14, economy: 6, social: 2, utility: 9, resilience: -1 },
  mixedUse: { air: -2, traffic: 7, green: -1, housing: 6, economy: 14, social: 3, utility: 6, resilience: 0 },
  park: { air: 8, traffic: -3, green: 16, housing: 0, economy: 2, social: 8, utility: -3, resilience: 4 },
  school: { air: 1, traffic: 2, green: 1, housing: 0, economy: 3, social: 14, utility: 4, resilience: 3 },
  hospital: { air: 0, traffic: 3, green: 0, housing: 0, economy: 4, social: 15, utility: 5, resilience: 9 },
  transit: { air: 4, traffic: -12, green: 1, housing: 0, economy: 6, social: 5, utility: 3, resilience: 5 },
  energy: { air: -6, traffic: 4, green: -2, housing: 0, economy: 8, social: 0, utility: 16, resilience: 4 },
};

const METRIC_LABELS = {
  air: 'Воздух',
  traffic: 'Трафик',
  green: 'Озеленение',
  housing: 'Жилье',
  economy: 'Экономика',
  social: 'Соцсервисы',
  utility: 'Сети',
  resilience: 'Устойчивость',
};

function computeSiteAdjustedImpact(typeId, site) {
  const base = TYPE_IMPACTS[typeId];
  if (!base || !site) return null;

  const context = site.context;
  const impact = { ...base };

  impact.traffic += context.currentPressure * (typeId === 'residential' || typeId === 'mixedUse' ? 7 : 2);
  impact.traffic -= context.transitAccess * (typeId === 'transit' ? 8 : 1);
  impact.air -= context.currentPressure * (typeId === 'energy' ? 3 : 1.5);
  impact.green += context.greenDeficit * (typeId === 'park' ? 10 : 0);
  impact.social += context.socialDeficit * (typeId === 'school' || typeId === 'hospital' ? 10 : 1);
  impact.housing += context.socialDeficit * (typeId === 'residential' ? 3 : 0);
  impact.economy += context.roadAccess * (typeId === 'mixedUse' || typeId === 'energy' ? 4 : 1.5);
  impact.utility += (1 - context.utilityCapacity) * (typeId === 'energy' ? 5 : 3);
  impact.resilience -= context.seismicConstraint * (typeId === 'energy' || typeId === 'mixedUse' ? 3.5 : 1.5);
  impact.resilience += context.seismicConstraint * (typeId === 'hospital' ? 2 : 0);

  return impact;
}

function describePlacement(typeId, site, adjustedImpact) {
  const type = DEVELOPMENT_TYPES[typeId];
  const messages = [];

  if (typeId === 'transit' && adjustedImpact.traffic <= -12) {
    messages.push('разгружает магистрали и усиливает общественный транспорт');
  }
  if (typeId === 'park' && adjustedImpact.green >= 20) {
    messages.push('компенсирует дефицит зелени в перегретом районе');
  }
  if (typeId === 'hospital' && adjustedImpact.social >= 20) {
    messages.push('закрывает серьезный дефицит медуслуг в районе');
  }
  if (typeId === 'school' && adjustedImpact.social >= 20) {
    messages.push('снимает давление на существующие школы и секции');
  }
  if ((typeId === 'residential' || typeId === 'mixedUse') && adjustedImpact.traffic >= 10) {
    messages.push('требует компенсации трафика через BRT, вело и parking policy');
  }
  if (site.context.seismicConstraint > 0.75) {
    messages.push('нужны усиленные сейсмостандарты и ограничение по высоте');
  }

  return {
    siteId: site.id,
    siteName: site.name,
    district: site.district,
    typeId,
    typeLabel: type.label,
    effect: messages.length > 0 ? messages.join('; ') : 'дает сбалансированный эффект без критичных перекосов',
  };
}

export function simulateCity(placementsBySite) {
  const metrics = { ...BASELINE_METRICS };
  const deltas = Object.keys(metrics).reduce((acc, key) => ({ ...acc, [key]: 0 }), {});
  const placements = [];
  const districtLoad = {};

  for (const site of DEVELOPMENT_SITES) {
    const typeId = placementsBySite[site.id];
    if (!typeId || typeId === 'none') continue;

    const adjustedImpact = computeSiteAdjustedImpact(typeId, site);
    placements.push(describePlacement(typeId, site, adjustedImpact));
    districtLoad[site.district] = (districtLoad[site.district] || 0) + 1;

    for (const metricKey of Object.keys(metrics)) {
      deltas[metricKey] += adjustedImpact[metricKey] || 0;
    }
  }

  for (const metricKey of Object.keys(metrics)) {
    const direction = metricKey === 'traffic' || metricKey === 'utility' ? 1 : 1;
    metrics[metricKey] = clamp(BASELINE_METRICS[metricKey] + deltas[metricKey] * direction);
  }

  const normalizedTraffic = clamp(100 - metrics.traffic);
  const normalizedUtility = clamp(100 - metrics.utility);
  const score = clamp(
    metrics.air * 0.15 +
      normalizedTraffic * 0.18 +
      metrics.green * 0.12 +
      metrics.housing * 0.12 +
      metrics.economy * 0.15 +
      metrics.social * 0.11 +
      normalizedUtility * 0.07 +
      metrics.resilience * 0.1
  );

  const warnings = [];
  if (metrics.traffic > 82) warnings.push('Трафик выходит в красную зону: нужны transit-first меры.');
  if (metrics.air < 52) warnings.push('Качество воздуха ухудшается: компенсируйте парками и снижением автотрафика.');
  if (metrics.utility > 80) warnings.push('Инженерные сети перегружаются: добавьте энергоцентр или phased rollout.');
  if (metrics.resilience < 55) warnings.push('Устойчивость снижается: усилите сейсмостойкость и эвакуационные сценарии.');

  const opportunities = [];
  if (metrics.green > BASELINE_METRICS.green + 8) opportunities.push('Сценарий улучшает микроклимат и снижает heat island.');
  if (metrics.social > BASELINE_METRICS.social + 8) opportunities.push('Новые соцобъекты повышают доступность сервиса по районам.');
  if (metrics.economy > BASELINE_METRICS.economy + 8) opportunities.push('Экономический потенциал растет без потери управляемости.');
  if (metrics.housing > BASELINE_METRICS.housing + 8) opportunities.push('Сценарий расширяет предложение жилья в дефицитных кластерах.');

  const strongestMetric = Object.entries(deltas)
    .filter(([metric]) => metric !== 'traffic' && metric !== 'utility')
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))[0];

  const summary = placements.length === 0
    ? 'Выберите участок и тип объекта. Система покажет влияние на воздух, трафик, сети и устойчивость.'
    : `Сценарий включает ${placements.length} новых объекта(ов). Самое сильное изменение: ${METRIC_LABELS[strongestMetric[0]]} ${
        strongestMetric[1] >= 0 ? 'улучшается' : 'ухудшается'
      } на ${Math.abs(Math.round(strongestMetric[1]))} п.`;

  const rankedSites = DEVELOPMENT_SITES.map((site) => {
    const selectedType = placementsBySite[site.id];
    const suggestedType = selectedType && selectedType !== 'none'
      ? selectedType
      : site.context.socialDeficit > 0.75
        ? 'school'
        : site.context.transitAccess > 0.85
          ? 'transit'
          : site.context.greenDeficit > 0.65
            ? 'park'
            : 'mixedUse';

    const projected = computeSiteAdjustedImpact(suggestedType, site);
    const suitability = clamp(
      72 +
        site.context.transitAccess * (suggestedType === 'transit' ? 18 : 6) +
        site.context.greenDeficit * (suggestedType === 'park' ? 16 : 0) +
        site.context.socialDeficit * (suggestedType === 'school' || suggestedType === 'hospital' ? 18 : 4) +
        site.context.utilityCapacity * (suggestedType === 'energy' ? 12 : 4) -
        site.context.currentPressure * (suggestedType === 'mixedUse' || suggestedType === 'residential' ? 12 : 4) -
        site.context.seismicConstraint * (suggestedType === 'mixedUse' ? 10 : 5)
    );

    return {
      siteId: site.id,
      siteName: site.name,
      suggestedType,
      suggestedTypeLabel: DEVELOPMENT_TYPES[suggestedType].label,
      suitability,
      quickImpact: projected,
    };
  }).sort((a, b) => b.suitability - a.suitability);

  return {
    metrics,
    baseline: BASELINE_METRICS,
    deltas: Object.fromEntries(Object.entries(deltas).map(([key, value]) => [key, Math.round(value)])),
    score,
    warnings,
    opportunities,
    summary,
    placements,
    rankedSites,
  };
}