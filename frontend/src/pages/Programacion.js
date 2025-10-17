import React, { useState, useEffect } from 'react';
import { Clock, User, Calendar } from 'lucide-react';
import axios from 'axios';
import './Pages.css';

const Programming = () => {
  const [programs, setPrograms] = useState([]);
  const [horarios, setHorarios] = useState([]);
  const [loading, setLoading] = useState(true);

  const daysOfWeek = {
    0: 'Domingo',
    1: 'Lunes',
    2: 'Martes',
    3: 'Miércoles',
    4: 'Jueves',
    5: 'Viernes',
    6: 'Sábado'
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Cargar programas
        const programsResponse = await axios.get('/api/radio/api/programas/');
        const programsData = programsResponse.data.results || programsResponse.data;
        console.log('Programas cargados:', programsData);
        setPrograms(programsData);
        
        // Cargar horarios
        const horariosResponse = await axios.get('/api/radio/api/horarios/');
        const horariosData = horariosResponse.data.results || horariosResponse.data;
        console.log('Horarios cargados:', horariosData);
        setHorarios(horariosData);
      } catch (error) {
        console.error('Error fetching data:', error);
        // Agregar datos de fallback para testing
        setPrograms([
          { id: 1, nombre: 'Buenos Días Oriente', descripcion: 'Programa matutino' },
          { id: 2, nombre: 'Tarde de Éxitos', descripcion: 'Los hits de la tarde' }
        ]);
        setHorarios([
          { id: 1, programa: 1, dia_semana: 1, hora_inicio: '06:00:00', hora_fin: '10:00:00', activo: true },
          { id: 2, programa: 2, dia_semana: 1, hora_inicio: '14:00:00', hora_fin: '18:00:00', activo: true }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const groupProgramsByDay = () => {
    const grouped = {};
    console.log('Agrupando programas por día...');
    console.log('Programas disponibles:', programs);
    console.log('Horarios disponibles:', horarios);
    
    Object.keys(daysOfWeek).forEach(dayNum => {
      const dayNumber = parseInt(dayNum);
      const horariosDelDia = horarios.filter(horario => 
        horario.dia_semana === dayNumber && (horario.activo !== false)
      );
      
      console.log(`Día ${dayNumber} (${daysOfWeek[dayNumber]}):`, horariosDelDia);
      
      grouped[dayNumber] = horariosDelDia.map(horario => {
        const programa = programs.find(p => p.id === horario.programa);
        console.log(`Horario ${horario.id} busca programa ${horario.programa}:`, programa);
        return {
          ...horario,
          programa: programa
        };
      }).sort((a, b) => a.hora_inicio.localeCompare(b.hora_inicio));
    });
    
    console.log('Programas agrupados:', grouped);
    return grouped;
  };

  const formatTime = (time) => {
    return new Date(`2000-01-01T${time}`).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const groupedPrograms = groupProgramsByDay();

  return (
    <div className="programming-page">
      <div className="container">
        <div className="page-header">
          <Calendar className="page-icon" />
          <div>
            <h1 className="page-title">Programación</h1>
            <p className="page-subtitle">
              Conoce nuestra programación semanal y no te pierdas tus programas favoritos
            </p>
          </div>
        </div>

        {loading ? (
          <div className="loading-container">
            <div className="spinner-large"></div>
            <p>Cargando programación...</p>
          </div>
        ) : (
          <div className="programming-grid">
            {Object.entries(daysOfWeek).map(([dayKey, dayName]) => {
              const dayNumber = parseInt(dayKey);
              return (
                <div key={dayKey} className="day-schedule">
                  <h2 className="day-title">{dayName}</h2>
                  <div className="programs-list">
                    {groupedPrograms[dayNumber]?.length > 0 ? (
                      groupedPrograms[dayNumber].map((horario) => (
                        <div key={`${horario.id}-${dayNumber}`} className="program-card">
                          {horario.programa?.imagen_url && (
                            <img 
                              src={horario.programa.imagen_url} 
                              alt={horario.programa.nombre}
                              className="program-image"
                            />
                          )}
                          <div className="program-content">
                            <h3 className="program-title">
                              {horario.programa?.nombre || `Programa ID: ${horario.programa || 'N/A'}`}
                            </h3>
                            <p className="program-description">
                              {horario.programa?.descripcion || 'Sin descripción disponible'}
                            </p>
                            <div className="program-meta">
                              <div className="program-time">
                                <Clock size={16} />
                                {formatTime(horario.hora_inicio)} - {formatTime(horario.hora_fin)}
                              </div>
                              {horario.programa?.conductores && horario.programa.conductores.length > 0 ? (
                                <div className="program-host">
                                  <User size={16} />
                                  {horario.programa.conductores.map(c => c.nombre).join(', ')}
                                </div>
                              ) : (
                                <div className="program-host">
                                  <User size={16} />
                                  Radio Oriente FM
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="no-programs">
                        <p>No hay programas programados para este día</p>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default Programming;
