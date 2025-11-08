import React, { useEffect, useMemo, useState } from 'react';
import styles from './PublicidadPage.module.css';
const CLP = new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 });

const cardsData = [
  {
    id: 1,
    badge: 'PREMIUM',
    dim: '728 x 90 px',
    title: 'Banner Superior Premium',
    desc:
      'Posición privilegiada en la cabecera del sitio. Máxima visibilidad en todas las páginas.',
    stats: [
      { label: 'Impresiones/mes', value: '150,000+' },
      { label: 'Ubicación', value: 'Header' },
      { label: 'Formato', value: 'Banner' },
      { label: 'Clics estimados', value: '4,500+' },
    ],
    price: 299,
    category: 'Banners',
  },
  {
    id: 2,
    dim: '300 x 600 px',
    title: 'Panel Lateral Derecho',
    desc:
      'Espacio vertical destacado al lado del contenido principal. Alta tasa de interacción.',
    stats: [
      { label: 'Impresiones/mes', value: '120,000+' },
      { label: 'Ubicación', value: 'Sidebar' },
      { label: 'Formato', value: 'Vertical' },
      { label: 'Clics estimados', value: '3,600+' },
    ],
    price: 249,
    category: 'Paneles Laterales',
  },
  {
    id: 3,
    dim: '300 x 250 px',
    title: 'Banner Medio Rectangular',
    desc:
      'Formato versátil integrado en el contenido. Excelente balance entre visibilidad y costo.',
    stats: [
      { label: 'Impresiones/mes', value: '100,000+' },
      { label: 'Ubicación', value: 'Contenido' },
      { label: 'Formato', value: 'Cuadrado' },
      { label: 'Clics estimados', value: '3,000+' },
    ],
    price: 179,
    category: 'Banners',
  },
  {
    id: 4,
    badge: 'POPULAR',
    dim: '970 x 250 px',
    title: 'Billboard Destacado',
    desc:
      'Gran formato impactante debajo del header. Perfecto para campañas de alto impacto.',
    stats: [
      { label: 'Impresiones/mes', value: '180,000+' },
      { label: 'Ubicación', value: 'Top Page' },
      { label: 'Formato', value: 'Billboard' },
      { label: 'Clics estimados', value: '5,400+' },
    ],
    price: 349,
    category: 'Destacados',
  },
  {
    id: 5,
    dim: '160 x 600 px',
    title: 'Panel Lateral Izquierdo',
    desc:
      'Espacio vertical a la izquierda del contenido. Presencia constante durante la navegación.',
    stats: [
      { label: 'Impresiones/mes', value: '95,000+' },
      { label: 'Ubicación', value: 'Sidebar Izq' },
      { label: 'Formato', value: 'Skyscraper' },
      { label: 'Clics estimados', value: '2,850+' },
    ],
    price: 199,
    category: 'Paneles Laterales',
  },
  {
    id: 6,
    dim: '728 x 90 px',
    title: 'Banner Footer',
    desc:
      'Ubicado al pie de página. Ideal para complementar otras posiciones publicitarias.',
    stats: [
      { label: 'Impresiones/mes', value: '80,000+' },
      { label: 'Ubicación', value: 'Footer' },
      { label: 'Formato', value: 'Banner' },
      { label: 'Clics estimados', value: '2,400+' },
    ],
    price: 129,
    category: 'Banners',
  },
];

const staticFilters = ['Todos'];

const PublicidadPage = () => {
  const [active, setActive] = useState('Todos');
  const [tipos, setTipos] = useState([]);
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selected, setSelected] = useState(null); // card seleccionada
  const [form, setForm] = useState({
    nombre: '',
    email: '',
    telefono: '',
    preferencia_contacto: 'telefono',
    url_destino: '',
    fecha_inicio: '',
    fecha_fin: '',
    mensaje: '',
  });
  const [selectedIds, setSelectedIds] = useState([]);

  const backendBase = useMemo(() => (window.location.port === '3000' ? 'http://127.0.0.1:8000' : window.location.origin), []);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const apiUrl = `${backendBase}/dashboard/api/publicidad/ubicaciones/?all=1`;
        const res = await fetch(apiUrl);
        if (!res.ok) {
          console.error('API publicidad no OK', res.status, apiUrl);
          return;
        }
        const data = await res.json();
        console.log('API ubicaciones (debug)', data);
        if (!mounted) return;
        setTipos(Array.isArray(data.tipos) ? data.tipos : []);
        const mapped = (data.ubicaciones || []).map(u => ({
          id: u.id,
          dim: u.dimensiones || '',
          title: u.nombre,
          desc: u.descripcion || '',
          stats: [
            { label: 'Ubicación', value: u['tipo__nombre'] || '' },
            { label: 'Formato', value: u.dimensiones || '' },
          ],
          price: Number(u.precio_mensual || 0),
          category: (u['tipo__nombre'] || 'Otros'),
          badge: undefined,
          tipoNombre: u['tipo__nombre'] || '',
        }));
        setCards(mapped);
      } catch (e) {
        console.error('Error cargando API de ubicaciones', e);
      }
      setLoading(false);
    }
    load();
    return () => { mounted = false; };
  }, []);

  const filters = useMemo(() => {
    const dynamic = tipos.map(t => t.nombre).filter(Boolean);
    const set = new Set([...staticFilters, ...dynamic]);
    return Array.from(set);
  }, [tipos]);

  const list = useMemo(() => {
    const source = cards; // sin fallback: mostramos solo BD
    if (active === 'Todos') return source;
    return source.filter((c) => c.category === active);
  }, [active, cards]);

  const selectedCards = useMemo(() => cards.filter(c => selectedIds.includes(c.id)), [cards, selectedIds]);
  const totalCLP = useMemo(() => selectedCards.reduce((acc, c) => acc + (Number(c.price) || 0), 0), [selectedCards]);

  function toggleSelect(card) {
    setSelectedIds(prev => prev.includes(card.id) ? prev.filter(id => id !== card.id) : [...prev, card.id]);
  }

  async function submitSolicitud() {
    try {
      const payload = {
        nombre: form.nombre,
        email: form.email,
        telefono: form.telefono,
        preferencia_contacto: form.preferencia_contacto,
        url_destino: form.url_destino,
        fecha_inicio: form.fecha_inicio,
        fecha_fin: form.fecha_fin,
        mensaje: form.mensaje,
        ubicacion_ids: selectedCards.length ? selectedCards.map(c => c.id) : (selected ? [selected.id] : []),
      };
      if (!payload.nombre || !payload.email || !payload.ubicacion_ids.length) {
        alert('Completa nombre, email y selecciona al menos una ubicación.');
        return;
      }
      const res = await fetch(`${backendBase}/dashboard/api/publicidad/solicitar/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        credentials: 'include',
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        alert(data.message || 'Error al enviar la solicitud');
        return;
      }
      alert(data.message || 'Solicitud enviada');
      setShowModal(false);
      setSelected(null);
      setSelectedIds([]);
      setForm({ nombre: '', email: '', telefono: '', preferencia_contacto: 'telefono', url_destino: '', fecha_inicio: '', fecha_fin: '', mensaje: '' });
    } catch (e) {
      console.error(e);
      alert('Ocurrió un error al enviar la solicitud');
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <div className={styles.header}>
          <h1>Publicidad en Radio Oriente</h1>
          <p>Alcanza a miles de oyentes con nuestros espacios publicitarios digitales</p>
        </div>

        <div className={styles.filters}>
          {filters.map((f) => (
            <button
              key={f}
              className={`${styles.filterBtn} ${active === f ? styles.active : ''}`}
              onClick={() => setActive(f)}
            >
              {f}
            </button>
          ))}
        </div>

        <div className={styles.packagesGrid}>
          {loading && <div className={styles.loading}>Cargando ubicaciones...</div>}
          {!loading && list.length === 0 && (
            <div className={styles.empty}>No hay ubicaciones activas disponibles en este momento.</div>
          )}
          {!loading && list.map((card) => (
            <div key={card.id} className={styles.packageCard}>
              {card.badge ? <div className={styles.cardBadge}>{card.badge}</div> : null}
              <div className={styles.cardPreview}>
                <div className={styles.previewDimensions}>{card.dim}</div>
              </div>
              <div className={styles.cardContent}>
                <h3 className={styles.cardTitle}>{card.title}</h3>
                <p className={styles.cardDescription}>{card.desc}</p>
                <div className={styles.cardStats}>
                  {card.stats.map((s, i) => (
                    <div key={i} className={styles.statItem}>
                      <div className={styles.statLabel}>{s.label}</div>
                      <div className={styles.statValue}>{s.value}</div>
                    </div>
                  ))}
                </div>
                <div className={styles.cardPrice}>
                  <div className={styles.priceTag}>
                    {CLP.format(card.price)}
                    <span className={styles.pricePeriod}>/mes</span>
                  </div>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <button className={styles.ctaButton} onClick={() => toggleSelect(card)}>
                      {selectedIds.includes(card.id) ? 'Quitar' : 'Agregar'}
                    </button>
                    <button className={styles.ctaButton} onClick={() => {
                      setSelected(card);
                      setForm(f => ({...f, mensaje: `Interés en ${card.title} (${card.dim}) - ${card.tipoNombre}`}));
                      setShowModal(true);
                    }}>
                      Contratar
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Barra de selección y total */}
        {selectedIds.length > 0 && (
          <div style={{ position: 'sticky', bottom: 16, marginTop: 24, background: '#1f1f1f', border: '1px solid #333', padding: 12, borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <strong>{selectedIds.length}</strong> espacios seleccionados · Total: <strong>{CLP.format(totalCLP)}</strong>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className={styles.ctaButton} onClick={() => setSelectedIds([])}>Limpiar</button>
              <button className={styles.ctaButton} onClick={() => { setSelected(null); setShowModal(true); }}>Solicitar</button>
            </div>
          </div>
        )}

        <div className={styles.locationMap}>
          <h2>📍 Mapa de Ubicaciones Publicitarias</h2>
          <div className={styles.websitePreview}>
            <div className={styles.locationHeader}>RADIO ORIENTE - HEADER</div>
            <div className={styles.locationSpot}>Banner Superior Premium (728x90) - $299/mes</div>
            <div className={styles.locationSpot}>Billboard Destacado (970x250) - $349/mes</div>
            <div className={styles.locationSidebar}>
              <div className={`${styles.locationSpot} ${styles.sidebarSpot}`}>
                Panel<br />Lateral<br />Izquierdo<br />(160x600)<br /><br />$199/mes
              </div>
              <div className={`${styles.locationSpot} ${styles.sidebarSpot}`}>
                <strong>CONTENIDO PRINCIPAL</strong>
                <br />
                <br />
                Banner Medio Rectangular
                <br />(300x250)
                <br />
                <br />
                $179/mes
              </div>
              <div className={`${styles.locationSpot} ${styles.sidebarSpot}`}>
                Panel<br />Lateral<br />Derecho<br />(300x600)<br /><br />$249/mes
              </div>
            </div>
            <div className={styles.locationSpot}>Banner Footer (728x90) - $129/mes</div>
          </div>
        </div>
        {/* Modal de solicitud */}
        <ModalSolicitud
          open={showModal}
          onClose={() => setShowModal(false)}
          onSubmit={submitSolicitud}
          selectedCards={selectedCards}
          selectedSingle={selected}
          form={form}
          setForm={setForm}
          CLP={CLP}
        />
      </div>
    </div>
  );
};

// Modal simple inline
function ModalSolicitud({ open, onClose, onSubmit, selectedCards, selectedSingle, form, setForm, CLP }) {
  if (!open) return null;
  const list = selectedSingle ? [selectedSingle] : selectedCards;
  const total = list.reduce((acc, c) => acc + (Number(c.price) || 0), 0);
  const backdrop = { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' };
  const modal = { width: 'min(720px, 95vw)', background: '#1f1f1f', color: '#fff', border: '1px solid #333', borderRadius: 12, padding: 16 };
  const input = { width: '100%', padding: 8, borderRadius: 8, border: '1px solid #333', background: '#111', color: '#fff' };
  const row = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 };
  return (
    <div style={backdrop} onClick={onClose}>
      <div style={modal} onClick={e => e.stopPropagation()}>
        <h3>Solicitud de Publicidad</h3>
        <p>Espacios seleccionados:</p>
        <ul>
          {list.map(c => (
            <li key={c.id}>{c.title} · {c.dim} · {CLP.format(c.price)}</li>
          ))}
        </ul>
        <p>Total estimado: <strong>{CLP.format(total)}</strong> / mes</p>
        <div style={{ display: 'grid', gap: 12 }}>
          <input style={input} placeholder="Nombre" value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} />
          <input style={input} placeholder="Email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
          <div style={row}>
            <input style={input} placeholder="Teléfono" value={form.telefono} onChange={e => setForm({ ...form, telefono: e.target.value })} />
            <select style={input} value={form.preferencia_contacto} onChange={e => setForm({ ...form, preferencia_contacto: e.target.value })}>
              <option value="telefono">Teléfono</option>
              <option value="whatsapp">WhatsApp</option>
              <option value="email">Email</option>
            </select>
          </div>
          <div style={row}>
            <input style={input} placeholder="URL destino (opcional)" value={form.url_destino} onChange={e => setForm({ ...form, url_destino: e.target.value })} />
            <input style={input} type="date" placeholder="Fecha inicio" value={form.fecha_inicio} onChange={e => setForm({ ...form, fecha_inicio: e.target.value })} />
          </div>
          <div style={row}>
            <input style={input} type="date" placeholder="Fecha fin" value={form.fecha_fin} onChange={e => setForm({ ...form, fecha_fin: e.target.value })} />
          </div>
          <textarea style={{ ...input, minHeight: 90 }} placeholder="Mensaje (opcional)" value={form.mensaje} onChange={e => setForm({ ...form, mensaje: e.target.value })} />
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 12 }}>
          <button className={styles.ctaButton} onClick={onClose}>Cancelar</button>
          <button className={styles.ctaButton} onClick={onSubmit}>Enviar solicitud</button>
        </div>
      </div>
    </div>
  );
}

export default PublicidadPage;
