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
        const response = await axios.get(API_URL);
        const data = response.data;

        // ---- ESTA ES LA SOLUCIÓN MEJORADA ----
        if (data && Array.isArray(data.results)) {
          // 1. Si es una respuesta paginada, usamos .results
          setLocutores(data.results);
        } else if (data && Array.isArray(data)) {
          // 2. Si es una respuesta de array simple, la usamos
          setLocutores(data);
        } else {
          // 3. Si es cualquier otra cosa (null, objeto, etc.), dejamos un array vacío
          console.error("La API no devolvió un array de locutores:", data);
          setLocutores([]); // <-- Garantiza que sea un array
        }
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
    return <div>Cargando locutores...</div>;
  }

  // Si no hay locutores, simplemente no mostramos nada.
  if (locutores.length === 0) {
    return null; 
  }

  return (
    <div className="locutores-carrusel-container">
      <h2>Nuestros Locutores</h2>
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
            <img src={locutor.foto_url} alt={`${locutor.nombre} ${locutor.apellido}`} />
            <h3>{locutor.apodo || locutor.nombre}</h3>
            <p>{locutor.nombre} {locutor.apellido}</p>
          </SwiperSlide>
        ))}
      </Swiper>
    </div>
  );
};

export default CarruselLocutores;