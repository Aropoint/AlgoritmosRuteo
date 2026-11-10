'use strict';

// Sitio de la Tarea 3: consulta del usuario, panel de control con capas (Ver / Considerar), las cuatro técnicas
// de ruteo con su tiempo de cómputo y resiliencia, sorteo de fallas 0-100 y caso de ejemplo. Debajo, lo de la
// Tarea 2 (par Yen y flota con aviso), sin cambios de comportamiento.

const TECNICAS = {
  // Grosores anidados: si varias técnicas eligen el mismo tramo, se ven todas (de la más ancha a la más fina).
  dijkstra_m: { nombre: 'pgr_dijkstra (metros)', color: '#2563eb', dash: null, peso: 13, opacidad: 0.45 },
  milp_gurobi: { nombre: 'MILP con Gurobi', color: '#059669', dash: null, peso: 8, opacidad: 0.95 },
  dijkstra_ponderado: { nombre: 'pgr_dijkstra ponderado', color: '#7c3aed', dash: '9 9', peso: 4.5, opacidad: 1 },
  aco: { nombre: 'Colonia de hormigas (ACO)', color: '#f472b6', dash: null, peso: 2, opacidad: 1 },
};
const MOTIVOS = {
  edificio: { color: '#111827', texto: 'edificio (+ relieve) ≥ altura de vuelo − margen' },
  relieve: { color: '#92400e', texto: 'relieve ≥ altura de vuelo − margen' },
  zona_publicada: { color: '#be123c', texto: 'zona restringida publicada (OSM)' },
  zona_usuario: { color: '#e11d48', texto: 'zona prohibida dibujada por el usuario' },
};
const COLOR = { dijkstra: '#2563eb', propuesta: '#ea580c', origen: '#16a34a', destino: '#7c3aed' };
const AOI_DEFECTO = [[46.945, 31.95], [47.005, 32.04]];
const P_ESCALA = 0.12;  // p de falla que se pinta en rojo pleno

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const vacio = (x) => x === null || x === undefined || x === '' || Number.isNaN(Number(x));
const num = (x, d = 2) => (vacio(x) ? '—' : Number(x).toLocaleString('es-CL', { maximumFractionDigits: d }));
const pct = (x, d = 0) => (vacio(x) ? '—' : `${num(100 * x, d)} %`);
const si = (b) => (b ? '<span class="ok">✓</span>' : '<span class="no">✗</span>');

async function pedir(url, opciones) {
  const r = await fetch(url, opciones);
  let datos = null;
  try { datos = await r.json(); } catch (_) { datos = null; }
  if (!r.ok) {
    let detalle = datos && (datos.detail || datos.error);
    if (Array.isArray(detalle)) detalle = detalle.map((d) => d.msg).join('; ');
    throw new Error(typeof detalle === 'string' ? detalle : `HTTP ${r.status}`);
  }
  return datos;
}
const postJSON = (url, cuerpo) => pedir(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo) });

// ---------------------------------------------------------------------------
// Mapa base
// ---------------------------------------------------------------------------
const mapa = L.map('mapa', { preferCanvas: true }).fitBounds(AOI_DEFECTO);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; colaboradores de <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(mapa);

function rampa(t, paradas) {
  const x = Math.max(0, Math.min(1, Number(t) || 0)) * (paradas.length - 1);
  const i = Math.min(paradas.length - 2, Math.floor(x));
  const u = x - i;
  return `rgb(${paradas[i].map((v, k) => Math.round(v + (paradas[i + 1][k] - v) * u)).join(',')})`;
}
const colorP = (p) => rampa(Math.min(1, (Number(p) || 0) / P_ESCALA), [[156, 163, 175], [245, 158, 11], [220, 38, 38]]);
const colorRiesgo = (r) => rampa(r, [[156, 163, 175], [245, 158, 11], [220, 38, 38]]);
const colorElevacion = (t) => rampa(t, [[37, 99, 235], [22, 163, 74], [234, 179, 8], [146, 64, 14]]);

const ETIQUETAS = {
  id: 'id', largo_m: 'largo (m)', largo_km: 'largo (km)', riesgo: 'riesgo T2 (0–1)', r_eventos: 'intensidad UCDP',
  r_incendios: 'intensidad incendios', p_gnss: 'GPSJam (fracción de días en rojo)', pf_eventos: 'p falla UCDP',
  pf_incendios: 'p falla incendios', pf_gnss: 'p falla GNSS', pf_total: 'p falla (las 3 amenazas)',
  altura_max_edificio_m: 'edificio más alto a ≤ 15 m (m)', terreno_max_m: 'terreno máx. (m s. n. m.)',
  en_zona_restringida: 'en zona restringida', tipo: 'tipo', elevacion_m: 'elevación (m s. n. m.)', orden: 'orden',
  rol: 'rol', osm_id: 'OSM id', altura_m: 'altura (m)', origen_altura: 'origen de la altura', clase: 'clase',
  nombre: 'nombre', buffer_m: 'radio de protección (m)', h3: 'celda H3', dias_con_datos: 'días con datos',
  dias_rojos: 'días en rojo', frac_dias_rojos: 'fracción de días en rojo', pct_malo_medio: '% de aviones degradados',
  contiene_aoi: 'contiene el AOI', fecha: 'fecha', periodo: 'período', guerra: 'de guerra',
  tipo_violencia: 'tipo de violencia', muertes: 'muertes estimadas', lugar: 'lugar',
};
function tabla(props, titulo) {
  const filas = Object.entries(props).filter(([, v]) => v !== null && v !== undefined)
    .map(([k, v]) => `<tr><th>${esc(ETIQUETAS[k] || k)}</th><td>${esc(typeof v === 'number' ? num(v, 6) : v)}</td></tr>`);
  return `${titulo ? `<b>${esc(titulo)}</b>` : ''}<table class="popup">${filas.join('')}</table>`;
}

// ---------------------------------------------------------------------------
// Estado
// ---------------------------------------------------------------------------
const estado = {
  origen: null, destino: null, mision: null, defecto: null, puntos: null, perfiles: {},
  considerar: { edificios: true, relieve: true, viento: true, zonas_publicadas: true, eventos: true, incendios: true, gnss: true, zonas_usuario: true },
  zonas: [],            // {tipo: 'prohibida', vertices: [[lat, lon], ...]} | {tipo: 'amenaza', lat, lon, radio_m, p}
  ultimo: null,         // respuesta de /api/t3/rutas
  ultimoCuerpo: null,   // consulta con que se calculó
  sorteo: null,         // respuesta de /api/t3/sorteo
  capaArista: {},       // id -> capa del tramo
  propsArista: {},      // id -> propiedades de la BD
  viento: null,
};

// ---------------------------------------------------------------------------
// Panel de control (punto 4): capas con Ver y Considerar
// ---------------------------------------------------------------------------
const GRUPOS = ['Infraestructura', 'Metadata', 'Amenazas', 'Rutas', 'Simulación'];
const CAPAS = [
  { clave: 'aristas', grupo: 'Infraestructura', nombre: 'Tramos (color = p de falla)', ver: true },
  { clave: 'nodos', grupo: 'Infraestructura', nombre: 'Nodos (color = p de falla)', ver: false },
  { clave: 'excluidas', grupo: 'Infraestructura', nombre: 'Tramos no sobrevolables (por motivo)', ver: true },
  { clave: 'mision', grupo: 'Infraestructura', nombre: 'Misión y puntos de observación', ver: true },
  { clave: 'edificios', grupo: 'Metadata', nombre: 'Edificios OSM (oscuro = con altura)', ver: false, considerar: 'edificios' },
  { clave: 'elevacion', grupo: 'Metadata', nombre: 'Elevación del terreno (nodos)', ver: false, considerar: 'relieve' },
  { clave: 'viento', grupo: 'Metadata', nombre: 'Viento (flecha en el mapa)', ver: true, considerar: 'viento' },
  { clave: 'zonas_restringidas', grupo: 'Metadata', nombre: 'Zonas restringidas OSM (helipuertos)', ver: true, considerar: 'zonas_publicadas' },
  { clave: 'eventos', grupo: 'Amenazas', nombre: 'Eventos UCDP', ver: true, considerar: 'eventos' },
  { clave: 'incendios', grupo: 'Amenazas', nombre: 'Incendios de guerra (oscuro = evaluación)', ver: false, considerar: 'incendios' },
  { clave: 'gpsjam', grupo: 'Amenazas', nombre: 'GPSJam (celdas H3)', ver: false, considerar: 'gnss' },
  { clave: 'zonas_usuario', grupo: 'Amenazas', nombre: 'Zonas del usuario (prohibidas y de amenaza)', ver: true, considerar: 'zonas_usuario' },
  ...Object.entries(TECNICAS).map(([k, t]) => ({ clave: `ruta_${k}`, grupo: 'Rutas', nombre: t.nombre, ver: true, tecnica: k })),
  { clave: 'yen', grupo: 'Rutas', nombre: 'Par Yen y Dijkstra (Tarea 2)', ver: false },
  { clave: 'fallas', grupo: 'Simulación', nombre: 'Fallas sorteadas', ver: true },
  { clave: 'vuelos', grupo: 'Simulación', nombre: 'Vuelo tras el sorteo', ver: true },
  { clave: 'flota', grupo: 'Simulación', nombre: 'Flota con aviso (Tarea 2)', ver: true },
];
const capa = {};
CAPAS.forEach((c) => { capa[c.clave] = L.layerGroup(); });

function construirPanel() {
  const html = GRUPOS.map((g) => {
    const filas = CAPAS.filter((c) => c.grupo === g).map((c) => {
      const muestra = c.tecnica
        ? `<span class="linea" style="border-color:${TECNICAS[c.tecnica].color};border-top-style:${TECNICAS[c.tecnica].dash ? 'dashed' : 'solid'}"></span>`
        : '';
      const cons = c.considerar
        ? `<label class="considerar" title="Entra al cálculo"><input type="checkbox" data-considerar="${c.considerar}"${estado.considerar[c.considerar] ? ' checked' : ''}> considerar</label>`
        : '';
      return `<div class="capa"><label><input type="checkbox" data-ver="${c.clave}"${c.ver ? ' checked' : ''}> ${muestra}${esc(c.nombre)}</label>${cons}</div>`;
    });
    return `<div class="grupo"><div class="grupo-titulo">${g}</div>${filas.join('')}</div>`;
  });
  $('panel-capas').innerHTML = html.join('');
  $('panel-capas').querySelectorAll('[data-ver]').forEach((el) => el.addEventListener('change', () => verCapa(el.dataset.ver, el.checked)));
  $('panel-capas').querySelectorAll('[data-considerar]').forEach((el) => el.addEventListener('change', () => {
    estado.considerar[el.dataset.considerar] = el.checked;
    if (estado.ultimo) $('txt-recalcular').hidden = false;
  }));
  CAPAS.forEach((c) => verCapa(c.clave, c.ver));
}

function verCapa(clave, visible) {
  const c = CAPAS.find((x) => x.clave === clave);
  if (clave === 'viento') {
    controlViento.getContainer().style.display = visible ? '' : 'none';
    return;
  }
  if (visible) {
    capa[clave].addTo(mapa);
    if (CARGADORES[clave]) CARGADORES[clave]();
  } else {
    capa[clave].remove();
  }
  const chk = $('panel-capas').querySelector(`[data-ver="${clave}"]`);
  if (chk && chk.checked !== visible) chk.checked = visible;
  return c;
}

// Datos GeoJSON de la BD, una sola vez por capa
const cache = {};
const geo = (nombre) => (cache[nombre] = cache[nombre] || pedir(`/api/capas/${nombre}`));

function unaVez(fn) {
  let hecho = null;
  return () => (hecho = hecho || fn().catch((e) => { hecho = null; console.warn(e); }));
}

function pArista(id) {
  const u = estado.ultimo;
  if (u && u.probabilidades) return Number(u.probabilidades.aristas[id] ?? 0);
  return Number((estado.propsArista[id] || {}).pf_total ?? 0);
}
function pNodo(id, props) {
  const u = estado.ultimo;
  if (u && u.probabilidades) return Number(u.probabilidades.nodos[id] ?? 0);
  return Number(props.pf_total ?? 0);
}

function popupArista(id) {
  const props = estado.propsArista[id] || {};
  const p = pArista(id);
  let extra = `<p class="nota">p de falla con lo que se considera ahora: <b>${num(p, 5)}</b> · umbral 0–100: <b>${num(100 * (1 - p), 3)}</b></p>`;
  const t = estado.sorteo && estado.sorteo.tiradas_rutas.aristas[id];
  if (t) extra += `<p class="nota">Último sorteo: n = ${num(t.n, 3)} ${t.falla ? '>' : '≤'} ${num(t.umbral, 3)} → ${t.falla ? '<b>falla</b>' : 'no falla'}</p>`;
  const exc = estado.ultimo && (estado.ultimo.excluidas || []).find((x) => x.id === id);
  if (exc) extra += `<p class="nota">No sobrevolable: ${esc(MOTIVOS[exc.motivo].texto)} (obstáculo ${num(exc.obstaculo_m, 1)} m, umbral ${num(exc.umbral_m, 1)} m)</p>`;
  return tabla(props, `Tramo ${id}`) + extra;
}

const CARGADORES = {
  aristas: unaVez(async () => {
    const datos = await geo('aristas');
    L.geoJSON(datos, {
      style: (f) => ({ color: colorP(f.properties.pf_total), weight: 2, opacity: 0.85 }),
      onEachFeature: (f, l) => {
        estado.capaArista[f.properties.id] = l;
        estado.propsArista[f.properties.id] = f.properties;
        l.bindPopup(() => popupArista(f.properties.id), { maxWidth: 340 });
      },
    }).addTo(capa.aristas);
  }),
  nodos: unaVez(async () => {
    const datos = await geo('nodos');
    L.geoJSON(datos, {
      pointToLayer: (f, ll) => {
        const m = L.circleMarker(ll, { radius: 4, weight: 1, color: '#374151', fillOpacity: 0.9, fillColor: colorP(f.properties.pf_total) });
        m.feature = f;
        return m;
      },
      onEachFeature: (f, l) => l.bindPopup(() => {
        const p = pNodo(f.properties.id, f.properties);
        const t = estado.sorteo && estado.sorteo.tiradas_rutas.nodos[f.properties.id];
        return tabla(f.properties, `Nodo ${f.properties.id}`)
          + `<p class="nota">p de falla con lo que se considera ahora: <b>${num(p, 5)}</b></p>`
          + (t ? `<p class="nota">Último sorteo: n = ${num(t.n, 3)} ${t.falla ? '>' : '≤'} ${num(t.umbral, 3)} → ${t.falla ? '<b>falla</b>' : 'no falla'}</p>` : '');
      }),
    }).addTo(capa.nodos);
  }),
  elevacion: unaVez(async () => {
    const datos = await geo('nodos');
    const elev = datos.features.map((f) => f.properties.elevacion_m).filter((x) => !vacio(x));
    const min = Math.min(...elev);
    const max = Math.max(...elev);
    L.geoJSON(datos, {
      pointToLayer: (f, ll) => L.circleMarker(ll, {
        radius: 6, weight: 0, fillOpacity: 0.85,
        fillColor: vacio(f.properties.elevacion_m) ? '#9ca3af' : colorElevacion((f.properties.elevacion_m - min) / ((max - min) || 1)),
      }),
      onEachFeature: (f, l) => l.bindPopup(tabla({ id: f.properties.id, elevacion_m: f.properties.elevacion_m },
        `Elevación (Copernicus GLO-90): ${num(min, 0)} a ${num(max, 0)} m en el AOI`)),
    }).addTo(capa.elevacion);
  }),
  mision: unaVez(async () => {
    const datos = await geo('mision');
    estado.mision = datos;
    if (!estado.puntos) restaurarPuntos();
    L.geoJSON(datos, {
      pointToLayer: (f, ll) => L.circleMarker(ll, { radius: 7, color: '#111827', weight: 2, fillColor: '#fde047', fillOpacity: 1 }),
      onEachFeature: (f, l) => l.bindPopup(tabla(f.properties, 'Punto de la misión')),
    }).addTo(capa.mision);
    capaPuntos.addTo(capa.mision);
  }),
  edificios: unaVez(async () => {
    L.geoJSON(await geo('edificios'), {
      style: (f) => ({ color: f.properties.altura_m ? '#475569' : '#94a3b8', weight: 0.5, fillOpacity: f.properties.altura_m ? 0.5 : 0.15 }),
      onEachFeature: (f, l) => l.bindPopup(tabla(f.properties, 'Edificio OSM')),
    }).addTo(capa.edificios);
  }),
  zonas_restringidas: unaVez(async () => {
    L.geoJSON(await geo('zonas_restringidas'), {
      style: () => ({ color: MOTIVOS.zona_publicada.color, weight: 2, fillOpacity: 0.15, dashArray: '4 4' }),
      onEachFeature: (f, l) => l.bindPopup(tabla(f.properties, 'Zona restringida publicada (OSM aeroway)')),
    }).addTo(capa.zonas_restringidas);
  }),
  gpsjam: unaVez(async () => {
    L.geoJSON(await geo('gpsjam'), {
      style: (f) => {
        const p = f.properties.frac_dias_rojos;
        return { color: '#7c3aed', weight: 1, fillColor: p ? '#dc2626' : '#7c3aed', fillOpacity: p ? 0.08 + 0.4 * p : 0.03 };
      },
      onEachFeature: (f, l) => l.bindPopup(tabla(f.properties, 'GPSJam: degradación GNSS (celda H3)')),
    }).addTo(capa.gpsjam);
  }),
  incendios: unaVez(async () => {
    L.geoJSON(await geo('incendios'), {
      pointToLayer: (f, ll) => L.circleMarker(ll, { radius: 4, weight: 0, fillOpacity: 0.8, fillColor: f.properties.periodo === 'evaluacion' ? '#7f1d1d' : '#f97316' }),
      onEachFeature: (f, l) => l.bindPopup(tabla(f.properties, 'Incendio de guerra (The Economist / FIRMS)')),
    }).addTo(capa.incendios);
  }),
  eventos: unaVez(async () => {
    L.geoJSON(await geo('eventos'), {
      pointToLayer: (f, ll) => L.circleMarker(ll, { radius: 5, color: '#111827', weight: 1, fillColor: '#111827', fillOpacity: 0.4 }),
      onEachFeature: (f, l) => l.bindPopup(tabla(f.properties, 'Evento UCDP')),
    }).addTo(capa.eventos);
  }),
};

function recolorear() {
  Object.entries(estado.capaArista).forEach(([id, l]) => l.setStyle({ color: colorP(pArista(id)) }));
  capa.nodos.eachLayer((g) => g.eachLayer && g.eachLayer((m) => {
    if (m.feature) m.setStyle({ fillColor: colorP(pNodo(m.feature.properties.id, m.feature.properties)) });
  }));
}

// Viento: no es un polígono, así que va como un control con flecha y detalle al pulsarlo.
const controlViento = L.control({ position: 'topleft' });
controlViento.onAdd = () => {
  const div = L.DomUtil.create('div', 'viento');
  div.innerHTML = '<div class="flecha">↑</div><div class="txt">viento…</div><div class="detalle" hidden></div>';
  L.DomEvent.disableClickPropagation(div);
  div.addEventListener('click', () => { const d = div.querySelector('.detalle'); d.hidden = !d.hidden; });
  div.title = 'Viento representativo de la ventana (pulsa para ver el detalle)';
  return div;
};
controlViento.addTo(mapa);

function pintarViento(v) {
  estado.viento = v;
  const div = controlViento.getContainer();
  if (!v || vacio(v.velocidad_a_altura_vuelo_m_s)) {
    div.querySelector('.txt').textContent = 'sin datos de viento';
    return;
  }
  const hacia = (Number(v.direccion_desde_grados) + 180) % 360;
  div.querySelector('.flecha').style.transform = `rotate(${hacia}deg)`;
  div.querySelector('.txt').innerHTML = `<b>${num(v.velocidad_a_altura_vuelo_m_s, 1)} m/s</b><br>desde ${num(v.direccion_desde_grados, 0)}°`;
  div.querySelector('.detalle').innerHTML = tabla({
    'fuente': v.fuente, 'horas': v.horas, 'desde': String(v.desde || '').slice(0, 10), 'hasta': String(v.hasta || '').slice(0, 10),
    'mediana a 100 m (m/s)': v.mediana_100m_m_s, 'p95 a 100 m (m/s)': v.p95_100m_m_s, 'ráfaga máx. a 10 m (m/s)': v.rafaga_max_10m_m_s,
    'a la altura de vuelo (m/s)': v.velocidad_a_altura_vuelo_m_s,
  }) + '<p class="nota">Entra al costo como factor de viento de frente v / (v − h), distinto en cada sentido del tramo.</p>';
}

// Leyenda: algoritmo, tiempo de cómputo y resiliencia de cada ruta (punto 8)
const leyenda = L.control({ position: 'bottomright' });
leyenda.onAdd = () => L.DomUtil.create('div', 'leyenda');
leyenda.addTo(mapa);

function actualizarLeyenda() {
  const u = estado.ultimo;
  const filas = Object.entries(TECNICAS).map(([k, t]) => {
    const r = u && (u.tecnicas || []).find((x) => x.clave === k);
    const estrella = u && u.mas_resiliente === k ? '★ ' : '';
    const datos = r && r.coordenadas
      ? ` · ${num(r.tiempo_ms, 1)} ms · R = ${pct(r.resiliencia, 1)} · F = ${num(r.fiabilidad, 3)} · ${num(r.largo_km, 2)} km`
      : (r && r.error ? ' · sin ruta' : '');
    return `<div class="${estrella ? 'mejor' : ''}"><span class="linea" style="border-color:${t.color};border-top-style:${t.dash ? 'dashed' : 'solid'}"></span>${estrella}${t.nombre}${datos}</div>`;
  });
  const pie = u
    ? `<div class="pie">R = misiones completadas en ${esc(u.resiliencia ? u.resiliencia.n_sorteos : 0)} sorteos · F = ∏(1 − p) · ★ más resiliente</div>`
    : '<div class="pie">Calcula una consulta para ver tiempo de cómputo y resiliencia.</div>';
  leyenda.getContainer().innerHTML = `${filas.join('')}${pie}
    <div>p de falla del tramo: 0 <span class="barra"></span> ≥ ${num(P_ESCALA, 2)}</div>`;
}

// ---------------------------------------------------------------------------
// Origen, destino y puntos de observación
// ---------------------------------------------------------------------------
const marcadores = { origen: null, destino: null };

function fijar(tipo, latlng) {
  estado[tipo] = { lat: latlng.lat, lon: latlng.lng };
  if (marcadores[tipo]) marcadores[tipo].remove();
  marcadores[tipo] = L.circleMarker(latlng, { radius: 9, color: '#fff', weight: 2, fillColor: COLOR[tipo], fillOpacity: 1 })
    .bindTooltip(tipo === 'origen' ? 'Origen' : 'Destino').addTo(mapa);
  $(`txt-${tipo}`).textContent = `${latlng.lat.toFixed(5)}, ${latlng.lng.toFixed(5)}`;
  describirSecuencia();
}

function quitar(tipo) {
  estado[tipo] = null;
  if (marcadores[tipo]) marcadores[tipo].remove();
  marcadores[tipo] = null;
  $(`txt-${tipo}`).textContent = 'sin definir';
  describirSecuencia();
}

function ordenarMision() {
  if (!estado.mision) return [];
  return estado.mision.features.slice().sort((a, b) => a.properties.orden - b.properties.orden)
    .map((f) => ({ lat: f.geometry.coordinates[1], lon: f.geometry.coordinates[0], rol: f.properties.rol }));
}

const capaPuntos = L.layerGroup();
let modoAnadir = false;

function dibujarPuntos() {
  capaPuntos.clearLayers();
  (estado.puntos || []).forEach((p, i) => {
    const icono = L.divIcon({ className: '', iconSize: [16, 16], iconAnchor: [8, 8],
      html: `<span class="punto-obs" title="Punto de observación ${i + 1}: arrastra para moverlo, pulsa para quitarlo"></span>` });
    const m = L.marker([p.lat, p.lon], { draggable: true, icon: icono, zIndexOffset: 500 })
      .bindTooltip(`P${i + 1}`, { permanent: true, direction: 'top', className: 'etiqueta-punto' })
      .addTo(capaPuntos);
    m.on('dragend', () => {
      const ll = m.getLatLng();
      estado.puntos[i] = { lat: ll.lat, lon: ll.lng };
      describirSecuencia();
    });
    m.on('click', (ev) => {
      L.DomEvent.stop(ev);
      estado.puntos.splice(i, 1);
      dibujarPuntos();
    });
  });
  describirSecuencia();
}

function restaurarPuntos() {
  estado.puntos = ordenarMision().slice(1, -1).map((p) => ({ lat: p.lat, lon: p.lon }));
  dibujarPuntos();
}

function anadirPunto(latlng) {
  (estado.puntos = estado.puntos || []).push({ lat: latlng.lat, lon: latlng.lng });
  modoAnadir = false;
  $('btn-anadir-punto').classList.remove('activo');
  $('btn-anadir-punto').textContent = 'Añadir punto';
  dibujarPuntos();
}

function describirSecuencia() {
  const n = (estado.puntos || []).length;
  const origen = estado.origen ? 'el origen marcado' : 'el inicio de la misión';
  const destino = estado.destino ? 'el destino marcado' : 'el destino de la misión';
  const medio = n ? `${n} punto${n === 1 ? '' : 's'} de observación` : 'ningún punto intermedio';
  $('txt-secuencia').textContent = `Se simulará: ${origen} → ${medio} → ${destino}.`
    + (n ? '' : ' Sin puntos intermedios la flota vuela directo y la misión deja de ser una inspección.');
}

$('btn-anadir-punto').addEventListener('click', () => {
  terminarDibujo();
  modoAnadir = !modoAnadir;
  const b = $('btn-anadir-punto');
  b.classList.toggle('activo', modoAnadir);
  b.textContent = modoAnadir ? 'Pulsa en el mapa…' : 'Añadir punto';
});
$('btn-restaurar-puntos').addEventListener('click', restaurarPuntos);

$('btn-limpiar').addEventListener('click', () => { quitar('origen'); quitar('destino'); });

$('btn-mision').addEventListener('click', async () => {
  try {
    if (!estado.mision) estado.mision = await geo('mision');
    const puntos = ordenarMision();
    if (puntos.length < 2) throw new Error('La misión no tiene inicio y destino.');
    fijar('origen', L.latLng(puntos[0].lat, puntos[0].lon));
    fijar('destino', L.latLng(puntos[puntos.length - 1].lat, puntos[puntos.length - 1].lon));
    restaurarPuntos();
  } catch (e) {
    mostrarEstado(`No se pudo leer la misión: ${e.message}`, true);
  }
});

// ---------------------------------------------------------------------------
// Zonas del usuario: prohibidas (polígono) y de amenaza (disco con p)
// ---------------------------------------------------------------------------
const dibujo = { modo: null, vertices: [], previa: null };

function terminarDibujo() {
  dibujo.modo = null;
  dibujo.vertices = [];
  if (dibujo.previa) dibujo.previa.remove();
  dibujo.previa = null;
  mapa.doubleClickZoom.enable();
  $('btn-zona-prohibida').classList.remove('activo');
  $('btn-zona-amenaza').classList.remove('activo');
  $('btn-terminar-zona').hidden = true;
  $('txt-dibujo').textContent = '';
  mapa.getContainer().classList.remove('dibujando');
}

function empezarDibujo(modo) {
  const mismo = dibujo.modo === modo;
  terminarDibujo();
  if (mismo) return;
  modoAnadir = false;
  dibujo.modo = modo;
  mapa.getContainer().classList.add('dibujando');
  if (modo === 'prohibida') {
    mapa.doubleClickZoom.disable();
    $('btn-zona-prohibida').classList.add('activo');
    $('btn-terminar-zona').hidden = false;
    $('txt-dibujo').textContent = 'Pulsa los vértices en el mapa; doble clic (o «Cerrar el polígono») para terminar.';
  } else {
    $('btn-zona-amenaza').classList.add('activo');
    $('txt-dibujo').textContent = 'Pulsa en el mapa el centro de la zona de amenaza.';
  }
}

function agregarVertice(ll) {
  const ultimo = dibujo.vertices[dibujo.vertices.length - 1];
  if (ultimo && Math.abs(ultimo[0] - ll.lat) < 1e-7 && Math.abs(ultimo[1] - ll.lng) < 1e-7) return;
  dibujo.vertices.push([ll.lat, ll.lng]);
  if (dibujo.previa) dibujo.previa.remove();
  dibujo.previa = L.polyline(dibujo.vertices, { color: MOTIVOS.zona_usuario.color, weight: 2, dashArray: '4 4' }).addTo(mapa);
}

function cerrarPoligono() {
  if (dibujo.vertices.length >= 3) {
    estado.zonas.push({ tipo: 'prohibida', vertices: dibujo.vertices.slice() });
    zonasCambiaron();
  }
  terminarDibujo();
}

function crearAmenaza(ll) {
  const radio = Number($('zona-radio').value) || 400;
  const p = Math.min(0.99, Math.max(0.01, Number($('zona-p').value) || 0.5));
  estado.zonas.push({ tipo: 'amenaza', lat: ll.lat, lon: ll.lng, radio_m: radio, p });
  terminarDibujo();
  zonasCambiaron();
}

function zonasCambiaron() {
  dibujarZonas();
  if (estado.ultimo) $('txt-recalcular').hidden = false;
}

function dibujarZonas() {
  capa.zonas_usuario.clearLayers();
  estado.zonas.forEach((z, i) => {
    const comun = { bubblingMouseEvents: false };
    const boton = `<br><button type="button" class="mini" data-quitar-zona="${i}">Quitar esta zona</button>`;
    const l = z.tipo === 'prohibida'
      ? L.polygon(z.vertices, { ...comun, color: MOTIVOS.zona_usuario.color, weight: 2, fillOpacity: 0.12, dashArray: '6 4' })
        .bindPopup(`<b>Zona prohibida ${i + 1}</b><br>Ningún tramo que la toque es sobrevolable.${boton}`)
      : L.circle([z.lat, z.lon], { ...comun, radius: z.radio_m, color: '#d97706', weight: 2, fillColor: '#f59e0b', fillOpacity: 0.2 })
        .bindPopup(`<b>Zona de amenaza ${i + 1}</b> (modelo abstracto)<br>radio ${num(z.radio_m, 0)} m · p de falla ${num(z.p, 2)}
          al tocarla<br>Se suma a la p de cada tramo y nodo que toca.${boton}`);
    l.addTo(capa.zonas_usuario);
  });
  const nP = estado.zonas.filter((z) => z.tipo === 'prohibida').length;
  const nA = estado.zonas.length - nP;
  $('txt-zonas').textContent = estado.zonas.length
    ? `${nP} zona${nP === 1 ? '' : 's'} prohibida${nP === 1 ? '' : 's'} y ${nA} de amenaza. Pulsa una zona para quitarla.`
    : 'Sin zonas.';
}

mapa.on('popupopen', (ev) => {
  const b = ev.popup.getElement().querySelector('[data-quitar-zona]');
  if (b) b.addEventListener('click', () => { estado.zonas.splice(Number(b.dataset.quitarZona), 1); mapa.closePopup(); zonasCambiaron(); });
});

$('btn-zona-prohibida').addEventListener('click', () => empezarDibujo('prohibida'));
$('btn-zona-amenaza').addEventListener('click', () => empezarDibujo('amenaza'));
$('btn-terminar-zona').addEventListener('click', cerrarPoligono);
$('btn-borrar-zonas').addEventListener('click', () => { estado.zonas = []; terminarDibujo(); zonasCambiaron(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') terminarDibujo(); });

mapa.on('click', (e) => {
  if (modoAnadir) { anadirPunto(e.latlng); return; }
  if (dibujo.modo === 'prohibida') { agregarVertice(e.latlng); return; }
  if (dibujo.modo === 'amenaza') { crearAmenaza(e.latlng); return; }
  if (!estado.origen || estado.destino) {
    quitar('destino');
    fijar('origen', e.latlng);
  } else {
    fijar('destino', e.latlng);
  }
});
mapa.on('dblclick', () => { if (dibujo.modo === 'prohibida') cerrarPoligono(); });

// ---------------------------------------------------------------------------
// Restricciones del usuario (punto 3)
// ---------------------------------------------------------------------------
const CAMPOS = ['altura_vuelo_m', 'margen_vertical_m', 'autonomia_km', 'prob_exito_min', 'viento_max_m_s',
  'velocidad_crucero_m_s', 'desvio_max', 'presupuesto_extra', 'peso_riesgo'];
const CAMPOS_ACO = ['n_hormigas', 'iteraciones', 'alfa', 'beta', 'gamma', 'rho', 'semilla'];

function llenarPreferencias(p) {
  const f = $('form-prefs');
  CAMPOS.forEach((c) => { if (c in p) f.elements[c].value = p[c] ?? ''; });
  if ('respetar_zonas_restringidas' in p) f.elements.respetar_zonas_restringidas.checked = !!p.respetar_zonas_restringidas;
}

function leerPreferencias() {
  const f = $('form-prefs');
  const p = {};
  CAMPOS.forEach((c) => {
    const v = f.elements[c].value;
    if (v !== '') p[c] = Number(v);
  });
  p.respetar_zonas_restringidas = f.elements.respetar_zonas_restringidas.checked;
  return p;
}

function leerACO() {
  const f = $('form-prefs');
  const a = {};
  CAMPOS_ACO.forEach((c) => { const v = f.elements[`aco_${c}`].value; if (v !== '') a[c] = Number(v); });
  return a;
}

function aplicarPerfil(clave) {
  const perfil = estado.perfiles[clave] || {};
  const valores = { ...estado.defecto };
  Object.entries(perfil).forEach(([k, v]) => { if (k !== 'nombre') valores[k] = v; });
  llenarPreferencias(valores);
}

$('sel-perfil').addEventListener('change', (e) => aplicarPerfil(e.target.value));
$('btn-defecto').addEventListener('click', () => { if (estado.defecto) aplicarPerfil($('sel-perfil').value); });

function textoViento(v) {
  if (!v || vacio(v.velocidad_a_altura_vuelo_m_s)) return (v && v.nota) || 'Sin datos de viento.';
  return `Viento representativo (mediana ${String(v.desde || '').slice(0, 10)} a ${String(v.hasta || '').slice(0, 10)}): `
    + `${num(v.mediana_100m_m_s, 1)} m/s a 100 m, ${num(v.velocidad_a_altura_vuelo_m_s, 1)} m/s a la altura de vuelo, `
    + `desde ${num(v.direccion_desde_grados, 0)}°.`;
}

function mostrarEstado(texto, error = false) {
  const p = $('txt-estado');
  p.textContent = texto;
  p.className = error ? 'aviso error' : 'ayuda';
}

// ---------------------------------------------------------------------------
// Las cuatro técnicas (puntos 6 y 8)
// ---------------------------------------------------------------------------
function cuerpoConsulta() {
  const f = $('form-prefs');
  return {
    origen: estado.origen,
    destino: estado.destino,
    puntos: $('chk-puntos').checked ? (estado.puntos || []) : [],
    preferencias: leerPreferencias(),
    considerar: { ...estado.considerar },
    zonas_prohibidas: estado.zonas.filter((z) => z.tipo === 'prohibida').map((z) => ({ vertices: z.vertices.map(([lat, lon]) => ({ lat, lon })) })),
    zonas_amenaza: estado.zonas.filter((z) => z.tipo === 'amenaza').map(({ lat, lon, radio_m, p }) => ({ lat, lon, radio_m, p })),
    aco: leerACO(),
    n_sorteos: vacio(f.elements.n_sorteos.value) ? 300 : Number(f.elements.n_sorteos.value),
    prob_deteccion: vacio(f.elements.prob_deteccion.value) ? 0.5 : Number(f.elements.prob_deteccion.value),
  };
}

function popupTecnica(r) {
  const t = TECNICAS[r.clave];
  return `<b style="color:${t.color}">${esc(t.nombre)}</b><table class="popup">
    <tr><th>largo</th><td>${num(r.largo_m, 0)} m</td></tr>
    <tr><th>tiempo de vuelo</th><td>${num(r.tiempo_vuelo_min, 1)} min</td></tr>
    <tr><th>fiabilidad F</th><td>${num(r.fiabilidad, 4)}</td></tr>
    <tr><th>resiliencia R</th><td>${pct(r.resiliencia, 1)}</td></tr>
    <tr><th>cómputo</th><td>${num(r.tiempo_ms, 1)} ms</td></tr>
    <tr><th>autonomía / R<sub>min</sub></th><td>${si(r.cumple_autonomia)} / ${si(r.cumple_fiabilidad)}</td></tr></table>`;
}

function dibujarTecnicas(res, ajustar) {
  const lineas = [];
  Object.keys(TECNICAS).forEach((k) => capa[`ruta_${k}`].clearLayers());
  (res.tecnicas || []).forEach((r) => {
    if (!r.coordenadas) return;
    const t = TECNICAS[r.clave];
    const linea = L.polyline(r.coordenadas, { color: t.color, weight: t.peso, opacity: t.opacidad, dashArray: t.dash })
      .bindPopup(popupTecnica(r));
    linea.addTo(capa[`ruta_${r.clave}`]);
    lineas.push(linea);
  });
  if (ajustar && lineas.length) mapa.fitBounds(L.featureGroup(lineas).getBounds(), { padding: [40, 40] });
}

function dibujarExcluidas(res) {
  capa.excluidas.clearLayers();
  (res.excluidas || []).forEach((x) => {
    const l = estado.capaArista[x.id];
    if (!l) return;
    L.polyline(l.getLatLngs(), { color: MOTIVOS[x.motivo].color, weight: 3, opacity: 0.9, dashArray: '1 5', lineCap: 'round' })
      .bindPopup(`<b>Tramo ${x.id}: no sobrevolable</b><br>${esc(MOTIVOS[x.motivo].texto)}`
        + (vacio(x.obstaculo_m) ? '' : `<br>obstáculo ${num(x.obstaculo_m, 1)} m sobre el despegue ≥ ${num(x.umbral_m, 1)} m`))
      .addTo(capa.excluidas);
  });
}

function detalleTecnica(r, milp) {
  const d = r.detalle || {};
  const tramos = d.tramos || [d];
  const suma = (k) => tramos.reduce((a, x) => a + (Number(x[k]) || 0), 0);
  const brecha = milp && milp.objetivo_km_eq && r.objetivo_km_eq ? 100 * (r.objetivo_km_eq / milp.objetivo_km_eq - 1) : null;
  const brechaTxt = brecha === null || r.clave === 'milp_gurobi' ? '' : ` Objetivo frente al óptimo del MILP: ${brecha > 0 ? '+' : ''}${num(brecha, 2)} %.`;
  if (r.clave === 'dijkstra_m') {
    return `Costo = <code>largo_m</code> en ambos sentidos; ignora amenazas, viento, autonomía y R<sub>min</sub>.${brechaTxt}
      <br><code class="sql">${esc(tramos[0].consulta || '')}</code>`;
  }
  if (r.clave === 'milp_gurobi') {
    const t0 = tramos[0];
    return `Estado: ${esc(t0.estado || '—')}; ${num(suma('n_variables'), 0)} variables binarias y ${num(suma('n_restricciones'), 0)}
      restricciones (licencia restringida: ${num(t0.limite_licencia, 0)}); poda exacta por elipse: ${num(suma('arcos_tras_poda'), 0)}
      de ${num(suma('arcos_sobrevolables'), 0)} arcos; tiempo de Gurobi ${num(suma('runtime_gurobi_ms'), 1)} ms; brecha ${num(t0.gap, 4)}.
      ${tramos.some((x) => x.modelo_secundario) ? '<br><b>R<sub>min</sub> no alcanzable</b>: se resolvió máxima fiabilidad dentro de la autonomía.' : ''}
      ${t0.nota ? `<br>${esc(t0.nota)}` : ''}`;
  }
  if (r.clave === 'dijkstra_ponderado') {
    return `Costo = 1000 · (c + λ · l), con c = km con viento y l = −ln(1 − p). λ = ${tramos.map((x) => num(x.lambda_m, 0)).join(' / ')} m,
      hallado por bisección (${num(suma('llamadas_dijkstra'), 0)} llamadas a <code>pgr_dijkstra</code>).${brechaTxt}
      ${tramos.some((x) => x.cumple_fiabilidad === false) ? '<br>Ni con el mayor λ se alcanza R<sub>min</sub>.' : ''}
      <br><code class="sql">${esc(tramos[0].consulta || '')}</code>`;
  }
  const p = tramos[0].parametros || {};
  return `${num(suma('iteraciones'), 0)} iteraciones (mejor en la ${tramos.map((x) => num(x.mejor_iteracion, 0)).join(' / ')}),
    ${num(suma('hormigas_validas'), 0)} de ${num(suma('hormigas_totales'), 0)} hormigas llegaron al destino.
    Parámetros: ${num(p.n_hormigas, 0)} hormigas, α = ${num(p.alfa)}, β = ${num(p.beta)}, γ = ${num(p.gamma)}, ρ = ${num(p.rho)},
    semilla ${esc(p.semilla)}.${brechaTxt}${tramos.some((x) => x.factible === false) ? '<br><b>La mejor ruta viola una restricción.</b>' : ''}`;
}

function mostrarT3(res) {
  const milp = (res.tecnicas || []).find((r) => r.clave === 'milp_gurobi' && r.coordenadas);
  const filas = (res.tecnicas || []).map((r) => {
    const t = TECNICAS[r.clave];
    const estrella = res.mas_resiliente === r.clave ? '★ ' : '';
    if (!r.coordenadas) return `<tr><td>${t.nombre}</td><td colspan="6">${esc(r.error || 'sin ruta')}</td></tr>`;
    return `<tr class="${estrella ? 'mejor' : ''}"><td><span class="linea" style="border-color:${t.color};border-top-style:${t.dash ? 'dashed' : 'solid'}"></span>${estrella}${t.nombre}</td>
      <td>${num(r.largo_km, 2)}</td><td>${num(r.tiempo_vuelo_min, 1)}</td><td>${num(r.fiabilidad, 3)}</td>
      <td><b>${pct(r.resiliencia, 1)}</b></td><td>${si(r.cumple_autonomia)}${si(r.cumple_fiabilidad)}</td><td>${num(r.tiempo_ms, 1)}</td></tr>`;
  });
  const ev = res.resiliencia || {};
  const difs = Object.entries(ev.diferencial_vs_dijkstra_m || {}).map(([k, d]) => {
    const v = Number(d.delta_R_pp);
    return `<li>${esc(TECNICAS[k].nombre)}: <strong class="${v > 0 ? 'pos' : (v < 0 ? 'neg' : '')}">${v > 0 ? '+' : ''}${num(v, 1)} pp</strong>
      <span class="ayuda">(solo ella completa ${esc(d.solo_tecnica_completa)}, solo Dijkstra ${esc(d.solo_dijkstra_m_completa)}; McNemar p ${d.p_mcnemar < 1e-4 ? '< 0,0001' : `= ${num(d.p_mcnemar, 4)}`})</span></li>`;
  });
  const motivos = {};
  (res.excluidas || []).forEach((x) => { motivos[x.motivo] = (motivos[x.motivo] || 0) + 1; });
  const txtMotivos = Object.entries(motivos).map(([m, n]) => `${n} por ${m.replace('_', ' ')}`).join(', ') || 'ninguno';
  const activas = (res.probabilidades && res.probabilidades.activas) || [];
  const avisos = (res.advertencias || []).map((a) => `<div class="aviso">${esc(a)}</div>`).join('');
  const mejor = res.mas_resiliente ? TECNICAS[res.mas_resiliente].nombre : '—';
  const detalles = (res.tecnicas || []).filter((r) => r.coordenadas).map((r) => `<details><summary>${TECNICAS[r.clave].nombre}</summary>
    <p class="ayuda">${detalleTecnica(r, milp)}</p></details>`).join('');
  $('contenido-t3').innerHTML = `
    ${avisos}
    <table>
      <thead><tr><th>Técnica</th><th>km</th><th>vuelo (min)</th><th>F</th><th>R</th><th>aut. / R<sub>min</sub></th><th>cómputo (ms)</th></tr></thead>
      <tbody>${filas.join('')}</tbody>
    </table>
    <p>Más resiliente: <strong>★ ${esc(mejor)}</strong></p>
    <p class="ayuda">Nodos ${esc((res.secuencia || []).join(' → '))}. Autonomía ${num(res.autonomia_km)} km (ruta sobrevolable más corta:
      ${num(res.largo_minimo_km)} km); R<sub>min</sub> = ${num(res.r_min, 2)}. Amenazas consideradas: ${esc(activas.join(', ') || 'ninguna')}.
      Tramos no sobrevolables: ${(res.excluidas || []).length} (${esc(txtMotivos)}).</p>
    <p class="ayuda"><b>F</b> = ∏(1 − p) de tramos y nodos de la ruta. <b>R</b> = misiones completadas dentro de la autonomía en
      ${esc(ev.n_sorteos ?? 0)} sorteos 0–100 (los mismos para las cuatro): el UAV nota cada falla antes de entrar con probabilidad
      ${num(ev.prob_deteccion, 2)} y se desvía con Dijkstra ponderado; si no la nota, se pierde.</p>
    <h3>Diferencia de resiliencia frente a pgr_dijkstra (metros)</h3>
    <ul class="difs">${difs.join('')}</ul>
    <h3>Cómo resolvió cada técnica</h3>
    ${detalles}`;
}

async function calcular() {
  if (!estado.origen || !estado.destino) {
    mostrarEstado('Define el origen y el destino haciendo clic en el mapa (o usa la misión).', true);
    return null;
  }
  const cuerpo = cuerpoConsulta();
  const boton = $('btn-calcular');
  boton.disabled = true;
  mostrarEstado('Calculando las cuatro técnicas y los sorteos de resiliencia…');
  try {
    const res = await postJSON('/api/t3/rutas', cuerpo);
    await CARGADORES.aristas();
    estado.ultimo = res;
    estado.ultimoCuerpo = cuerpo;
    estado.sorteo = null;
    capa.fallas.clearLayers();
    capa.vuelos.clearLayers();
    $('contenido-sorteo').innerHTML = '';
    $('txt-sorteo').textContent = 'Listo para sortear.';
    $('txt-recalcular').hidden = true;
    dibujarTecnicas(res, true);
    dibujarExcluidas(res);
    recolorear();
    mostrarT3(res);
    actualizarLeyenda();
    if (res.viento) pintarViento(res.viento);
    mostrarEstado(res.id_evaluacion ? `Guardado en la BD (evaluación ${res.id_evaluacion} de evaluaciones_t3).` : 'Listo.');
    return res;
  } catch (e) {
    mostrarEstado(`Error: ${e.message}`, true);
    return null;
  } finally {
    boton.disabled = false;
  }
}

$('form-prefs').addEventListener('submit', (ev) => { ev.preventDefault(); calcular(); });

// ---------------------------------------------------------------------------
// Sorteo 0-100 (punto 7)
// ---------------------------------------------------------------------------
function textoVuelo(r) {
  const rec = r.recuperacion;
  if (r.intacta) return rec.exito ? `Intacta: completa (${num(rec.km, 2)} km)` : 'Intacta, pero excede la autonomía';
  const desvios = (rec.desvios || []).length;
  if (rec.exito) return `Notó ${desvios} falla${desvios === 1 ? '' : 's'}, se desvió y completó (${num(rec.km, 2)} km)`;
  if (rec.motivo === 'perdido') return `Entró sin notarla al ${esc(rec.perdido_en.tipo)} ${esc(rec.perdido_en.id)}: UAV perdido`;
  if (rec.motivo === 'sin_alternativa') return 'Notó la falla, pero no quedó ruta';
  if (rec.motivo === 'autonomia') return 'Se desvió, pero agotó la autonomía';
  return esc(rec.motivo);
}

function dibujarSorteo(s) {
  capa.fallas.clearLayers();
  capa.vuelos.clearLayers();
  s.tramos_fallados.forEach((x) => {
    const l = estado.capaArista[x.id];
    if (!l) return;
    L.polyline(l.getLatLngs(), { color: '#dc2626', weight: 6, opacity: 0.9, dashArray: '6 5' })
      .bindPopup(`<b>Tramo ${x.id} falla</b><br>n = ${num(x.n, 3)} &gt; umbral ${num(x.umbral, 3)} (p = ${num(x.p, 5)})`)
      .addTo(capa.fallas);
  });
  s.nodos_fallados.forEach((x) => {
    L.marker([x.lat, x.lon], { icon: L.divIcon({ className: '', iconSize: [18, 18], iconAnchor: [9, 9], html: '<span class="nodo-falla">✕</span>' }) })
      .bindPopup(`<b>Nodo ${x.id} falla</b><br>n = ${num(x.n, 3)} &gt; umbral ${num(x.umbral, 3)} (p = ${num(x.p, 5)})<br>Sus tramos quedan inutilizables.`)
      .addTo(capa.fallas);
  });
  Object.entries(s.por_tecnica).forEach(([k, r]) => {
    const rec = r.recuperacion;
    if (!rec.coordenadas || rec.coordenadas.length < 1) return;
    const t = TECNICAS[k];
    if (rec.coordenadas.length > 1) {
      L.polyline(rec.coordenadas, { color: t.color, weight: 3, opacity: 1, dashArray: '1 6', lineCap: 'round' })
        .bindPopup(`<b>${esc(t.nombre)}</b> tras el sorteo: ${textoVuelo(r)}`).addTo(capa.vuelos);
    }
    const fin = rec.coordenadas[rec.coordenadas.length - 1];
    const icono = rec.exito ? '✓' : '✕';
    L.marker(fin, { icon: L.divIcon({ className: '', iconSize: [20, 20], iconAnchor: [10, 10],
      html: `<span class="fin-vuelo" style="background:${t.color}">${icono}</span>` }) })
      .bindPopup(`<b>${esc(t.nombre)}</b>: ${textoVuelo(r)}`).addTo(capa.vuelos);
  });
}

function mostrarSorteo(s) {
  const filas = Object.entries(s.por_tecnica).map(([k, r]) => {
    const t = TECNICAS[k];
    const pf = r.primer_fallo;
    const primero = pf ? `${pf.tipo} ${pf.id}: n = ${num(pf.n, 2)} &gt; ${num(pf.umbral, 2)}` : '—';
    return `<tr><td><span class="linea" style="border-color:${t.color};border-top-style:${t.dash ? 'dashed' : 'solid'}"></span>${t.nombre}</td>
      <td>${si(r.intacta)}</td><td>${primero}</td><td>${si(r.recuperacion.exito)} ${textoVuelo(r)}</td></tr>`;
  });
  $('contenido-sorteo').innerHTML = `
    <p class="ayuda">Semilla ${esc(s.semilla)}: fallan <b>${s.tramos_fallados.length}</b> de ${s.n_tramos} tramos y
      <b>${s.nodos_fallados.length}</b> de ${s.n_nodos} nodos (${esc(s.regla)}). Prob. de notar una falla antes de entrar:
      ${num(s.prob_deteccion, 2)}.</p>
    <table>
      <thead><tr><th>Técnica</th><th>intacta</th><th>primer fallo</th><th>vuelo</th></tr></thead>
      <tbody>${filas.join('')}</tbody>
    </table>
    <p class="ayuda">En el mapa: tramos que fallan en rojo discontinuo, nodos que fallan con ✕ y el vuelo de cada ruta afectada
      con su color (✓ completó, ✕ no). Pulsa un tramo o nodo para ver su número sorteado y su umbral.</p>`;
}

async function sortear(semilla) {
  if (!estado.ultimo || !estado.ultimoCuerpo) {
    $('txt-sorteo').textContent = 'Primero calcula las rutas.';
    return null;
  }
  if (!vacio(semilla)) $('sorteo-semilla').value = semilla;
  const rutas = {};
  (estado.ultimo.tecnicas || []).forEach((r) => { if (r.nodos) rutas[r.clave] = r.nodos; });
  const cuerpo = { ...estado.ultimoCuerpo, semilla: Number($('sorteo-semilla').value) || 0, rutas,
    lambda_recuperacion_km: estado.ultimo.lambda_recuperacion_km };
  const boton = $('btn-sortear');
  boton.disabled = true;
  $('txt-sorteo').textContent = 'Sorteando…';
  try {
    const s = await postJSON('/api/t3/sorteo', cuerpo);
    estado.sorteo = s;
    dibujarSorteo(s);
    mostrarSorteo(s);
    $('txt-sorteo').textContent = 'Sorteo listo.';
    return s;
  } catch (e) {
    $('txt-sorteo').textContent = `Error: ${e.message}`;
    return null;
  } finally {
    boton.disabled = false;
  }
}

$('btn-sortear').addEventListener('click', () => sortear());
$('btn-nueva-semilla').addEventListener('click', () => sortear(Math.floor(Math.random() * 1e6)));

// ---------------------------------------------------------------------------
// Caso de ejemplo (punto 9)
// ---------------------------------------------------------------------------
async function cargarCaso() {
  const boton = $('btn-caso');
  boton.disabled = true;
  try {
    const caso = await pedir('/api/t3/caso_ejemplo');
    terminarDibujo();
    $('sel-perfil').value = caso.perfil;
    aplicarPerfil(caso.perfil);
    llenarPreferencias(caso.preferencias);  // el caso fija R_min para que, sin la amenaza, la ruta corta ya cumpla
    $('chk-puntos').checked = false;
    Object.keys(estado.considerar).forEach((k) => { estado.considerar[k] = true; });
    $('panel-capas').querySelectorAll('[data-considerar]').forEach((el) => { el.checked = true; });
    fijar('origen', L.latLng(caso.origen.lat, caso.origen.lon));
    fijar('destino', L.latLng(caso.destino.lat, caso.destino.lon));
    estado.zonas = [{ tipo: 'amenaza', ...caso.zona_amenaza }];
    dibujarZonas();
    const filas = Object.keys(TECNICAS).map((k) => {
      const a = (caso.etapa1.tecnicas || {})[k] || {};
      const b = (caso.etapa2.tecnicas || {})[k] || {};
      return `<tr><td>${TECNICAS[k].nombre}</td><td>${num(a.largo_km, 2)}</td><td>${pct(a.resiliencia, 1)}</td>
        <td>${num(b.largo_km, 2)} ${b.cruza_zona ? '<span class="no" title="cruza la zona">⚠</span>' : ''}</td><td>${pct(b.resiliencia, 1)}</td></tr>`;
    });
    $('contenido-caso').innerHTML = `
      <p class="ayuda">${esc(caso.descripcion)}</p>
      <table>
        <thead><tr><th>Técnica</th><th colspan="2">sin la zona: km · R</th><th colspan="2">con la zona: km · R</th></tr></thead>
        <tbody>${filas.join('')}</tbody>
      </table>
      <p class="ayuda">⚠ = la ruta cruza la zona de amenaza. Sorteo ilustrativo: semilla ${esc(caso.sorteo.semilla)}
        (${esc(caso.sorteo.criterio)}). Desmarca «considerar» en «Zonas del usuario» y recalcula para ver la etapa sin la zona.</p>
      ${(caso.objetivos || []).map((o) => `<div class="${o.cumple ? 'ok-caja' : 'aviso'}">${si(o.cumple)} ${esc(o.texto)}</div>`).join('')}`;
    const res = await calcular();
    if (res) await sortear(caso.sorteo.semilla);
  } catch (e) {
    $('contenido-caso').innerHTML = `<div class="aviso error">No se pudo cargar el caso: ${esc(e.message)}</div>`;
  } finally {
    boton.disabled = false;
  }
}
$('btn-caso').addEventListener('click', cargarCaso);

// ---------------------------------------------------------------------------
// Tarea 2: par Dijkstra + par Yen con selección resiliente
// ---------------------------------------------------------------------------
function dibujarRutasT2(grupo, res, ajustar) {
  grupo.clearLayers();
  const lineas = [];
  const dibujar = (rutas, color, metodo) => (rutas || []).forEach((r, i) => {
    const linea = L.polyline(r.coordenadas, { color, weight: i === 0 ? 5 : 4, opacity: 0.9, dashArray: i === 0 ? null : '8 6' })
      .bindTooltip(`${metodo} (Tarea 2), ruta ${i + 1}: ${num(r.largo_km)} km`);
    linea.addTo(grupo);
    lineas.push(linea);
  });
  dibujar(res.dijkstra, COLOR.dijkstra, 'Dijkstra');
  dibujar(res.propuesta, COLOR.propuesta, 'Propuesta');
  if (ajustar && lineas.length) mapa.fitBounds(L.featureGroup(lineas).getBounds(), { padding: [30, 30] });
}

function filaRuta(clase, i, metodo, r) {
  return `<tr><td><span class="linea ${clase} ${i ? 'alt' : ''}"></span>${metodo} ${i + 1}</td>`
    + `<td>${num(r.largo_km)}</td><td>${num(r.costo)}</td><td>${num(r.riesgo_medio, 3)}</td></tr>`;
}

function mostrarResultadoT2(res, titulo) {
  const ev = res.resiliencia || {};
  const rPar = ev.r_par || {};
  const rMis = ev.r_mision || {};
  const dCA = ev.diferencial_C_vs_A || {};
  const dCD = ev.diferencial_C_vs_D || {};
  const filas = [
    ...(res.dijkstra || []).map((r, i) => filaRuta('dij', i, 'Dijkstra', r)),
    ...(res.propuesta || []).map((r, i) => filaRuta('prop', i, 'Propuesta', r)),
  ];
  const avisos = (res.advertencias || []).map((a) => `<div class="aviso">${esc(a)}</div>`).join('');
  $('contenido-resultado').innerHTML = `
    <h3>${esc(titulo)}</h3>${avisos}
    <table>
      <thead><tr><th>Ruta</th><th>km</th><th>costo</th><th>riesgo medio</th></tr></thead>
      <tbody>${filas.join('')}</tbody>
    </table>
    <table>
      <thead><tr><th>Métrica (Tarea 2)</th><th>Dijkstra</th><th>Propuesta</th><th>Δ pp</th></tr></thead>
      <tbody>
        <tr><td>R_par</td><td>${pct(rPar.dijkstra)}</td><td>${pct(rPar.propuesta)}</td><td>${num(ev.delta_r_par_pp, 1)}</td></tr>
        <tr><td>R_misión</td><td>${pct(rMis.A_dijkstra_fijo)}</td><td>${pct(rMis.C_propuesta)}</td><td>${num(dCA.delta_R_pp, 1)}</td></tr>
        <tr><td>Ablación D</td><td>${pct(rMis.D_dijkstra_replan)}</td><td></td><td>${num(dCD.delta_R_pp, 1)} (C−D)</td></tr>
      </tbody>
    </table>`;
}

$('btn-yen').addEventListener('click', async () => {
  if (!estado.origen || !estado.destino) { $('txt-yen').textContent = 'Define el origen y el destino.'; return; }
  const boton = $('btn-yen');
  boton.disabled = true;
  $('txt-yen').textContent = 'Calculando el par de la Tarea 2…';
  try {
    const res = await postJSON('/api/rutas', { origen: estado.origen, destino: estado.destino, preferencias: leerPreferencias() });
    dibujarRutasT2(capa.yen, res, true);
    verCapa('yen', true);
    mostrarResultadoT2(res, 'Par Yen (Tarea 2)');
    $('txt-yen').textContent = '';
  } catch (e) {
    $('txt-yen').textContent = `Error: ${e.message}`;
  } finally {
    boton.disabled = false;
  }
});

// ---------------------------------------------------------------------------
// Inicio
// ---------------------------------------------------------------------------
(async function iniciar() {
  try {
    const [t3, prefs] = await Promise.all([pedir('/api/t3/perfiles'), pedir('/api/preferencias')]);
    estado.perfiles = t3.perfiles;
    estado.defecto = t3.preferencias;
    Object.assign(estado.considerar, t3.considerar);
    $('sel-perfil').innerHTML = Object.entries(t3.perfiles).map(([k, p]) => `<option value="${k}">${esc(p.nombre)}</option>`).join('');
    $('sel-perfil').value = 'inspeccion';
    aplicarPerfil('inspeccion');
    const f = $('form-prefs');
    CAMPOS_ACO.forEach((c) => { f.elements[`aco_${c}`].value = t3.aco[c]; });
    f.elements.n_sorteos.value = t3.resiliencia.n_sorteos;
    f.elements.prob_deteccion.value = t3.resiliencia.prob_deteccion;
    construirPanel();
    $('txt-viento').textContent = textoViento(prefs.viento);
    pintarViento(prefs.viento);
    actualizarLeyenda();
    mostrarEstado('Elige origen y destino (o «Usar la misión») y pulsa «Calcular las 4 rutas». También puedes cargar el caso de ejemplo.');
  } catch (e) {
    mostrarEstado(`No se pudo conectar con la BD: ${e.message}`, true);
    return;
  }
  try {
    const ej = await pedir('/api/ejemplo');
    dibujarRutasT2(capa.yen, ej, false);
    mostrarResultadoT2(ej, 'Ejemplo de la misión (Tarea 2)');
  } catch (_) { /* sin ejemplo de la Tarea 2 */ }
}());

// ---------------------------------------------------------------------------
// Tarea 2: flota con aviso compartido (animación del cambio de ruta en tiempo real)
// ---------------------------------------------------------------------------
const COLOR_UAV = ['#0f766e', '#2563eb', '#ea580c', '#9333ea', '#db2777'];
const capaFlota = capa.flota;
const anim = { datos: null, modo: 'con_aviso', t: 0, fin: 0, jugando: false, ultimo: null, capas: null, bitacora: [] };
const FINALES = ['completada', 'perdido_en_interferencia', 'atrapado', 'sin_alternativa', 'presupuesto', 'sin_ruta', 'bucle'];

const TEXTO_EVENTO = {
  despegue: [(i) => `UAV ${i} despega`, ''],
  deteccion: [(i) => `UAV ${i} detecta interferencia en el borde de una zona`, 'clave'],
  aviso_enviado: [(i) => `UAV ${i} avisa a la flota`, 'clave'],
  aviso_recibido: [(i, e) => `UAV ${i} recibe el aviso ${e.clase === 'silencio' ? 'por silencio' : 'de detección'} (de UAV ${e.de + 1})`, ''],
  replan_aviso: [(i) => `UAV ${i} cambia de ruta en pleno vuelo por el aviso`, 'clave'],
  replan: [(i) => `UAV ${i} se topa con el bloqueo y replanifica`, ''],
  perdido_en_interferencia: [(i) => `UAV ${i} entra a una zona sin notarla y pierde el enlace`, 'mala'],
  atrapado: [(i) => `UAV ${i} queda dentro de una zona y pierde el enlace`, 'mala'],
  completada: [(i) => `UAV ${i} completa la misión`, 'clave'],
  sin_alternativa: [(i) => `UAV ${i} aborta: no queda ruta`, 'mala'],
  presupuesto: [(i) => `UAV ${i} aborta: excede el presupuesto de km`, 'mala'],
  sin_ruta: [(i) => `UAV ${i} no encuentra ruta`, 'mala'],
  bucle: [(i) => `UAV ${i} aborta: demasiados pasos`, 'mala'],
};

function posicionEn(tray, t) {
  if (!tray.length) return null;
  if (t <= tray[0].t_s) return tray[0].pos;
  for (let i = 1; i < tray.length; i += 1) {
    const a = tray[i - 1];
    const b = tray[i];
    if (t <= b.t_s) {
      const f = b.t_s > a.t_s ? (t - a.t_s) / (b.t_s - a.t_s) : 1;
      return [a.pos[0] + f * (b.pos[0] - a.pos[0]), a.pos[1] + f * (b.pos[1] - a.pos[1])];
    }
  }
  return tray[tray.length - 1].pos;
}

function ultimoEvento(eventos, t, tipos) {
  let elegido = null;
  for (const e of eventos) {
    if (e.t_s > t) break;
    if (tipos.includes(e.tipo)) elegido = e;
  }
  return elegido;
}

function armarCapas() {
  capaFlota.clearLayers();
  const lt = anim.datos.animacion[anim.modo];
  const zonas = lt.fallas.map((f) => L.circle([f.lat, f.lon], { radius: f.radio_km * 1000, weight: 1 })
    .bindTooltip(`Zona de interferencia ${f.id + 1}: activa desde t = ${num(f.inicio_s, 0)} s`).addTo(capaFlota));
  const uavs = lt.uavs.map((u, i) => {
    const color = COLOR_UAV[i % COLOR_UAV.length];
    return {
      plan: L.polyline([], { color, weight: 2, opacity: 0.7, dashArray: '6 6' }).addTo(capaFlota),
      hecho: L.polyline([], { color, weight: 4, opacity: 0.9 }).addTo(capaFlota),
      marca: L.circleMarker(AOI_DEFECTO[0], { radius: 9, color: '#fff', weight: 2, fillColor: color, fillOpacity: 1 })
        .bindTooltip(String(i + 1), { permanent: true, direction: 'center', className: 'etiqueta-uav' }).addTo(capaFlota),
    };
  });
  const efimeras = L.layerGroup().addTo(capaFlota);
  anim.capas = { zonas, uavs, efimeras };
  anim.fin = lt.fin_s;
  $('txt-fin').textContent = num(lt.fin_s, 0);
  const filas = [];
  lt.uavs.forEach((u, i) => u.eventos.forEach((e) => {
    const def = TEXTO_EVENTO[e.tipo];
    if (def) filas.push({ t: e.t_s, texto: def[0](i + 1, e), clase: def[1] });
  }));
  lt.avisos.filter((a) => a.tipo === 'silencio').forEach((a) => filas.push({
    t: a.t_s, clase: 'clave', texto: `La flota deja de oír al UAV ${a.origen + 1} y marca su zona para evitarla`,
  }));
  anim.bitacora = filas.sort((a, b) => a.t - b.t);
}

function dibujarInstante() {
  if (!anim.datos || !anim.capas) return;
  const lt = anim.datos.animacion[anim.modo];
  const t = anim.t;
  lt.fallas.forEach((f, i) => {
    anim.capas.zonas[i].setStyle(t >= f.inicio_s
      ? { color: '#b91c1c', fillColor: '#ef4444', fillOpacity: 0.25, dashArray: null, opacity: 0.9 }
      : { color: '#6b7280', fillColor: '#9ca3af', fillOpacity: 0.04, dashArray: '4 6', opacity: 0.6 });
  });
  const estadoTxt = [];
  lt.uavs.forEach((u, i) => {
    const color = COLOR_UAV[i % COLOR_UAV.length];
    const capas = anim.capas.uavs[i];
    const pos = posicionEn(u.trayectoria, t);
    const enTierra = t < u.despegue_s;
    const fin = ultimoEvento(u.eventos, t, FINALES);
    if (pos) capas.marca.setLatLng(pos);
    capas.marca.setStyle({ fillOpacity: enTierra ? 0.35 : 1, fillColor: fin && fin.tipo !== 'completada' ? '#111827' : color });
    const pasados = u.trayectoria.filter((p) => p.t_s <= t).map((p) => p.pos);
    capas.hecho.setLatLngs(pos && !enTierra ? [...pasados, pos] : []);
    const plan = fin ? null : ultimoEvento(u.eventos, t, ['plan', 'replan', 'replan_aviso']);
    capas.plan.setLatLngs(plan && plan.ruta ? plan.ruta : []);
    const cambios = u.eventos.filter((e) => e.tipo === 'replan_aviso' && e.t_s <= t).length;
    let txt = enTierra ? 'en tierra' : 'volando';
    if (fin) {
      if (fin.tipo === 'completada') txt = 'completó';
      else if (fin.tipo === 'atrapado' || fin.tipo.startsWith('perdido')) txt = 'sin enlace';
      else txt = 'abortó';
    }
    estadoTxt.push(`<div><span class="punto-uav" style="background:${color}"></span>`
      + `UAV ${i + 1}: ${txt}${cambios ? ` · ${cambios} cambio(s) por aviso` : ''}</div>`);
  });
  $('estado-uav').innerHTML = estadoTxt.join('');
  const ef = anim.capas.efimeras;
  ef.clearLayers();
  const radio = (anim.datos.radio_silencio_km || 0.6) * 1000;
  lt.avisos.forEach((a) => {
    const color = a.tipo === 'silencio' ? '#7c3aed' : '#f59e0b';
    if (a.tipo === 'silencio' && t >= a.t_s) {
      L.circle(a.pos, { radius: radio, color, weight: 2, dashArray: '5 5', fillOpacity: 0.06 })
        .bindTooltip(`Zona marcada por el silencio del UAV ${a.origen + 1}`).addTo(ef);
    }
    const dt = t - a.t_s;
    if (dt < 0 || dt > 25) return;
    L.circleMarker(a.pos, { radius: 8 + dt * 1.2, color, weight: 3, fill: false, opacity: 1 - dt / 25 }).addTo(ef);
    Object.entries(a.recepciones).forEach(([j, tr]) => {
      const k = Number(j);
      if (k === a.origen || t < tr || t > tr + 15) return;
      const destino = posicionEn(lt.uavs[k].trayectoria, t);
      if (destino) L.polyline([a.pos, destino], { color, weight: 2, dashArray: '2 6', opacity: 0.9 }).addTo(ef);
    });
  });
  $('txt-t').textContent = num(t, 0);
  $('rng-t').value = anim.fin ? Math.round((1000 * t) / anim.fin) : 0;
  const visibles = anim.bitacora.filter((f) => f.t <= t).slice(-12).reverse();
  $('bitacora').innerHTML = visibles
    .map((f) => `<li class="${f.clase}"><span class="t">${num(f.t, 0)} s</span> ${esc(f.texto)}</li>`).join('');
}

function pausar() {
  anim.jugando = false;
  anim.ultimo = null;
  $('btn-play').textContent = '▶ Reproducir';
}

function cuadro(ahora) {
  if (!anim.jugando) return;
  if (anim.ultimo !== null) anim.t = Math.min(anim.fin, anim.t + ((ahora - anim.ultimo) / 1000) * Number($('sel-vel').value));
  anim.ultimo = ahora;
  dibujarInstante();
  if (anim.t >= anim.fin) { pausar(); return; }
  requestAnimationFrame(cuadro);
}

$('btn-play').addEventListener('click', () => {
  if (anim.jugando) { pausar(); return; }
  if (anim.t >= anim.fin) anim.t = 0;
  anim.jugando = true;
  $('btn-play').textContent = '❚❚ Pausa';
  requestAnimationFrame(cuadro);
});
$('rng-t').addEventListener('input', (e) => { anim.t = (Number(e.target.value) / 1000) * anim.fin; dibujarInstante(); });
$('sel-modo').addEventListener('change', (e) => { anim.modo = e.target.value; armarCapas(); dibujarInstante(); });

const ETIQUETA_FLOTA = {
  D_dijkstra_replan: 'Sin aviso (D)',
  C_propuesta: 'Sin aviso, propuesta (C)',
  D_A_dijkstra_replan_aviso: 'Con aviso, Dijkstra (D_A)',
  C_A_propuesta_aviso: 'Con aviso, propuesta (C_A)',
};
const etiquetaFlota = (n) => ETIQUETA_FLOTA[n] || n;

function mostrarFlota(res) {
  const filas = Object.entries(res.resumen).map(([n, s]) => `<tr><td>${esc(etiquetaFlota(n))}</td>`
    + `<td>${pct(s.R_uav)}</td><td>${pct(s.R_seguidores)}</td><td>${num(s.perdidos_media)}</td>`
    + `<td>${num(s.replan_por_aviso_media)}</td><td>${num(s.demora_aviso_media_s, 1)}</td></tr>`);
  const difs = (res.diferenciales_seguidores || []).map((d) => {
    const v = Number(d.delta_R_pp);
    return `<li>${esc(etiquetaFlota(d.metodo))} frente a ${esc(etiquetaFlota(d.referencia))}: `
      + `<strong class="${v > 0 ? 'pos' : (v < 0 ? 'neg' : '')}">${v > 0 ? '+' : ''}${num(v, 1)} pp</strong> `
      + `<span class="ayuda">(gana ${esc(d.solo_metodo_completa)}, pierde ${esc(d.solo_referencia_completa)}; `
      + `McNemar p ${d.p_mcnemar < 1e-4 ? '< 0,0001' : `= ${num(d.p_mcnemar, 4)}`})</span></li>`;
  });
  const avisos = (res.advertencias || []).map((a) => `<div class="aviso">${esc(a)}</div>`).join('')
    + (res.secuencia_editada ? '<div class="aviso">Misión editada: estas cifras no son comparables con las'
      + ` del informe, que usan la misión de la base de datos. Secuencia simulada: ${esc((res.secuencia || []).join(' → '))}.</div>` : '');
  const ej = res.escenario_animado || {};
  $('contenido-flota').innerHTML = `
    ${avisos}
    <p class="ayuda">Escenario animado: semilla ${esc(ej.semilla)} (${esc(ej.motivo)}). Las métricas son de
      ${esc(res.n_escenarios)} escenarios con ${esc(res.n_fallas)} zonas cada uno.</p>
    <table>
      <thead><tr><th>Estrategia</th><th>R_uav</th><th>seguidores</th><th>perdidos</th><th>cambios por aviso</th><th>demora (s)</th></tr></thead>
      <tbody>${filas.join('')}</tbody>
    </table>
    <h3>Diferencial en los seguidores</h3>
    <ul class="difs">${difs.join('')}</ul>
    <p class="ayuda">Presupuesto ${num(res.presupuesto_km)} km por UAV = (1 + β) × ${num(res.largo_minimo_km)} km.
      Focos de las zonas: ${esc(res.origen_focos)} (${esc(res.n_focos)}). Las zonas de interferencia son círculos sintéticos.</p>`;
}

$('form-flota').addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const f = $('form-flota');
  const cuerpo = {
    preferencias: leerPreferencias(),
    n_uav: Number(f.elements.n_uav.value) || 4,
    separacion_km: Number(f.elements.separacion_km.value) || 1,
    prob_deteccion: Number(f.elements.prob_deteccion.value),
    alcance_com_km: Number(f.elements.alcance_com_km.value) || null,
    n_fallas: Number(f.elements.n_fallas.value) || 3,
    n_escenarios: Number(f.elements.n_escenarios.value) || 30,
  };
  if (estado.origen) cuerpo.origen = estado.origen;
  if (estado.destino) cuerpo.destino = estado.destino;
  if (estado.puntos) cuerpo.puntos = estado.puntos;
  const boton = $('btn-flota');
  boton.disabled = true;
  pausar();
  $('txt-flota').textContent = 'Simulando la flota sin aviso y con aviso…';
  try {
    anim.datos = await postJSON('/api/flota', cuerpo);
    anim.t = 0;
    anim.modo = $('sel-modo').value;
    verCapa('flota', true);
    armarCapas();
    dibujarInstante();
    $('reproductor').hidden = false;
    mostrarFlota(anim.datos);
    const puntos = anim.datos.animacion[anim.modo].uavs.flatMap((u) => u.trayectoria.map((p) => p.pos));
    if (puntos.length) mapa.fitBounds(L.latLngBounds(puntos), { padding: [30, 30] });
    $('txt-flota').textContent = 'Listo. Pulsa reproducir y cambia entre "con aviso" y "sin aviso" para comparar el mismo escenario.';
  } catch (e) {
    $('txt-flota').textContent = `Error: ${e.message}`;
  } finally {
    boton.disabled = false;
  }
});
