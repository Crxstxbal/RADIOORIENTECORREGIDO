// frontend/src/components/CarruselLocutores.jsx

import React, { useState, useEffect } from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination, Autoplay } from 'swiper/modules';
import axios from 'axios'; // <-- 1. Importamos axios

// Importa los estilos de Swiper
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';

import './CarruselLocutores.css'; 

const API_URL = '/api/radio/locutores/activos/';

const CarruselLocutores = () => {
  // El estado inicial DEBE ser un array vacío
  const [locutores, setLocutores] = useState([]); 
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLocutores = async () => {
      try {
        console.log('Fetching locutores from:', API_URL);
        const response = await axios.get(API_URL);
        const data = response.data;
        console.log('API Response:', data);

        // ---- ESTA ES LA SOLUCIÓN MEJORADA ----
        let locutoresData = [];
        
        if (data && Array.isArray(data.results)) {
          // 1. Si es una respuesta paginada, usamos .results
          locutoresData = data.results;
        } else if (data && Array.isArray(data)) {
          // 2. Si es una respuesta de array simple, la usamos
          locutoresData = data;
        } else {
          // 3. Si es cualquier otra cosa (null, objeto, etc.), dejamos un array vacío
          console.error("La API no devolvió un array de locutores:", data);
        }

        // Log de depuración para las URLs de las imágenes
        console.log('Locutores con sus fotos:', locutoresData.map(l => ({
          id: l.id,
          nombre: l.nombre,
          foto_url: l.foto_url,
          foto_completa: l.foto_url ? new URL(l.foto_url, window.location.origin).href : 'No tiene foto'
        })));

        setLocutores(locutoresData);
        // -------------------------------------

      } catch (error) {
        console.error("Error al cargar locutores:", error);
        // 4. Si la API falla (404, 500), también dejamos un array vacío
        setLocutores([]); // <-- Garantiza que sea un array
      } finally {
        setLoading(false);
      }
    };

    fetchLocutores();
  }, []); // Array de dependencias vacío, se ejecuta 1 vez

  if (loading) {
    return (
      <div className="locutores-carrusel-container">
        <h2>Nuestros Locutores</h2>
        <div style={{ textAlign: 'center', padding: '20px', color: '#fff' }}>
          Cargando locutores...
        </div>
      </div>
    );
  }

  // Si no hay locutores, mostramos un mensaje
  if (locutores.length === 0) {
    return (
      <div className="locutores-carrusel-container">
        <h2>Nuestros Locutores</h2>
        <div style={{ textAlign: 'center', padding: '20px', color: '#fff' }}>
          No hay locutores disponibles en este momento.
        </div>
      </div>
    );
  }

  return (
    <div className="locutores-carrusel-container">
      <div className="title-container">
        <h2>Nuestros Locutores</h2>
      </div>
      <Swiper
        modules={[Navigation, Pagination, Autoplay]}
        spaceBetween={30}
        slidesPerView={4}
        navigation
        pagination={{ clickable: true }}
        autoplay={{
          delay: 3000,
          disableOnInteraction: false,
        }}
        breakpoints={{
          320: { slidesPerView: 1, spaceBetween: 10 },
          768: { slidesPerView: 2, spaceBetween: 20 },
          1024: { slidesPerView: 4, spaceBetween: 30 },
        }}
      >
        {/* LÍNEA 74 (ahora): 
          'locutores' está GARANTIZADO que es un array, 
          por lo que .map() NUNCA fallará.
        */}
        {locutores.map(locutor => (
          <SwiperSlide key={locutor.id} className="locutor-slide">
            <div className="avatar-wrap">
              <div className="avatar-ring">
                <div className="avatar-inner">
                  <img
                    src={locutor.foto_url}
                    alt={`${locutor.nombre} ${locutor.apellido}`}
                    onError={(e) => {
                      console.error('Error al cargar la imagen:', locutor.foto_url);
                      e.target.style.display = 'none';
                      e.target.nextElementSibling.style.display = 'flex';
                    }}
                    style={{ display: locutor.foto_url ? 'block' : 'none' }}
                  />
                  <div className="placeholder-avatar" style={{ display: locutor.foto_url ? 'none' : 'flex' }}>
                    {locutor.nombre?.charAt(0)}{locutor.apellido?.charAt(0) || ''}
                  </div>
                </div>
              </div>
            </div>
            <h3 className="locutor-nombre">{locutor.apodo || `${locutor.nombre}`}</h3>
            <p className="locutor-rol">{locutor.nombre} {locutor.apellido}</p>
          </SwiperSlide>
        ))}
      </Swiper>
    </div>
  );
};

export default CarruselLocutores;