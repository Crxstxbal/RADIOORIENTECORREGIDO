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
    nombre_contacto: '',
    email_contacto: '',
    telefono_contacto: '',
    preferencia_contacto: 'email',
    url_destino: '',
    fecha_inicio: '',
    fecha_fin: '',
    mensaje: '',
    imagenes: {}, // Para almacenar las imágenes por ubicación
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
        let data;
      try {
        data = await res.json();
      } catch (e) {
        const text = await res.text().catch(() => '');
        console.error('[Publicidad] Respuesta no JSON', res.status, text);
        alert(`Error al crear la solicitud: HTTP ${res.status}`);
        return;
      }
      console.log('[Publicidad] Respuesta crear solicitud:', data);
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
      const ubicaciones = selectedCards.length ? selectedCards : (selected ? [selected] : []);
      
      // Validar campos requeridos
      if (!form.nombre_contacto || !form.email_contacto || !ubicaciones.length) {
        alert('Completa nombre, email y selecciona al menos una ubicación.');
        return;
      }

      // Validar URL de destino (requerida por ItemSolicitudWeb)
      if (!form.url_destino) {
        alert('Ingresa la URL de destino de tu publicidad.');
        return;
      }

      // Autocompletar fechas por mes si no se proporcionan
      const fmt = (d) => d.toISOString().split('T')[0];
      const today = new Date();
      const startAuto = fmt(today);
      const endAuto = (() => { const d = new Date(today); d.setMonth(d.getMonth() + 1); return fmt(d); })();
      const fechaInicio = form.fecha_inicio || startAuto;
      const fechaFin = form.fecha_fin || endAuto;

      // Nota: el endpoint actual no acepta imágenes. No bloqueamos por falta de imagen.

      const ubicacionIds = ubicaciones.map(u => u.id);

      // Crear el payload en el formato que espera el endpoint de dashboard
      const payload = {
        nombre: String(form.nombre_contacto || '').trim(),
        email: String(form.email_contacto || '').trim(),
        telefono: form.telefono_contacto || '',
        preferencia_contacto: form.preferencia_contacto || 'email',
        ubicacion_ids: ubicacionIds,
        url_destino: form.url_destino,
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
        mensaje: form.mensaje || '',
        // Copias de respaldo (por si hay otras vistas que las lean)
        nombre_contacto: String(form.nombre_contacto || '').trim(),
        email_contacto: String(form.email_contacto || '').trim(),
      };

      console.log('[Publicidad] Enviando solicitud:', payload);

      const res = await fetch(`${backendBase}/dashboard/api/publicidad/solicitar/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
        },
        credentials: 'include',
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        alert(`Error al crear la solicitud: ${data && data.message ? data.message : 'Error desconocido'}`);
        return;
      }

      console.log('[Publicidad] Solicitud creada:', data);

      // Subir imágenes si existen
      if (data.items_web && data.items_web.length > 0 && Object.keys(form.imagenes).length > 0) {
        console.log('[Publicidad] Subiendo imágenes...');
        
        for (const item of data.items_web) {
          const imagen = form.imagenes[item.ubicacion_id];
          if (imagen) {
            try {
              const formData = new FormData();
              formData.append('imagen', imagen);
              formData.append('descripcion', `Imagen para ${ubicaciones.find(u => u.id === item.ubicacion_id)?.title || 'ubicación'}`);
              formData.append('orden', '0');

              const imgRes = await fetch(`${backendBase}/dashboard/api/publicidad/items/${item.id}/imagenes/subir/`, {
                method: 'POST',
                credentials: 'include',
                body: formData,
              });

              const imgData = await imgRes.json();
              if (!imgRes.ok || !imgData.success) {
                console.error(`Error al subir imagen para item ${item.id}:`, imgData.message);
              } else {
                console.log(`Imagen subida para item ${item.id}`);
              }
            } catch (imgError) {
              console.error(`Error al subir imagen para item ${item.id}:`, imgError);
            }
          }
        }
      }

      alert(data.message || 'Solicitud enviada correctamente');
      setShowModal(false);
      setSelected(null);
      setSelectedIds([]);
      setForm({
        nombre_contacto: '',
        email_contacto: '',
        telefono_contacto: '',
        preferencia_contacto: 'email',
        url_destino: '',
        fecha_inicio: '',
        fecha_fin: '',
        mensaje: '',
        imagenes: {},
      });
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
  const backdrop = { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', overflowY: 'auto', padding: '20px 0' };
  const modal = { width: 'min(720px, 95vw)', background: '#1f1f1f', color: '#fff', border: '1px solid #333', borderRadius: 12, padding: 24, maxHeight: '90vh', overflowY: 'auto' };
  const input = { width: '100%', padding: 12, borderRadius: 8, border: '1px solid #444', background: '#111', color: '#fff', fontSize: '0.9em' };
  const row = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 };
  
  const handleImageChange = (ubicacionId, event) => {
    const file = event.target.files[0];
    if (file) {
      // Validar tamaño de la imagen (máx 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('La imagen no debe superar los 5MB');
        return;
      }
      
      // Validar tipo de archivo
      const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
      if (!validTypes.includes(file.type)) {
        alert('Formato de archivo no válido. Usa JPG, PNG, GIF o WebP');
        return;
      }
      
      setForm(prev => ({
        ...prev,
        imagenes: {
          ...prev.imagenes,
          [ubicacionId]: file
        }
      }));
    }
  };
  
  const renderImagePreview = (ubicacionId) => {
    const file = form.imagenes[ubicacionId];
    if (!file) return null;
    
    const previewUrl = URL.createObjectURL(file);
    return (
      <div style={{ marginTop: 8, position: 'relative' }}>
        <img 
          src={previewUrl} 
          alt="Vista previa" 
          style={{ 
            maxWidth: '100%', 
            maxHeight: '150px', 
            borderRadius: 8,
            border: '2px solid #dc143c',
            boxSizing: 'border-box'
          }} 
        />
        <button 
          onClick={(e) => {
            e.stopPropagation();
            setForm(prev => {
              const newImagenes = { ...prev.imagenes };
              delete newImagenes[ubicacionId];
              return { ...prev, imagenes: newImagenes };
            });
          }}
          style={{
            position: 'absolute',
            top: 5,
            right: 5,
            background: '#dc143c',
            border: 'none',
            borderRadius: '50%',
            width: 24,
            height: 24,
            color: 'white',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 0,
            fontSize: 12,
            lineHeight: 1
          }}
        >
          ×
        </button>
      </div>
    );
  };
  
  const renderFileInput = (ubicacion) => (
    <div key={ubicacion.id} style={{ marginBottom: 20 }}>
      <div style={{ marginBottom: 8, fontWeight: 500 }}>
        Imagen para: {ubicacion.title} ({ubicacion.dim})
      </div>
      <label 
        htmlFor={`file-upload-${ubicacion.id}`} 
        style={{
          display: 'block',
          padding: '12px 16px',
          background: '#2d2d2d',
          border: '2px dashed #444',
          borderRadius: 8,
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          ':hover': {
            borderColor: '#dc143c',
            background: '#333'
          }
        }}
      >
        {form.imagenes[ubicacion.id] ? 'Cambiar imagen' : 'Seleccionar imagen'}
        <input
          id={`file-upload-${ubicacion.id}`}
          type="file"
          accept="image/*"
          style={{ display: 'none' }}
          onChange={(e) => handleImageChange(ubicacion.id, e)}
        />
      </label>
      {renderImagePreview(ubicacion.id)}
      <div style={{ fontSize: '0.8em', color: '#888', marginTop: 4 }}>
        Formatos: JPG, PNG, GIF, WebP (máx. 5MB)
      </div>
    </div>
  );
  return (
    <div style={backdrop} onClick={onClose}>
      <div style={modal} onClick={e => e.stopPropagation()}>
        <h3 style={{ marginTop: 0, color: '#fff', borderBottom: '1px solid #444', paddingBottom: 12, marginBottom: 20 }}>Solicitud de Publicidad</h3>
        
        <div style={{ marginBottom: 24 }}>
          <h4 style={{ marginTop: 0, marginBottom: 12, color: '#ddd' }}>Espacios seleccionados:</h4>
          <ul style={{ paddingLeft: 20, margin: '0 0 16px 0' }}>
            {list.map(c => (
              <li key={c.id} style={{ marginBottom: 8 }}>
                <strong>{c.title}</strong> · {c.dim} · {CLP.format(c.price)}
              </li>
            ))}
          </ul>
          <div style={{ fontSize: '1.1em', fontWeight: 'bold', color: '#fff' }}>
            Total estimado: <span style={{ color: '#dc143c' }}>{CLP.format(total)}</span> / mes
          </div>
        </div>

        <div style={{ marginBottom: 24 }}>
          <h4 style={{ marginTop: 0, marginBottom: 16, color: '#ddd', borderBottom: '1px solid #444', paddingBottom: 8 }}>Datos de contacto</h4>
          <div style={{ display: 'grid', gap: 16 }}>
            <div>
              <label style={{ display: 'block', marginBottom: 6, color: '#bbb' }}>Nombre completo *</label>
              <input 
                style={input} 
                placeholder="Tu nombre" 
                value={form.nombre_contacto} 
                onChange={e => setForm({ ...form, nombre_contacto: e.target.value })} 
              />
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: 6, color: '#bbb' }}>Email *</label>
              <input 
                style={input} 
                type="email" 
                placeholder="tu@email.com" 
                value={form.email_contacto} 
                onChange={e => setForm({ ...form, email_contacto: e.target.value })} 
              />
            </div>
            
            <div style={row}>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: 6, color: '#bbb' }}>Teléfono</label>
                <input 
                  style={input} 
                  placeholder="+56912345678" 
                  value={form.telefono_contacto} 
                  onChange={e => setForm({ ...form, telefono_contacto: e.target.value })} 
                />
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: 6, color: '#bbb' }}>Preferencia de contacto</label>
                <select 
                  style={{ ...input, width: '100%' }} 
                  value={form.preferencia_contacto} 
                  onChange={e => setForm({ ...form, preferencia_contacto: e.target.value })}
                >
                  <option value="telefono">Llamada telefónica</option>
                  <option value="whatsapp">WhatsApp</option>
                  <option value="email">Correo electrónico</option>
                </select>
              </div>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: 6, color: '#bbb' }}>URL de destino</label>
              <input 
                style={input} 
                type="url" 
                placeholder="https://tusitio.com" 
                value={form.url_destino} 
                onChange={e => setForm({ ...form, url_destino: e.target.value })} 
              />
            </div>
            
            <div style={row}>
              <div>
                <label style={{ display: 'block', marginBottom: 6, color: '#bbb' }}>Fecha de inicio</label>
                <input 
                  style={input} 
                  type="date" 
                  value={form.fecha_inicio} 
                  onChange={e => setForm({ ...form, fecha_inicio: e.target.value })} 
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: 6, color: '#bbb' }}>Fecha de término</label>
                <input 
                  style={input} 
                  type="date" 
                  value={form.fecha_fin} 
                  onChange={e => setForm({ ...form, fecha_fin: e.target.value })} 
                />
              </div>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: 6, color: '#bbb' }}>Mensaje adicional (opcional)</label>
              <textarea 
                style={{ ...input, minHeight: 100 }} 
                placeholder="¿Algo más que quieras contarnos sobre tu publicidad?" 
                value={form.mensaje} 
                onChange={e => setForm({ ...form, mensaje: e.target.value })} 
              />
            </div>
          </div>
        </div>

        <div style={{ marginBottom: 24 }}>
          <h4 style={{ marginTop: 0, marginBottom: 16, color: '#ddd', borderBottom: '1px solid #444', paddingBottom: 8 }}>
            Imágenes para publicidad
          </h4>
          <div style={{ display: 'grid', gap: 20 }}>
            {list.map(ubicacion => renderFileInput(ubicacion))}
          </div>
        </div>

        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          paddingTop: 16,
          borderTop: '1px solid #444',
          marginTop: 8
        }}>
          <button 
            onClick={onClose}
            style={{
              padding: '10px 24px',
              background: 'transparent',
              border: '1px solid #666',
              color: '#ddd',
              borderRadius: 6,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              ':hover': {
                background: '#333',
                borderColor: '#888'
              }
            }}
          >
            Cancelar
          </button>
          <button 
            onClick={onSubmit}
            style={{
              padding: '10px 32px',
              background: '#dc143c',
              border: 'none',
              color: 'white',
              borderRadius: 6,
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              ':hover': {
                background: '#b01030',
                transform: 'translateY(-1px)'
              }
            }}
          >
            Enviar solicitud
          </button>
        </div>
      </div>
    </div>
  );
}

export default PublicidadPage;
