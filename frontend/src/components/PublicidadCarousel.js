import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Loader2 } from 'lucide-react';

function parseDims(dimStr) {
  if (!dimStr) return null;
  const m = String(dimStr).match(/(\d+)\s*x\s*(\d+)/i);
  if (!m) return null;
  return { w: parseInt(m[1], 10), h: parseInt(m[2], 10) };
}

export default function PublicidadCarousel({ 
  dimensiones, 
  query, 
  position = 'inline', 
  autoPlayMs = 5000,
  debug = true
}) {
  const [items, setItems] = useState([]);
  const [index, setIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const timerRef = useRef(null);
  const dims = useMemo(() => parseDims(dimensiones), [dimensiones]);

  // Debug log when component mounts
  useEffect(() => {
    if (debug) {
      console.log(`[PublicidadCarousel] Mounted with position=${position}, dimensiones=${dimensiones}, query=${query}`);
    }
    return () => {
      if (debug) {
        console.log(`[PublicidadCarousel] Unmounted (was at position=${position})`);
      }
    };
  }, [position, dimensiones, query, debug]);

  // Fetch ads data
  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    if (debug) {
      console.log(`[PublicidadCarousel] Fetching ads for position=${position}, dimensiones=${dimensiones}, query=${query}`);
    }

    async function load() {
      try {
        const params = new URLSearchParams();
        if (dimensiones) params.set('dimensiones', dimensiones);
        if (query) params.set('q', query);
        params.set('limit', '100');
        
        const url = `/dashboard/api/publicidad/activas/?${params.toString()}`;
        if (debug) {
          console.log(`[PublicidadCarousel] API URL: ${url}`);
        }

        const startTime = performance.now();
        const resp = await fetch(url);
        const data = await resp.json();
        const endTime = performance.now();

        if (debug) {
          console.log(`[PublicidadCarousel] API response (${Math.round(endTime - startTime)}ms):`, {
            status: resp.status,
            data: {
              success: data.success,
              itemsCount: data.items?.length || 0,
              itemsSample: data.items?.slice(0, 2)
            }
          });
        }

        if (!cancelled) {
          if (data?.success && Array.isArray(data.items)) {
            setItems(data.items);
            setIndex(0);
            if (data.items.length === 0 && debug) {
              console.warn(`[PublicidadCarousel] No ads found for position=${position}, dimensiones=${dimensiones}, query=${query}`);
            }
          } else {
            setError(data?.message || 'Error al cargar publicidad');
            console.error('[PublicidadCarousel] API error:', data);
          }
        }
      } catch (e) {
        console.error('[PublicidadCarousel] Error fetching ads:', e);
        if (!cancelled) {
          setError('Error de conexión');
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [dimensiones, query, position, debug]);

  // Auto-advance slides
  useEffect(() => {
    if (!items.length || autoPlayMs <= 0) return;

    timerRef.current = setInterval(() => {
      setIndex((i) => (i + 1) % items.length);
    }, autoPlayMs);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [items, autoPlayMs]);

  // Log slide changes
  useEffect(() => {
    if (debug && items.length > 0) {
      console.log(`[PublicidadCarousel] Changed to slide ${index + 1}/${items.length}`, {
        currentItem: items[index]
      });
    }
  }, [index, items, debug]);

  // Base container styles
  const baseContainerStyle = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(245, 245, 245, 0.9)',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
    overflow: 'hidden',
    position: 'relative',
    border: '1px solid #e0e0e0'
  };

  // Position-specific styles
  const positionStyles = {
    'top': {
      ...baseContainerStyle,
      width: '100%',
      maxWidth: dims ? `${dims.w}px` : '100%',
      margin: '16px auto',
      minHeight: dims ? `${dims.h}px` : '200px',
    },
    'left-fixed': {
      ...baseContainerStyle,
      position: 'fixed',
      left: '16px',
      top: '140px',
      zIndex: 1000,
      width: dims ? `${dims.w}px` : '300px',
      minHeight: dims ? `${dims.h}px` : '600px',
    },
    'right-fixed': {
      ...baseContainerStyle,
      position: 'fixed',
      right: '16px',
      top: '140px',
      zIndex: 1000,
      width: dims ? `${dims.w}px` : '300px',
      minHeight: dims ? `${dims.h}px` : '600px',
    },
    'inline': {
      ...baseContainerStyle,
      width: '100%',
      margin: '16px 0',
      minHeight: dims ? `${dims.h}px` : '200px',
    }
  };

  const containerStyle = {
    ...positionStyles[position] || positionStyles.inline,
    ...(position.includes('fixed') && {
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
      borderRadius: '12px'
    })
  };

  const imageStyle = {
    width: '100%',
    height: '100%',
    objectFit: 'contain',
    display: 'block'
  };

  // Loading state
  if (isLoading) {
    return (
      <div style={containerStyle}>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          width: '100%',
          height: '100%',
          padding: '20px',
          color: '#666'
        }}>
          <Loader2 className="animate-spin" style={{ marginBottom: '10px' }} />
          <div>Cargando publicidad...</div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={containerStyle}>
        <div style={{
          padding: '20px',
          color: '#666',
          textAlign: 'center'
        }}>
          <div>No se pudo cargar la publicidad</div>
          {debug && <div style={{ fontSize: '0.8em', marginTop: '8px' }}>{error}</div>}
        </div>
      </div>
    );
  }

  // No items state
  if (items.length === 0) {
    return (
      <div style={containerStyle}>
        <div style={{
          padding: '20px',
          color: '#999',
          textAlign: 'center',
          fontStyle: 'italic'
        }}>
          {debug ? (
            <div>
              <div>No hay publicidad disponible</div>
              <div style={{ fontSize: '0.8em', marginTop: '8px' }}>
                Posición: {position}, Dimensiones: {dimensiones || 'ninguna'}, Query: {query || 'ninguna'}
              </div>
            </div>
          ) : (
            <div>Publicidad no disponible</div>
          )}
        </div>
      </div>
    );
  }

  const currentItem = items[index];

  return (
    <div 
      className={`pub-carousel pos-${position}`} 
      style={containerStyle}
      title={currentItem?.ubicacion?.nombre || 'Publicidad'}
    >
      <a 
        href={currentItem?.url_destino || '#'} 
        target="_blank" 
        rel="noopener noreferrer"
        style={{ 
          display: 'block', 
          width: '100%', 
          height: '100%',
          position: 'relative'
        }}
      >
        <img 
          src={currentItem?.media_url} 
          alt={currentItem?.ubicacion?.nombre || 'Publicidad'} 
          style={imageStyle} 
          onError={(e) => {
            console.error(`[PublicidadCarousel] Error loading image: ${currentItem?.media_url}`);
            e.target.style.display = 'none';
          }}
        />
        
        {/* Navigation dots */}
        {items.length > 1 && (
          <div style={{
            position: 'absolute',
            bottom: '10px',
            left: 0,
            right: 0,
            display: 'flex',
            justifyContent: 'center',
            gap: '8px',
            padding: '4px'
          }}>
            {items.map((_, i) => (
              <div 
                key={i}
                style={{
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  backgroundColor: i === index ? 'rgba(255, 255, 255, 0.9)' : 'rgba(255, 255, 255, 0.4)',
                  cursor: 'pointer',
                  transition: 'background-color 0.3s',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.3)'
                }}
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setIndex(i);
                  // Reset auto-play timer
                  if (timerRef.current) {
                    clearInterval(timerRef.current);
                    timerRef.current = setInterval(() => {
                      setIndex(i => (i + 1) % items.length);
                    }, autoPlayMs);
                  }
                }}
                aria-label={`Ir al slide ${i + 1}`}
              />
            ))}
          </div>
        )}
      </a>
    </div>
  );
}
