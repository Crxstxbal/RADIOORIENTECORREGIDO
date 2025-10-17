import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Radio, Users, Music, Newspaper } from "lucide-react";
import axios from "axios";
import "./Home.css";

const Home = () => {
  const [featuredArticles, setFeaturedArticles] = useState([]);
  const [radioStation, setRadioStation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [articlesResponse, stationResponse] = await Promise.all([
          axios.get("/api/blog/articulos/"),
          axios.get("/api/radio/station/"),
        ]);

        // Filtrar artículos destacados
        const articles = articlesResponse.data.results || articlesResponse.data || [];
        const featured = articles.filter(article => article.destacado && article.publicado).slice(0, 3);
        setFeaturedArticles(featured);
        setRadioStation(stationResponse.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text">
              <h1 className="hero-title">
                Bienvenidos a
              </h1>
              <h1 className="hero-title">
                <span className="text-red">Radio Oriente FM</span>
              </h1>
              
              <p className="hero-description">
                La mejor música, noticias y entretenimiento de la Zona oriente
                de santiago. Conectando comunidades a través de las ondas
                radiales.
              </p>
              <div className="hero-buttons">
                <Link to="/programacion" className="btn btn-primary">
                  Ver Programación
                </Link>
                <Link to="/contacto" className="btn btn-outline">
                  Contáctanos
                </Link>
              </div>
            </div>
            <div className="hero-image">
              <div className="radio-graphic">
                <img
                  src="/images/radiooriente.png"
                  alt="Radio Oriente FM"
                  className="hero-logo"
                />
                <div className="radio-waves">
                  <div className="wave wave-1"></div>
                  <div className="wave wave-2"></div>
                  <div className="wave wave-3"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Secciones */}
      <section className="stats">
        <div className="container">
          <div className="stats-grid">
            <div className="stat-item">
              <Users className="stat-icon" />
              <div className="stat-number">
                {radioStation?.listeners_count || "1,000"}+
              </div>
              <div className="stat-label">Oyentes Activos</div>
            </div>
            <div className="stat-item">
              <Music className="stat-icon" />
              <div className="stat-number">24/7</div>
              <div className="stat-label">Música en Vivo</div>
            </div>
            <div className="stat-item">
              <Newspaper className="stat-icon" />
              <div className="stat-number">50+</div>
              <div className="stat-label">Noticias Diarias</div>
            </div>
            
            <div className="stat-item">
              <Radio className="stat-icon" />
              <div className="stat-number">
                {new Date().getFullYear() - 2011 - (new Date().getMonth() < 8 || (new Date().getMonth() === 8 && new Date().getDate() < 20) ? 1 : 0)}
              </div>
              <div className="stat-label">Años al Aire</div>
            </div>
          </div>
        </div>
      </section>

      {/* Noticias */}
      <section className="featured-news">
        <div className="container">
          <h2 className="section-title">Últimos Artículos</h2>
          {loading ? (
            <div className="loading-container">
              <div className="spinner"></div>
              <p>Cargando artículos...</p>
            </div>
          ) : (
            <div className="news-grid">
              {featuredArticles.map((article) => (
                <article key={article.id} className="news-card">
                  {article.imagen_url && (
                    <img
                      src={article.imagen_url}
                      alt={article.titulo}
                      className="news-image"
                    />
                  )}
                  <div className="news-content">
                    <h3 className="news-title">{article.titulo}</h3>
                    <p className="news-excerpt">{article.resumen || article.contenido.substring(0, 120) + '...'}</p>
                    <div className="news-meta">
                      <span className="news-date">
                        {new Date(article.fecha_publicacion || article.fecha_creacion).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
          <div className="text-center mt-8">
            <Link to="/articulos" className="btn btn-outline">
              Ver todos los artículos
            </Link>
          </div>
        </div>
      </section>

      <section className="cards-section">
        <div className="card">
          <div>
            <div className="icon mb-4">
              <Music className="icon-white" size={48} />
            </div>
            <h2 className="title mb-2 text-2xl font-bold">
              ¿Eres una banda o artista emergente?
            </h2>
            <p className="description mb-4 text-lg">
              ¡Queremos escucharte! Envía tu información y podrías aparecer en nuestra programación especial para artistas locales.
            </p>
          </div>
          <Link to="/emergente" className="btn-white mt-2">
            Postular Ahora
          </Link>
        </div>

        <div className="card">
          <div>
            <div className="icon mb-4">
              <Newspaper className="icon-white" size={48} />
            </div>
            <h2 className="title mb-2 text-2xl font-bold">
              ¿Quieres estar al día?
            </h2>
            <p className="description mb-4 text-lg">
              Suscríbete a nuestro boletín y recibe las últimas noticias y actualizaciones directamente en tu correo.
            </p>
          </div>
          <Link to="/suscripcion" className="btn-white mt-2">
            Suscribirse ahora
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;