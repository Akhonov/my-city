export const DEVELOPMENT_TYPES = {
  none: { id: 'none', label: 'Очистить участок', shortLabel: 'Сброс', color: '#64748b' },
  residential: { id: 'residential', label: 'Жилой квартал', shortLabel: 'Жилье', color: '#7dd3fc' },
  mixedUse: { id: 'mixedUse', label: 'Mixed-use кластер', shortLabel: 'Mixed-use', color: '#c084fc' },
  park: { id: 'park', label: 'Городской парк', shortLabel: 'Парк', color: '#22c55e' },
  school: { id: 'school', label: 'Школа / STEM центр', shortLabel: 'Школа', color: '#fbbf24' },
  hospital: { id: 'hospital', label: 'Медицинский центр', shortLabel: 'Клиника', color: '#fb7185' },
  transit: { id: 'transit', label: 'Transit hub', shortLabel: 'Транспорт', color: '#38bdf8' },
  energy: { id: 'energy', label: 'Энергоцентр', shortLabel: 'Энергия', color: '#f97316' },
};

export const STORY_FACTS = {
  ru: [
    "Алматы растет между плотным центром, предгорьями и промышленным поясом.",
    "Ключевые ограничения: транспортная перегрузка, инверсия воздуха."
  ],
  kk: [
    "Алматы тығыз орталық, тау бөктері мен өнеркәсіптік белдеу арасында өсуде.",
    "Негізгі шектеулер: көлік кептелісі, ауа инверсиясы."
  ],
  en: [
    "Almaty is growing between a dense center, foothills and an industrial belt.",
    "Key constraints: traffic congestion, air inversion."
  ]
};

export const DISTRICTS = [
  { id: 'historic-core', name: 'Исторический центр', center: [-1, 0], size: [10, 14], color: '#1e293b', summary: 'Историческая ткань, туризм и культурные объекты.' },
  { id: 'esentai', name: 'Есентай и деловой пояс', center: [11, -2], size: [10, 10], color: '#0f766e', summary: 'Финансы, офисы и mixed-use проекты.' },
  { id: 'south-foothill', name: 'Южные предгорья', center: [4, -10], size: [20, 8], color: '#334155', summary: 'Предгорные районы с видом на Алатау.' },
  { id: 'west-growth', name: 'Западный рост', center: [-11, -1], size: [10, 12], color: '#3f3f46', summary: 'Новые жилые кварталы и дефицит соцобъектов.' },
  { id: 'north-logistics', name: 'Северный логистический пояс', center: [2, 10], size: [22, 10], color: '#1f2937', summary: 'Промзона, склады и коммунальная инфраструктура.' },
];

export const ROADS = [
  { id: 'al-farabi', name: 'пр. Аль-Фараби', start: [-18, -8], end: [18, -8], width: 1.2, color: '#64748b' },
  { id: 'abay', name: 'пр. Абая', start: [-20, 0], end: [20, 0], width: 1.4, color: '#94a3b8' },
  { id: 'tole-bi', name: 'ул. Толе би', start: [-18, 4], end: [18, 4], width: 1.1, color: '#475569' },
  { id: 'dostyk', name: 'пр. Достык', start: [6, -18], end: [6, 16], width: 1.2, color: '#cbd5e1' },
  { id: 'nazarbayev', name: 'ул. Назарбаева', start: [1, -18], end: [1, 16], width: 0.9, color: '#94a3b8' },
  { id: 'seifullin', name: 'пр. Сейфуллина', start: [-8, -16], end: [-8, 16], width: 1.0, color: '#64748b' },
];

export const GREEN_ZONES = [
  { id: 'panfilov-park', name: 'Парк 28 гвардейцев', position: [2.4, 0.8], size: [4.2, 3.4], color: '#166534' },
  { id: 'botanical', name: 'Ботанический сад', position: [8.5, -4.8], size: [4.8, 3.6], color: '#15803d' },
  { id: 'first-president', name: 'Парк Первого Президента', position: [10.5, -11], size: [5.8, 3.6], color: '#14532d' },
  { id: 'sairan', name: 'Сайранский зеленый коридор', position: [-8.5, -3.2], size: [3.6, 4.4], color: '#166534' },
];

export const EXISTING_BUILDINGS = [
  { id: 'kbtu', name: 'KBTU', position: [-3, 1], size: [2.2, 2.6], color: '#f8c15c' },
  { id: 'hotel-kz', name: 'Hotel Kazakhstan', position: [4.5, -1.5], size: [1.8, 1.8], color: '#60a5fa' },
  { id: 'panfilov', name: 'Пешеходная Панфилова', position: [1.5, 2.5], size: [0.8, 6.6], color: '#cbd5e1' },
  { id: 'ascension', name: 'Вознесенский собор', position: [2.8, 1.8], size: [1.6, 1.2], color: '#fef08a' },
  { id: 'green-bazaar', name: 'Зеленый базар', position: [4.6, 3.5], size: [2.4, 1.4], color: '#fb7185' },
  { id: 'nurly-tau', name: 'Нурлы Тау', position: [10.5, -1.2], size: [3.2, 1.8], color: '#22c55e' },
  { id: 'esentai-tower', name: 'Esentai Tower', position: [13.5, -3], size: [1.8, 1.8], color: '#a78bfa' },
  { id: 'dostyk-plaza', name: 'Dostyk Plaza', position: [7.8, -8.7], size: [3.4, 2], color: '#f59e0b' },
  { id: 'kok-tobe', name: 'Кок-Тобе Tower', position: [11.5, -13], size: [0.8, 0.8], color: '#e2e8f0' },
  { id: 'res-west-1', name: 'ЖК Family', position: [-11, -1], size: [2.8, 2.4], color: '#7dd3fc' },
  { id: 'res-west-2', name: 'ЖК Auezov', position: [-13.5, 2.2], size: [2.8, 2.2], color: '#38bdf8' },
  { id: 'tec-2', name: 'ТЭЦ-2', position: [8.5, 10], size: [3.6, 2.4], color: '#ef4444' },
  { id: 'logistics-hub', name: 'Логистический терминал', position: [-1.5, 9.8], size: [4.5, 2.4], color: '#94a3b8' },
  { id: 'bus-station', name: 'Сайран транспортный узел', position: [-8.5, 0.2], size: [2.8, 1.2], color: '#c084fc' },
];

export const DEVELOPMENT_SITES = [
  {
    id: 'site-abay-river',
    name: 'Abay Riverfront',
    district: 'historic-core',
    position: [0.5, -2.8],
    size: [2.8, 2.4],
    recommendation: 'Подходит для low-impact mixed-use, парка или transit-first сценария.',
    context: { transitAccess: 0.9, roadAccess: 0.8, currentPressure: 0.86, greenDeficit: 0.58, socialDeficit: 0.42, utilityCapacity: 0.58, seismicConstraint: 0.68 },
  },
  {
    id: 'site-west-housing',
    name: 'Auezov Growth Parcel',
    district: 'west-growth',
    position: [-12.5, -4.6],
    size: [3.4, 2.4],
    recommendation: 'Сильная площадка для жилья, школы и парка второй очереди.',
    context: { transitAccess: 0.55, roadAccess: 0.78, currentPressure: 0.48, greenDeficit: 0.72, socialDeficit: 0.84, utilityCapacity: 0.66, seismicConstraint: 0.38 },
  },
  {
    id: 'site-esentai-mix',
    name: 'Esentai East Lot',
    district: 'esentai',
    position: [15, -4.3],
    size: [2.8, 2.2],
    recommendation: 'Высокий потенциал для mixed-use, но нужен контроль трафика.',
    context: { transitAccess: 0.74, roadAccess: 0.92, currentPressure: 0.82, greenDeficit: 0.46, socialDeficit: 0.36, utilityCapacity: 0.71, seismicConstraint: 0.59 },
  },
  {
    id: 'site-foothill-clinic',
    name: 'Foothill Wellness Node',
    district: 'south-foothill',
    position: [3.5, -11.8],
    size: [3.6, 2.4],
    recommendation: 'Подходит для клиники, школы и устойчивых low-rise проектов.',
    context: { transitAccess: 0.44, roadAccess: 0.67, currentPressure: 0.34, greenDeficit: 0.31, socialDeficit: 0.76, utilityCapacity: 0.63, seismicConstraint: 0.82 },
  },
  {
    id: 'site-north-utility',
    name: 'North Utility Reserve',
    district: 'north-logistics',
    position: [4.5, 12.6],
    size: [4.2, 2.6],
    recommendation: 'Лучшее место для энергоузла и коммунальной инфраструктуры.',
    context: { transitAccess: 0.38, roadAccess: 0.88, currentPressure: 0.41, greenDeficit: 0.63, socialDeficit: 0.52, utilityCapacity: 0.85, seismicConstraint: 0.29 },
  },
  {
    id: 'site-sairan-transit',
    name: 'Sairan Mobility Gate',
    district: 'west-growth',
    position: [-7.5, -6.5],
    size: [2.8, 2.4],
    recommendation: 'Лучший участок для transit hub с разгрузкой западного потока.',
    context: { transitAccess: 0.91, roadAccess: 0.84, currentPressure: 0.74, greenDeficit: 0.54, socialDeficit: 0.45, utilityCapacity: 0.62, seismicConstraint: 0.36 },
  },
];

export const BASELINE_METRICS = {
  air: 63,
  traffic: 69,
  green: 48,
  housing: 57,
  economy: 72,
  social: 61,
  utility: 64,
  resilience: 58,
};


