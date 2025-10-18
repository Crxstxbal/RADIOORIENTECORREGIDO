import React, { useState, useEffect } from 'react';
import { BookOpen, Calendar, User, Eye, Tag, Filter } from 'lucide-react';
import axios from 'axios';
import './Pages.css';

const Articles = () => {
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Cargar artículos desde nueva API
        const articlesResponse = await axios.get('/api/articulos/api/articulos/');
        setArticles(articlesResponse.data.results || articlesResponse.data);
        
        // Cargar categorías
        const categoriesResponse = await axios.get('/api/articulos/api/categorias/');
        setCategories(categoriesResponse.data.results || categoriesResponse.data);
      } catch (error) {
        console.error('Error fetching data:', error);
        // Fallback con datos de ejemplo
        setArticles([]);
        setCategories([
          { id: 1, nombre: 'Noticias' },
          { id: 2, nombre: 'Entrevistas' },
          { id: 3, nombre: 'Música' },
          { id: 4, nombre: 'Eventos' }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleArticleClick = (article) => {
    setSelectedArticle(article);
  };

  const closeModal = () => {
    setSelectedArticle(null);
  };

  // Función auxiliar para obtener la imagen thumbnail (para tarjetas)
  const getArticleThumbnail = (article) => {
    // Priorizar thumbnail, luego imagen_url
    return article.imagen_thumbnail || article.imagen_url || article.imagen_portada;
  };

  // Función auxiliar para obtener la imagen banner (para modal)
  const getArticleBanner = (article) => {
    // Priorizar portada, luego imagen_url
    return article.imagen_portada || article.imagen_url;
  };

  // Filtrar artículos
  const filteredArticles = articles.filter(article => {
    const matchesCategory = !selectedCategory || article.categoria?.id === parseInt(selectedCategory);
    const matchesSearch = !searchTerm || 
      article.titulo.toLowerCase().includes(searchTerm.toLowerCase()) ||
      article.contenido.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch && article.publicado;
  });

  // Artículos destacados
  const featuredArticles = filteredArticles.filter(article => article.destacado).slice(0, 3);
  const regularArticles = filteredArticles.filter(article => !article.destacado);

  return (
    <div className="news-page">
      <div className="container">
        <div className="page-header">
          <BookOpen className="page-icon" />
          <div>
            <h1 className="page-title">Artículos</h1>
            <p className="page-subtitle">
              Noticias, entrevistas, artículos y contenido especial de Radio Oriente FM
            </p>
          </div>
        </div>

        {/* Filtros */}
        <div className="news-container">
          <div className="filters-section" style={{display: 'flex', gap: '2rem', marginBottom: '2rem', alignItems: 'center', flexWrap: 'wrap'}}>
            <div className="search-filter" style={{flex: '1', minWidth: '300px'}}>
              <input
                type="text"
                placeholder="Buscar artículos..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="form-input"
                style={{width: '100%'}}
              />
            </div>
            
            <div className="category-filter" style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              <Filter size={20} />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="form-select"
              >
                <option value="">Todas las categorías</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.nombre}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Cargando artículos...</p>
            </div>
          ) : (
            <>
              {/* Artículos destacados */}
              {featuredArticles.length > 0 && (
                <section className="featured-section">
                  <h2 className="section-title">Artículos Destacados</h2>
                  <div className="featured-news-grid">
                    {featuredArticles.map(article => (
                      <article 
                        key={article.id} 
                        className="featured-news-card"
                        onClick={() => handleArticleClick(article)}
                      >
                        {getArticleThumbnail(article) && (
                          <img src={getArticleThumbnail(article)} alt={article.titulo} className="featured-news-image" />
                        )}
                        <div className="featured-news-content">
                          <div className="meta-item" style={{marginBottom: '1rem'}}>
                            <Tag size={14} />
                            <span>{article.categoria?.nombre || 'Sin categoría'}</span>
                          </div>
                          <h3 className="featured-news-title">{article.titulo}</h3>
                          <p className="featured-news-excerpt">
                            {article.resumen || article.contenido.substring(0, 150) + '...'}
                          </p>
                          <div className="news-meta">
                            <div className="meta-item">
                              <User size={14} />
                              <span>{article.autor_nombre || 'Radio Oriente'}</span>
                            </div>
                            <div className="meta-item">
                              <Calendar size={14} />
                              <span>{formatDate(article.fecha_publicacion || article.fecha_creacion)}</span>
                            </div>
                          </div>
                        </div>
                      </article>
                    ))}
                  </div>
                </section>
              )}

              {/* Lista de artículos */}
              <section className="all-news-section">
                <h2 className="section-title">
                  {selectedCategory ? 
                    `${categories.find(c => c.id === parseInt(selectedCategory))?.nombre || 'Artículos'}` : 
                    'Todos los Artículos'
                  }
                </h2>
                
                {regularArticles.length === 0 ? (
                  <div className="no-programs" style={{textAlign: 'center', padding: '3rem'}}>
                    <BookOpen size={48} style={{color: 'var(--color-gray-400)', marginBottom: '1rem'}} />
                    <h3>No hay artículos disponibles</h3>
                    <p>No se encontraron artículos que coincidan con los filtros seleccionados.</p>
                  </div>
                ) : (
                  <div className="news-grid">
                    {regularArticles.map(article => (
                      <article 
                        key={article.id} 
                        className="news-card"
                        onClick={() => handleArticleClick(article)}
                      >
                        {getArticleThumbnail(article) && (
                          <img src={getArticleThumbnail(article)} alt={article.titulo} className="news-image" />
                        )}
                        <div className="news-content">
                          <div className="meta-item" style={{marginBottom: '1rem'}}>
                            <Tag size={14} />
                            <span>{article.categoria?.nombre || 'Sin categoría'}</span>
                          </div>
                          <h3 className="news-title">{article.titulo}</h3>
                          <p className="news-excerpt">
                            {article.resumen || article.contenido.substring(0, 120) + '...'}
                          </p>
                          <div className="news-meta">
                            <div className="meta-item">
                              <User size={14} />
                              <span>{article.autor_nombre || 'Radio Oriente'}</span>
                            </div>
                            <div className="meta-item">
                              <Calendar size={14} />
                              <span>{formatDate(article.fecha_publicacion || article.fecha_creacion)}</span>
                            </div>
                          </div>
                          <button className="read-more-btn">
                            Leer más
                          </button>
                        </div>
                      </article>
                    ))}
                  </div>
                )}
              </section>
            </>
          )}
        </div>

        {/* Modal para artículo seleccionado */}
        {selectedArticle && (
          <div className="news-modal-overlay" onClick={closeModal}>
            <div className="news-modal" onClick={(e) => e.stopPropagation()}>
              <button className="modal-close" onClick={closeModal}>×</button>
              
              {getArticleBanner(selectedArticle) && (
                <img src={getArticleBanner(selectedArticle)} alt={selectedArticle.titulo} className="modal-image" />
              )}
              
              <div className="modal-content">
                <div className="meta-item" style={{marginBottom: '1rem'}}>
                  <Tag size={16} />
                  <span>{selectedArticle.categoria?.nombre || 'Sin categoría'}</span>
                </div>
                
                <h1 className="modal-title">{selectedArticle.titulo}</h1>
                
                <div className="modal-meta">
                  <div className="meta-item">
                    <User size={16} />
                    <span>{selectedArticle.autor_nombre || 'Radio Oriente'}</span>
                  </div>
                  <div className="meta-item">
                    <Calendar size={16} />
                    <span>{formatDate(selectedArticle.fecha_publicacion || selectedArticle.fecha_creacion)}</span>
                  </div>
                </div>
                
                {selectedArticle.resumen && (
                  <div style={{marginBottom: '2rem', padding: '1rem', backgroundColor: 'var(--color-gray-50)', borderRadius: '0.5rem'}}>
                    <p><strong>{selectedArticle.resumen}</strong></p>
                  </div>
                )}
                
                <div className="modal-text">
                  <div dangerouslySetInnerHTML={{ __html: selectedArticle.contenido }} />
                </div>
                
                {/* Video embebido si existe */}
                {selectedArticle.video_url && (
                  <div style={{marginTop: '2rem'}}>
                    <h3 style={{marginBottom: '1rem', fontSize: '1.25rem', fontWeight: '600'}}>Video relacionado</h3>
                    <div style={{position: 'relative', paddingBottom: '56.25%', height: 0, overflow: 'hidden'}}>
                      <iframe
                        src={selectedArticle.video_url.includes('youtube.com') || selectedArticle.video_url.includes('youtu.be') 
                          ? selectedArticle.video_url.replace('watch?v=', 'embed/').replace('youtu.be/', 'youtube.com/embed/')
                          : selectedArticle.video_url}
                        style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none', borderRadius: '0.5rem'}}
                        allowFullScreen
                        title="Video del artículo"
                      />
                    </div>
                  </div>
                )}
                
                {/* Archivo adjunto si existe */}
                {selectedArticle.archivo_adjunto && (
                  <div style={{marginTop: '2rem', padding: '1rem', backgroundColor: 'var(--color-gray-50)', borderRadius: '0.5rem'}}>
                    <h3 style={{marginBottom: '0.5rem', fontSize: '1.125rem', fontWeight: '600'}}>📎 Archivo adjunto</h3>
                    <a 
                      href={selectedArticle.archivo_adjunto}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{color: 'var(--color-red)', textDecoration: 'underline', display: 'inline-flex', alignItems: 'center', gap: '0.5rem'}}
                    >
                      <span>Descargar archivo</span>
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Articles;
