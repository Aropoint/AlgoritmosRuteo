'use strict';

// Mapa del sitio: capas de infraestructura, metadata y amenazas; rutas Dijkstra vs propuesta.
const COLOR = { dijkstra: '#2563eb', propuesta: '#ea580c', origen: '#16a34a', destino: '#7c3aed' };
const AOI_DEFECTO = [[46.945, 31.95], [47.005, 32.04]];

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const vacio = (x) => x === null || x === undefined || Number.isNaN(Number(x));
const num = (x, d = 2) => (vacio(x) ? '—' : Number(x).toLocaleString('es-CL', { maximumFractionDigits: d }));
const pct = (x, d = 0) => (vacio(x) ? '—' : `${num(100 * x, d)} %`);

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

// ---------------------------------------------------------------------------
// Mapa base y capas
// ---------------------------------------------------------------------------
const mapa = L.map('mapa', { preferCanvas: true }).fitBounds(AOI_DEFECTO);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; colaboradores de <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(mapa);
const control = L.control.layers(null, null, { collapsed: false }).addTo(mapa);

function colorRiesgo(r) {
  const t = Math.max(0, Math.min(1, Number(r) || 0));
  const [a, b, u] = t < 0.5 ? [[156, 163, 175], [245, 158, 11], t / 0.5] : [[245, 158, 11], [220, 38, 38], (t - 0.5) / 0.5];
  const c = a.map((v, i) => Math.round(v + (b[i] - v) * u));
  return `rgb(${c.join(',')})`;
}

function popup(props) {
  const filas = Object.entries(props).map(([k, v]) => `<tr><th>${esc(k)}</th><td>${esc(v)}</td></tr>`);
  return `<table>${filas.join('')}</table>`;
}

const CAPAS = {
  aristas: {
    nombre: 'Tramos del grafo (color = riesgo)', visible: true,
    style: (f) => ({ color: colorRiesgo(f.properties.riesgo), weight: 2, opacity: 0.8 }),
  },
  mision: {
    nombre: 'Misión: inicio, puntos de observación, destino', visible: true,
    pointToLayer: (f, ll) => L.circleMarker(ll, { radius: 7, color: '#111827', weight: 2, fillColor: '#fde047', fillOpacity: 1 }),
  },
  edificios: {
    nombre: 'Metadata: edificios OSM (gris oscuro = con altura)', perezosa: true,
    style: (f) => ({ color: f.properties.altura_m ? '#475569' : '#94a3b8', weight: 0.5, fillOpacity: f.properties.altura_m ? 0.5 : 0.15 }),
  },
  gpsjam: {
    nombre: 'Amenaza: GPSJam (celdas H3; rojo = días degradados)',
    style: (f) => {
      const p = f.properties.frac_dias_rojos;
      return { color: '#7c3aed', weight: 1, fillColor: p ? '#dc2626' : '#7c3aed', fillOpacity: p ? 0.1 + 0.5 * p : 0.03 };
    },
  },
  incendios: {
    nombre: 'Amenaza: incendios de guerra (oscuro = período de evaluación)',
    pointToLayer: (f, ll) => L.circleMarker(ll, {
      radius: 3, weight: 0, fillOpacity: 0.7, fillColor: f.properties.periodo === 'evaluacion' ? '#7f1d1d' : '#f97316',
    }),
  },
  eventos: {
    nombre: 'Amenaza: eventos UCDP',
    pointToLayer: (f, ll) => L.circleMarker(ll, { radius: 5, color: '#111827', weight: 1, fillColor: '#111827', fillOpacity: 0.45 }),
  },
};

const estado = { origen: null, destino: null, mision: null, defecto: null };

for (const [clave, def] of Object.entries(CAPAS)) {
  const grupo = L.layerGroup();
  control.addOverlay(grupo, def.nombre);
  if (def.visible) grupo.addTo(mapa);
  let cargada = false;
  const cargar = async () => {
    if (cargada) return;
    cargada = true;
    try {
      const geo = await pedir(`/api/capas/${clave}`);
      if (clave === 'mision') estado.mision = geo;
      const opciones = { onEachFeature: (f, l) => l.bindPopup(popup(f.properties)) };
      if (def.style) opciones.style = def.style;
      if (def.pointToLayer) opciones.pointToLayer = def.pointToLayer;
      L.geoJSON(geo, opciones).addTo(grupo);
      if (clave === 'mision') grupo.eachLayer((l) => l.bringToFront && l.bringToFront());
    } catch (e) {
      cargada = false;
      console.warn(`Capa ${clave}:`, e);
    }
  };
  if (def.perezosa) grupo.on('add', cargar); else cargar();
}

const capaEjemplo = L.layerGroup().addTo(mapa);
control.addOverlay(capaEjemplo, 'Ejemplo de la misión (pgr_dijkstra y propuesta)');
const capaCalculadas = L.layerGroup().addTo(mapa);
control.addOverlay(capaCalculadas, 'Rutas calculadas');

const leyenda = L.control({ position: 'bottomright' });
leyenda.onAdd = () => {
  const div = L.DomUtil.create('div', 'leyenda');
  div.innerHTML = `
    <div><span class="linea dij"></span>Dijkstra ruta 1 &nbsp;<span class="linea dij alt"></span>ruta 2</div>
    <div><span class="linea prop"></span>Propuesta ruta 1 &nbsp;<span class="linea prop alt"></span>ruta 2</div>
    <div>Riesgo del tramo: 0 <span class="barra"></span> 1</div>`;
  return div;
};
leyenda.addTo(mapa);

// ---------------------------------------------------------------------------
// Origen y destino
// ---------------------------------------------------------------------------
const marcadores = { origen: null, destino: null };

function fijar(tipo, latlng) {
  estado[tipo] = { lat: latlng.lat, lon: latlng.lng };
  if (marcadores[tipo]) marcadores[tipo].remove();
  marcadores[tipo] = L.circleMarker(latlng, { radius: 9, color: '#fff', weight: 2, fillColor: COLOR[tipo], fillOpacity: 1 })
    .bindTooltip(tipo === 'origen' ? 'Origen' : 'Destino').addTo(mapa);
  $(`txt-${tipo}`).textContent = `${latlng.lat.toFixed(5)}, ${latlng.lng.toFixed(5)}`;
}

function quitar(tipo) {
  estado[tipo] = null;
  if (marcadores[tipo]) marcadores[tipo].remove();
  marcadores[tipo] = null;
  $(`txt-${tipo}`).textContent = 'sin definir';
}

mapa.on('click', (e) => {
  if (!estado.origen || estado.destino) {
    quitar('destino');
    fijar('origen', e.latlng);
  } else {
    fijar('destino', e.latlng);
  }
});

$('btn-limpiar').addEventListener('click', () => { quitar('origen'); quitar('destino'); capaCalculadas.clearLayers(); });

$('btn-mision').addEventListener('click', async () => {
  try {
    const geo = estado.mision || await pedir('/api/capas/mision');
    const puntos = geo.features.slice().sort((a, b) => a.properties.orden - b.properties.orden);
    if (puntos.length < 2) throw new Error('La misión no tiene inicio y destino.');
    const ll = (f) => L.latLng(f.geometry.coordinates[1], f.geometry.coordinates[0]);
    fijar('origen', ll(puntos[0]));
    fijar('destino', ll(puntos[puntos.length - 1]));
  } catch (e) {
    mostrarEstado(`No se pudo leer la misión: ${e.message}`, true);
  }
});

// ---------------------------------------------------------------------------
// Preferencias
// ---------------------------------------------------------------------------
const CAMPOS_NUMERICOS = ['altura_vuelo_m', 'margen_vertical_m', 'viento_max_m_s', 'velocidad_crucero_m_s',
  'desvio_max', 'presupuesto_extra', 'peso_riesgo'];

function llenarPreferencias(p) {
  const f = $('form-prefs');
  CAMPOS_NUMERICOS.forEach((c) => { f.elements[c].value = p[c]; });
  f.elements.respetar_zonas_restringidas.checked = !!p.respetar_zonas_restringidas;
}

function leerPreferencias() {
  const f = $('form-prefs');
  const p = {};
  CAMPOS_NUMERICOS.forEach((c) => {
    const v = f.elements[c].value;
    if (v !== '') p[c] = Number(v);
  });
  p.respetar_zonas_restringidas = f.elements.respetar_zonas_restringidas.checked;
  return p;
}

function textoViento(v) {
  if (!v || vacio(v.velocidad_a_altura_vuelo_m_s)) return (v && v.nota) || 'Sin datos de viento.';
  return `Viento representativo (mediana ${String(v.desde || '').slice(0, 10)} a ${String(v.hasta || '').slice(0, 10)}): `
    + `${num(v.mediana_100m_m_s, 1)} m/s a 100 m, ${num(v.velocidad_a_altura_vuelo_m_s, 1)} m/s a la altura de vuelo, `
    + `desde ${num(v.direccion_desde_grados, 0)}°.`;
}

$('btn-defecto').addEventListener('click', () => { if (estado.defecto) llenarPreferencias(estado.defecto); });

// ---------------------------------------------------------------------------
// Resultado
// ---------------------------------------------------------------------------
function mostrarEstado(texto, error = false) {
  const p = $('txt-estado');
  p.textContent = texto;
  p.className = error ? 'aviso error' : 'ayuda';
}

function dibujarRutas(grupo, res, ajustar) {
  grupo.clearLayers();
  const lineas = [];
  const dibujar = (rutas, color, metodo) => (rutas || []).forEach((r, i) => {
    const linea = L.polyline(r.coordenadas, { color, weight: i === 0 ? 5 : 4, opacity: 0.9, dashArray: i === 0 ? null : '8 6' })
      .bindTooltip(`${metodo}, ruta ${i + 1}: ${num(r.largo_km)} km`);
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

function mostrarResultado(res, titulo) {
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
  const delta = Number(dCA.delta_R_pp);
  const clase = delta > 0 ? 'pos' : (delta < 0 ? 'neg' : '');
  const sel = res.seleccion;
  const textoSel = sel
    ? `<p class="ayuda">Selección del par: J = ${num(sel.J, 3)} (estiramiento ${num(sel.estiramiento, 3)}, solape ${num(sel.solape, 3)}, `
      + `riesgo ${num(sel.riesgo, 3)}; ${num(sel.candidatas, 0)} candidatas de pgr_KSP, ${num(sel.validas, 0)} dentro del desvío).</p>`
    : '';
  $('contenido-resultado').innerHTML = `
    <h3>${esc(titulo)}</h3>
    <p class="ayuda">Nodos ${esc(res.origen)} → ${esc(res.destino)}. Tramos excluidos por restricciones: ${(res.aristas_excluidas || []).length}.
      ${esc(textoViento(res.viento))}</p>
    ${avisos}
    <table>
      <thead><tr><th>Ruta</th><th>km</th><th>costo</th><th>riesgo medio</th></tr></thead>
      <tbody>${filas.join('')}</tbody>
    </table>
    ${textoSel}
    <h3>Resiliencia en ${esc(ev.n_escenarios ?? '—')} escenarios con ${esc(ev.n_fallas ?? '—')} fallas cada uno</h3>
    <table>
      <thead><tr><th>Métrica</th><th>Dijkstra</th><th>Propuesta</th><th>Δ pp</th></tr></thead>
      <tbody>
        <tr><td>R_par: alguna ruta del par queda libre</td><td>${pct(rPar.dijkstra)}</td><td>${pct(rPar.propuesta)}</td><td>${num(ev.delta_r_par_pp, 1)}</td></tr>
        <tr><td>R_misión: llega dentro del presupuesto</td><td>${pct(rMis.A_dijkstra_fijo)}</td><td>${pct(rMis.C_propuesta)}</td><td>${num(dCA.delta_R_pp, 1)}</td></tr>
        <tr><td>Ablación D: Dijkstra que replanifica</td><td>${pct(rMis.D_dijkstra_replan)}</td><td></td><td>${num(dCD.delta_R_pp, 1)} (C−D)</td></tr>
      </tbody>
    </table>
    <p>Diferencial de resiliencia ΔR = R(C) − R(A):
      <span class="delta ${clase}">${delta > 0 ? '+' : ''}${num(dCA.delta_R_pp, 1)} pp</span><br>
      <span class="ayuda">McNemar p = ${num(dCA.p_mcnemar, 4)}: ${esc(dCA.solo_metodo_completa ?? 0)} escenarios solo los completa la propuesta
      y ${esc(dCA.solo_referencia_completa ?? 0)} solo Dijkstra.</span></p>
    <p class="ayuda">Presupuesto ${num(ev.presupuesto_km)} km = (1 + β) × ${num(ev.largo_minimo_km)} km.
      Focos de las fallas: ${esc(ev.origen_focos)} (${esc(ev.n_focos ?? 0)}).</p>`;
}

$('form-prefs').addEventListener('submit', async (ev) => {
  ev.preventDefault();
  if (!estado.origen || !estado.destino) {
    mostrarEstado('Define el origen y el destino haciendo clic en el mapa (o usa la misión).', true);
    return;
  }
  const f = $('form-prefs');
  const cuerpo = {
    origen: estado.origen,
    destino: estado.destino,
    preferencias: leerPreferencias(),
    n_fallas: Number(f.elements.n_fallas.value) || 3,
    n_escenarios: Number(f.elements.n_escenarios.value) || 100,
  };
  const boton = $('btn-calcular');
  boton.disabled = true;
  mostrarEstado('Calculando rutas en la BD y simulando escenarios de fallas…');
  try {
    const res = await pedir('/api/rutas', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo),
    });
    dibujarRutas(capaCalculadas, res, true);
    mostrarResultado(res, 'Rutas calculadas');
    mostrarEstado(res.id_evaluacion ? `Guardado en la BD (evaluación ${res.id_evaluacion}).` : 'Listo.');
  } catch (e) {
    mostrarEstado(`Error: ${e.message}`, true);
  } finally {
    boton.disabled = false;
  }
});

// ---------------------------------------------------------------------------
// Inicio: preferencias por defecto y ejemplo de la misión
// ---------------------------------------------------------------------------
(async function iniciar() {
  try {
    const p = await pedir('/api/preferencias');
    estado.defecto = p.preferencias;
    llenarPreferencias(p.preferencias);
    $('txt-viento').textContent = textoViento(p.viento);
  } catch (e) {
    mostrarEstado(`No se pudo conectar con la BD: ${e.message}`, true);
    return;
  }
  try {
    const ej = await pedir('/api/ejemplo');
    dibujarRutas(capaEjemplo, ej, false);
    mostrarResultado(ej, 'Ejemplo: inicio → destino de la misión, preferencias por defecto');
    mostrarEstado('Se muestra el ejemplo generado con pgr_dijkstra y pgr_KSP. Elige otro origen y destino para calcular.');
  } catch (e) {
    mostrarEstado(`Sin rutas de ejemplo todavía (${e.message}). Elige origen y destino para calcular.`);
  }
}());
