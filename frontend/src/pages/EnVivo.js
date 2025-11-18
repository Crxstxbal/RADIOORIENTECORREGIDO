import React, { useState, useEffect } from 'react';
import { Play, Users, Wifi, WifiOff, ExternalLink, Youtube, Facebook } from 'lucide-react';
import axios from 'axios';
import './Pages.css';

const EnVivo = () => {
  const [liveStream, setLiveStream] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [videoTitle, setVideoTitle] = useState("");

  useEffect(() => {
    const fetchLiveStreamData = async () => {
      try {
        const response = await axios.get('/api/radio/station/');
        const estacionData = response.data;
        
        if (estacionData && estacionData.live_stream_url) {
          setLiveStream({
            url: estacionData.live_stream_url,
            nombre: estacionData.nombre,
            descripcion: estacionData.descripcion,
            activo: estacionData.activo
          });
        } else {
          setLiveStream(null);
        }
      } catch (error) {
        console.error('Error fetching live stream data:', error);
        setError('Error al cargar la transmisión en vivo');
      } finally {
        setLoading(false);
      }
    };

    fetchLiveStreamData();
  }, []);

  const normalizeStreamUrl = (raw) => {
    if (!raw) return null;

    const url = String(raw).trim();

    // Si el usuario pegó un iframe completo, extraer el src
    if (/<iframe/i.test(url)) {
      const match = url.match(/src\s*=\s*"([^"]+)"/i) || url.match(/src\s*=\s*'([^']+)'/i);
      if (match && match[1]) return normalizeStreamUrl(match[1]);
    }

    // Normalizar YouTube
    if (/youtube\.com|youtu\.be/i.test(url)) {
      let videoId = '';
      // watch?v=
      if (/watch\?v=/.test(url)) videoId = new URL(url).searchParams.get('v') || '';
      // youtu.be/<id>
      if (!videoId && /youtu\.be\//.test(url)) videoId = url.split('youtu.be/')[1].split(/[?&#]/)[0];
      // /embed/<id>
      if (!videoId && /\/embed\//.test(url)) videoId = url.split('/embed/')[1].split(/[?&#]/)[0];
      // /live/<id>
      if (!videoId && /\/live\//.test(url)) videoId = url.split('/live/')[1].split(/[?&#]/)[0];
      if (videoId) return `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1`;
      // Si no se pudo extraer ID, intentar retornar como embed si ya lo es
      if (/\/embed\//.test(url)) return `${url}${url.includes('?') ? '&' : '?'}autoplay=1&mute=1`;
    }

    // Normalizar Facebook
    if (/facebook\.com/i.test(url)) {
      // /videos/<id>
      if (/\/videos\//.test(url)) {
        const after = url.split('/videos/')[1];
        const id = after.split(/[/?&#]/)[0];
        if (id) return `https://www.facebook.com/plugins/video.php?href=https://www.facebook.com/video.php?v=${id}&show_text=false&autoplay=1`;
      }
      // watch/?v=<id> o watch/live/?v=<id>
      try {
        const u = new URL(url, window.location.origin);
        const id = u.searchParams.get('v');
        if (id) return `https://www.facebook.com/plugins/video.php?href=https://www.facebook.com/video.php?v=${id}&show_text=false&autoplay=1`;
      } catch {}
      // Fallback: usar plugin con href crudo
      return `https://www.facebook.com/plugins/video.php?href=${encodeURIComponent(url)}&show_text=false&autoplay=1`;
    }

    // Otras URLs: devolver tal cual
    return url;
  };

  const getEmbedUrl = () => {
    if (!liveStream?.url) return null;
    return normalizeStreamUrl(liveStream.url);
  };

  const isYouTubeUrl = (url) => {
    return url && /youtube\.com|youtu\.be/i.test(url);
  };

  const isFacebookUrl = (url) => {
    return url && /facebook\.com/i.test(url);
  };

  // Utilidad: obtener el ID de YouTube desde diferentes formatos
  const getYouTubeId = (url) => {
    if (!url) return "";
    try {
      if (/watch\?v=/.test(url)) return new URL(url).searchParams.get('v') || "";
      if (/youtu\.be\//.test(url)) return url.split('youtu.be/')[1].split(/[?&#]/)[0];
      if (/\/embed\//.test(url)) return url.split('/embed/')[1].split(/[?&#]/)[0];
      if (/\/live\//.test(url)) return url.split('/live/')[1].split(/[?&#]/)[0];
    } catch {}
    return "";
  };

  // Cargar título del video con oEmbed (YouTube). Facebook requiere token, así que omitimos.
  useEffect(() => {
    const loadTitle = async () => {
      if (!liveStream?.url) return;
      try {
        if (isYouTubeUrl(liveStream.url)) {
          const id = getYouTubeId(liveStream.url);
          const watchUrl = id ? `https://www.youtube.com/watch?v=${id}` : liveStream.url;
          const resp = await axios.get('https://www.youtube.com/oembed', {
            params: { url: watchUrl, format: 'json' }
          });
          if (resp?.data?.title) setVideoTitle(resp.data.title);
        } else {
          setVideoTitle("");
        }
      } catch {
        setVideoTitle("");
      }
    };
    loadTitle();
  }, [liveStream?.url]);

  if (loading) {
    return (
      <div className="live-page">
        <div className="container">
          <div className="loading-container">
            <div className="spinner-large"></div>
            <p>Cargando transmisión en vivo...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="live-page">
        <div className="container">
          <div className="page-header">
            <WifiOff className="page-icon" style={{color: 'var(--color-gray-400)'}} />
            <div>
              <h1 className="page-title">Transmisión en Vivo</h1>
              <p className="page-subtitle">Error al cargar la transmisión</p>
            </div>
          </div>
          <div className="error-container">
            <p>{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!liveStream || !liveStream.url) {
    return (
      <div className="live-page">
        <div className="container">
          <div className="page-header">
            <WifiOff className="page-icon" style={{color: 'var(--color-gray-400)'}} />
            <div>
              <h1 className="page-title">Transmisión en Vivo</h1>
              <p className="page-subtitle">No hay transmisión en vivo disponible</p>
            </div>
          </div>
          
          <div className="no-stream-container">
            <div className="no-stream-card">
              <WifiOff size={64} style={{color: 'var(--color-gray-400)', marginBottom: '1rem'}} />
              <h3>No hay transmisión activa</h3>
              <p>En este momento no hay ninguna transmisión en vivo programada.</p>
              <p>Mantente atento a nuestras redes sociales para conocer próximos eventos en vivo.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const embedUrl = getEmbedUrl();

  return (
    <div className="live-page">
      <div className="container">
        <div className="page-header">
          <Wifi className="page-icon" style={{color: 'var(--color-red)'}} />
          <div>
            <h1 className="page-title">Transmisión en Vivo</h1>
            <p className="page-subtitle subtitle-primary"><strong>Cobertura especial de eventos y programas en directo</strong></p>
            {videoTitle && (
              <p className="page-subtitle">{videoTitle}</p>
            )}
          </div>
        </div>

        <div className="live-content">
          {/* Reproductor de video */}
          <div className="video-container">
            {embedUrl ? (
              <div className="video-wrapper">
                <iframe
                  src={embedUrl}
                  title="Transmisión en vivo"
                  frameBorder="0"
                  allowFullScreen
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  className="video-iframe"
                />
              </div>
            ) : (
              <div className="video-error">
                <Play size={48} style={{color: 'var(--color-gray-400)', marginBottom: '1rem'}} />
                <h3>Error al cargar el video</h3>
                <p>No se pudo cargar la transmisión. Verifica el enlace o intenta más tarde.</p>
                {liveStream.url && (
                  <a 
                    href={liveStream.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="external-link"
                  >
                    <ExternalLink size={16} />
                    Ver en plataforma original
                  </a>
                )}
              </div>
            )}
          </div>

          {/* Información en un solo contenedor debajo del video */}
          <div className="stream-details">
            <div className="stream-left">
              <div className="status-label">
                <span className="status-top">EN</span>
                <span className="status-bottom">VIVO</span>
              </div>
              <div className="stream-info">
                <h2>{liveStream.nombre}</h2>
                {liveStream.descripcion && <p>{liveStream.descripcion}</p>}
              </div>
            </div>

            <div className="stream-right">
              <div className="stream-actions">
                <a
                  href={liveStream.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-external"
                >
                  <ExternalLink size={16} />
                  Ver en plataforma original
                </a>
              </div>
              <div className="platform-info">
                {isYouTubeUrl(liveStream.url) && (
                  <div className="platform-badge youtube">
                    <Youtube size={16} style={{ marginRight: 6 }} />
                    <span>YouTube Live</span>
                  </div>
                )}
                {isFacebookUrl(liveStream.url) && (
                  <div className="platform-badge facebook">
                    <Facebook size={16} style={{ marginRight: 6 }} />
                    <span>Facebook Live</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnVivo;
