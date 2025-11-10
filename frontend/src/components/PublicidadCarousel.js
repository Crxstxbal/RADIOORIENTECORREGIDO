import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

function parseDims(dimStr) {
  if (!dimStr) return null;
  const m = String(dimStr).match(/(\d+)\s*x\s*(\d+)/i);
  if (!m) return null;
  return { w: parseInt(m[1], 10), h: parseInt(m[2], 10) };
}

//Variantes de animacion para los paneles
const panelVariants = {
  hidden: (position) => ({
    opacity: 0,
    x: position === 'left-fixed' ? -80 : 80,
    transition: { duration: 0.4, ease: 'easeInOut' }
  }),
  visible: { 
    opacity: 1,
    x: 0,
    transition: { 
      duration: 0.5,
      ease: [0.16, 1, 0.3, 1],
      delay: 0.1
    }
  }
};

export default function PublicidadCarousel({ 
  dimensiones, 
  query, 
  position = 'inline', 
  autoPlayMs = 5000,
  debug = true
}) {
  const [isVisible, setIsVisible] = useState(false);
  const location = useLocation();
  const isHomePage = location.pathname === '/';
  const panelRef = useRef(null);
  const [items, setItems] = useState([]);
  const [index, setIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const timerRef = useRef(null);
  const dims = useMemo(() => parseDims(dimensiones), [dimensiones]);

  //Log de debug cuando se monta el componente
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

  //Obtener datos de publicidad
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

  const throttle = (func, limit) => {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  };

  const lastScrollY = useRef(0);
  
  useEffect(() => {
    if (!isHomePage || (position !== 'left-fixed' && position !== 'right-fixed')) {
      return;
    }

    const handleScroll = () => {
      //Para que aparezca la animacion de la publicidad cuando se llega a la seccion de ultimos articulos
      const sections = document.querySelectorAll('section');
      let articlesSection = null;
      
      for (const section of sections) {
        const h2 = section.querySelector('h2.section-title');
        if (h2 && h2.textContent.includes('Últimos Artículos')) {
          articlesSection = section;
          break;
        }
      }
      
      if (!articlesSection) {
        if (debug) console.log('No se encontró la sección de Últimos Artículos');
        return;
      }
      
      const sectionRect = articlesSection.getBoundingClientRect();
      const windowHeight = window.innerHeight;
      const currentScrollY = window.scrollY;
      const isScrollingUp = currentScrollY < lastScrollY.current;
      lastScrollY.current = currentScrollY;
      
      if (isScrollingUp) {
        const triggerPoint = windowHeight * 0.3;
        setIsVisible(sectionRect.top <= triggerPoint);
      } else {
        const triggerPoint = windowHeight * 0.7;
        setIsVisible(sectionRect.top <= triggerPoint);
      }
    };

    const throttledScroll = throttle(handleScroll, 100);
    window.addEventListener('scroll', throttledScroll, { passive: true });
    
    handleScroll();
    
    return () => {
      window.removeEventListener('scroll', throttledScroll);
    };
  }, [position, isHomePage, debug]);

  //Avance automático
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

  //Log de cambios de diapositiva
  useEffect(() => {
    if (debug && items.length > 0) {
      console.log(`[PublicidadCarousel] Changed to slide ${index + 1}/${items.length}`, {
        currentItem: items[index]
      });
    }
  }, [index, items, debug]);

  //Calcular dimensiones responsivas manteniendo la proporción
  const calculateDimensions = (width, height, maxWidth = '100%') => {
    if (!width || !height) return { width: '100%', height: 'auto' };
    
    const aspectRatio = height / width;
    let maxW = maxWidth === '100%' ? '100%' : Math.min(Number(maxWidth), width);
    if (typeof maxW === 'number') {
      maxW = `${maxW}px`;
    }
    
    return {
      width: maxW,
      height: 'auto',
      aspectRatio: `${width}/${height}`,
      maxWidth: '100%',
      margin: '0 auto'
    };
  };

  //Contenido base con estilo
  const baseContainerStyle = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'transparent',
    overflow: 'hidden',
    position: 'relative',
    padding: 0,
    margin: '5px auto',
    maxWidth: '100%',
    width: '100%',
    boxSizing: 'border-box'
  };

  //No renderizar paneles fijos en móvil
  if ((position === 'left-fixed' || position === 'right-fixed') && window.innerWidth < 1024) {
    return null;
  }

  //Estilos específicos de posición
  const positionStyles = {
    'top': {
      ...baseContainerStyle,
      display: 'flex',
      margin: '0 auto',
      padding: '8px 0',
      maxWidth: '100%',
      width: '100%',
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: '#fff',
      boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
      borderBottom: '1px solid #f0f0f0',
      height: 'auto',
      maxHeight: '110px',
      overflow: 'hidden',
      '@media (max-width: 768px)': {
        maxHeight: '70px',
        padding: '4px 0',
      },
      '@media (min-width: 1200px)': {
        maxHeight: '130px',
        padding: '10px 0',
      }
    },
    'left-fixed': {
      ...baseContainerStyle,
      width: dims ? `${Math.min(dims.w, 180)}px` : '180px',
      height: dims ? `${dims.h * (180 / dims.w)}px` : 'auto',
      maxHeight: '450px',
      minHeight: 'auto',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      borderRadius: '6px',
      overflow: 'hidden',
      backgroundColor: '#fff',
      transition: 'all 0.3s ease'
    },
    'right-fixed': {
      ...baseContainerStyle,
      width: dims ? `${Math.min(dims.w, 180)}px` : '180px',
      height: dims ? `${dims.h * (180 / dims.w)}px` : 'auto',
      maxHeight: '450px',
      minHeight: 'auto',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      borderRadius: '6px',
      overflow: 'hidden',
      backgroundColor: '#fff',
      transition: 'all 0.3s ease'
    },
    'inline': {
      ...baseContainerStyle,
      display: 'flex',
      margin: '5px auto',
      justifyContent: 'center',
      alignItems: 'center'
    }
  };

  const containerStyle = {
    ...positionStyles[position] || positionStyles.inline,
    ...(position.includes('fixed') && {
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)'
    })
  };

  const imageStyle = {
    maxWidth: position === 'top' ? 'min(100%, 1200px)' : '100%',
    maxHeight: position === 'top' ? '90px' : '450px',
    height: 'auto',
    width: position === 'top' ? 'auto' : '100%',
    display: 'block',
    padding: 0,
    margin: '0 auto',
    borderRadius: position === 'top' ? '4px' : '4px',
    objectFit: position === 'top' ? 'contain' : 'cover',
    transition: 'all 0.3s ease',
    '@media (max-width: 768px)': {
      maxHeight: position === 'top' ? '60px' : '300px',
      borderRadius: position === 'top' ? '3px' : '4px',
    },
    '@media (min-width: 1200px)': {
      maxHeight: position === 'top' ? '110px' : '450px',
    }
  };

  //Mientras carga
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

  //En estado de error por si acaso
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

  //Sin items
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

  //Contenido para el carousel
  const content = (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <img
        src={currentItem?.media_url}
        alt={currentItem?.nombre || 'Publicidad'}
        style={imageStyle}
      />
      {items.length > 1 && (
        <div style={{
          position: 'absolute',
          bottom: '10px',
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          gap: '5px',
          zIndex: 10
        }}>
          {items.map((_, i) => (
            <button
              key={i}
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                setIndex(i);
              }}
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                border: 'none',
                padding: 0,
                backgroundColor: i === index ? '#007bff' : 'rgba(0,0,0,0.2)',
                cursor: 'pointer',
                transition: 'all 0.3s',
                transform: i === index ? 'scale(1.3)' : 'scale(1)'
              }}
              aria-label={`Ir al slide ${i + 1}`}
            />
          ))}
        </div>
      )}
    </div>
  );

  //Para paneles fijos (izquierda y derecha)
  if (position === 'left-fixed' || position === 'right-fixed') {
    const isArticlesPage = location.pathname.includes('/articulos');
    const shouldAnimate = isHomePage && !isArticlesPage; // Solo animar en la página de inicio
    
    //Estilo del panel
    const panelStyle = {
      position: 'fixed',
      [position === 'left-fixed' ? 'left' : 'right']: '8px',
      top: isArticlesPage ? '50%' : '30%', // Centrado vertical en artículos, 30% en home
      transform: 'translateY(-50%)',
      zIndex: 1000,
    };

    //En articulos sin animacion
    if (isArticlesPage) {
      return (
        <div style={panelStyle}>
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
                top: '0%',
                height: '100%',
                textDecoration: 'none',
                color: 'inherit'
              }}
              onClick={(e) => {
                if (!currentItem?.url_destino) {
                  e.preventDefault();
                }
              }}
            >
              {content}
            </a>
          </div>
        </div>
      );
    }
    
    //En home con animacion
    return (
      <motion.div
        initial="hidden"
        animate={isVisible ? "visible" : "hidden"}
        variants={panelVariants}
        custom={position}
        style={panelStyle}
      >
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
              textDecoration: 'none',
              color: 'inherit'
            }}
            onClick={(e) => {
              if (!currentItem?.url_destino) {
                e.preventDefault();
              }
            }}
          >
            {content}
          </a>
        </div>
      </motion.div>
    );
  } else {
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
            textDecoration: 'none',
            color: 'inherit'
          }}
          onClick={(e) => {
            if (!currentItem?.url_destino) {
              e.preventDefault();
            }
          }}
        >
          {content}
        </a>
      </div>
    );
  }
}
