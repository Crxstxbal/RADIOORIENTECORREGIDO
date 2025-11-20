import React, { useState, useEffect } from 'react';
import { Upload, Music, Users, Link, Send, X, Plus, CheckCircle, User, MapPin, Mail, Phone, Globe, Radio, Home } from 'lucide-react';
import {
  FaSpotify,
  FaYoutube,
  FaInstagram,
  FaFacebook,
  FaTiktok,
  FaSoundcloud,
  FaLink,
  FaTwitter,
  FaBandcamp,
  FaApple
} from 'react-icons/fa';
import toast from 'react-hot-toast';
import './emergente.css';

const Emergente = () => {
    const [formData, setFormData] = useState({
        nombre_banda: '',
        integrantes: [],
        genero: '',
        pais: '',
        ciudad: '',
        comuna: '',
        email_contacto: '',
        telefono_contacto: '',
        mensaje: '',
        links: [],
        documento_presentacion: ''
    });

    const [isLoading, setIsLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [errors, setErrors] = useState({});
    const [generos, setGeneros] = useState([]);
    const [paises, setPaises] = useState([]);
    const [ciudades, setCiudades] = useState([]);
    const [comunas, setComunas] = useState([]);
    const [isLoadingCiudades, setIsLoadingCiudades] = useState(false);
    const [isLoadingComunas, setIsLoadingComunas] = useState(false);
    const [newIntegrante, setNewIntegrante] = useState('');
    const [newLink, setNewLink] = useState({ tipo: '', url: '' });

    const token = localStorage.getItem('token');
    const isLoggedIn = Boolean(token);

    // Cargar países al iniciar
    useEffect(() => {
        const inicializarDatos = async () => {
            try {
                // Verificar si hay países
                const paisesResponse = await fetch('/api/ubicacion/paises/');
                if (!paisesResponse.ok) {
                    throw new Error('Error al cargar países');
                }
                const paisesData = await paisesResponse.json();

                // Los endpoints DRF devuelven objetos paginados con { results: [] }
                const paisesArray = paisesData.results || (Array.isArray(paisesData) ? paisesData : []);

                // Si no hay países o no está Chile, reiniciar datos desde API
                const chile = paisesArray.find(p => p.nombre === 'Chile');

                if (!chile) {
                    console.log('Chile no encontrado, cargando datos desde API...');
                    const loadingToast = toast.loading('Cargando regiones y comunas de Chile desde API oficial...');

                    try {
                        const response = await fetch('/api/ubicacion/paises/reiniciar_datos_chile/', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' }
                        });
                        if (response.ok) {
                            const data = await response.json();
                            toast.dismiss(loadingToast);
                            toast.success(`✅ ${data.message}\n📍 ${data.regiones_creadas} regiones\n🏘️ ${data.comunas_creadas} comunas`);

                            // Recargar países
                            const paisesActualizadosResponse = await fetch('/api/ubicacion/paises/');
                            if (paisesActualizadosResponse.ok) {
                                const paisesActualizados = await paisesActualizadosResponse.json();
                                const paisesActualizadosArray = paisesActualizados.results || (Array.isArray(paisesActualizados) ? paisesActualizados : []);
                                setPaises(paisesActualizadosArray);
                                // Seleccionar Chile por defecto si no hay país seleccionado
                                const chileNuevo = paisesActualizadosArray.find(p => p.nombre === 'Chile');
                                if (chileNuevo && !formData.pais) {
                                    setFormData(prev => ({ ...prev, pais: chileNuevo.id }));
                                }
                            }
                        } else {
                            throw new Error('Error al reiniciar datos');
                        }
                    } catch (apiError) {
                        toast.dismiss(loadingToast);
                        console.error('Error al cargar desde API:', apiError);
                        toast.error('No se pudieron cargar los datos desde la API');
                        setPaises([]);
                    }
                } else {
                    // Chile existe, verificar si tiene regiones
                    const ciudadesResponse = await fetch(`/api/ubicacion/ciudades/por_pais/?pais_id=${chile.id}`);
                    const ciudadesData = ciudadesResponse.ok ? await ciudadesResponse.json() : [];

                    // Si no hay regiones o hay muy pocas, recargar desde API
                    if (!ciudadesData || ciudadesData.length < 10) {
                        console.log('Pocas o ninguna región, recargando desde API...');
                        const loadingToast = toast.loading('Actualizando datos desde API oficial de Chile...');

                        try {
                            const response = await fetch('/api/ubicacion/paises/reiniciar_datos_chile/', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' }
                            });
                            if (response.ok) {
                                const data = await response.json();
                                toast.dismiss(loadingToast);
                                toast.success(`Datos actualizados: ${data.regiones_creadas} regiones, ${data.comunas_creadas} comunas`);
                            }
                        } catch (apiError) {
                            toast.dismiss(loadingToast);
                            console.error('Error al actualizar desde API:', apiError);
                        }
                    }

                    setPaises(paisesArray);
                    // Seleccionar Chile por defecto si no hay país seleccionado
                    if (chile && !formData.pais) {
                        setFormData(prev => ({ ...prev, pais: chile.id }));
                    }
                }
            } catch (error) {
                console.error('Error al inicializar datos:', error);
                toast.error('Error al cargar la lista de países');
                setPaises([]);
            }
        };

        // Cargar géneros musicales
        const cargarGeneros = async () => {
            try {
                const response = await fetch('/api/radio/api/generos/');
                if (!response.ok) {
                    throw new Error('Error al cargar géneros');
                }
                const data = await response.json();
                // Los endpoints DRF devuelven objetos paginados con { results: [] }
                const generosArray = data.results || (Array.isArray(data) ? data : []);
                setGeneros(generosArray);
            } catch (error) {
                console.error('Error al cargar géneros musicales:', error);
                toast.error('Error al cargar la lista de géneros musicales');
                // Fallback con datos por defecto
                setGeneros([
                    { id: 1, nombre: 'Rock' },
                    { id: 2, nombre: 'Pop' },
                    { id: 3, nombre: 'Reggaeton' },
                    { id: 4, nombre: 'Cumbia' }
                ]);
            }
        };

        inicializarDatos();
        cargarGeneros();
    }, []);

    // Cargar ciudades cuando se selecciona un país
    useEffect(() => {
        const cargarCiudades = async () => {
            if (!formData.pais) {
                setCiudades([]);
                setComunas([]);
                setFormData(prev => ({
                    ...prev,
                    ciudad: '',
                    comuna: ''
                }));
                return;
            }

            setIsLoadingCiudades(true);
            try {
                console.log('Solicitando ciudades para país ID:', formData.pais);
                const response = await fetch(`/api/ubicacion/ciudades/por_pais/?pais_id=${formData.pais}`);

                if (!response.ok) {
                    throw new Error('Error al cargar ciudades');
                }

                const data = await response.json();
                console.log('Respuesta de ciudades:', data);

                // La respuesta ya debería ser un array
                const ciudadesData = Array.isArray(data) ? data : [];

                setCiudades(ciudadesData);

                // Resetear ciudad y comuna cuando cambia el país
                setFormData(prev => ({
                    ...prev,
                    ciudad: '',
                    comuna: ''
                }));
            } catch (error) {
                console.error('Error al cargar ciudades:', error);
                toast.error('Error al cargar las ciudades. Intenta nuevamente.');
                setCiudades([]);
                setComunas([]);
            } finally {
                setIsLoadingCiudades(false);
            }
        };

        cargarCiudades();
    }, [formData.pais]);

    // Cargar comunas cuando se selecciona una ciudad
    useEffect(() => {
        const cargarComunas = async () => {
            if (!formData.ciudad) {
                setComunas([]);
                setFormData(prev => ({
                    ...prev,
                    comuna: ''
                }));
                return;
            }

            setIsLoadingComunas(true);
            try {
                console.log('Solicitando comunas para ciudad ID:', formData.ciudad);
                const response = await fetch(`/api/ubicacion/comunas/por_ciudad/?ciudad_id=${formData.ciudad}`);

                if (!response.ok) {
                    throw new Error('Error al cargar comunas');
                }

                const data = await response.json();
                console.log('Respuesta de comunas:', data);

                // La respuesta ya debería ser un array
                const comunasData = Array.isArray(data) ? data : [];
                setComunas(comunasData);

                // Resetear comuna cuando cambia la ciudad
                setFormData(prev => ({
                    ...prev,
                    comuna: ''
                }));
            } catch (error) {
                console.error('Error al cargar comunas:', error);
                toast.error('Error al cargar las comunas. Intenta nuevamente.');
                setComunas([]);
            } finally {
                setIsLoadingComunas(false);
            }
        };

        cargarComunas();
    }, [formData.ciudad]);

    // Funciones para manejar integrantes
    const agregarIntegrante = () => {
        if (newIntegrante.trim()) {
            setFormData(prev => ({
                ...prev,
                integrantes: [...prev.integrantes, newIntegrante.trim()]
            }));
            setNewIntegrante('');
        }
    };

    const eliminarIntegrante = (index) => {
        setFormData(prev => ({
            ...prev,
            integrantes: prev.integrantes.filter((_, i) => i !== index)
        }));
    };

    // Funciones para manejar links
    const agregarLink = () => {
        if (newLink.tipo && newLink.url.trim()) {
            setFormData(prev => ({
                ...prev,
                links: [...prev.links, { ...newLink }]
            }));
            setNewLink({ tipo: '', url: '' });
        }
    };

    const eliminarLink = (index) => {
        setFormData(prev => ({
            ...prev,
            links: prev.links.filter((_, i) => i !== index)
        }));
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));

        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    const handleLinkChange = (e) => {
        const { name, value } = e.target;
        setNewLink(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const validateForm = () => {
        const newErrors = {};
        if (!formData.nombre_banda.trim()) newErrors.nombre_banda = 'El nombre de la banda es requerido';
        if (!formData.genero) newErrors.genero = 'El género musical es requerido';
        if (!formData.email_contacto.trim()) {
            newErrors.email_contacto = 'El correo electrónico es requerido';
        } else if (!/\S+@\S+\.\S+/.test(formData.email_contacto)) {
            newErrors.email_contacto = 'Por favor ingresa un correo electrónico válido';
        }
        if (!formData.mensaje.trim()) newErrors.mensaje = 'El mensaje es requerido';
        if (formData.integrantes.length === 0) newErrors.integrantes = 'Debes agregar al menos un integrante';
        return newErrors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log('🚀 Iniciando envío del formulario...');
        console.log('📝 Datos del formulario:', formData);
        console.log('🔑 Token disponible:', !!token);
        console.log('👤 Usuario logueado:', isLoggedIn);

        // Limpiar errores previos
        setErrors({});

        if (!isLoggedIn) {
            const errorMsg = 'Debes iniciar sesión para enviar tu propuesta.';
            setErrors({ general: errorMsg });
            toast.error(errorMsg);
            return;
        }

        const newErrors = validateForm();
        if (Object.keys(newErrors).length > 0) {
            console.log('❌ Errores de validación:', newErrors);
            setErrors(newErrors);
            toast.error('Por favor corrige los errores en el formulario.');
            return;
        }

        setIsLoading(true);

        try {
            const dataToSend = {
                nombre_banda: formData.nombre_banda.trim(),
                email_contacto: formData.email_contacto.trim(),
                telefono_contacto: formData.telefono_contacto?.trim() || '',
                mensaje: formData.mensaje.trim(),
                documento_presentacion: formData.documento_presentacion?.trim() || '',
                genero: parseInt(formData.genero),
                comuna: formData.comuna ? parseInt(formData.comuna) : null,
                integrantes_data: formData.integrantes.filter(i => i.trim()),
                links_data: formData.links.filter(l => l.tipo && l.url.trim())
            };

            console.log('📤 Enviando datos:', dataToSend);

            const response = await fetch('/api/emergentes/api/bandas/', {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dataToSend)
            });

            if (response.ok) {
                const data = await response.json();
                console.log('✅ Respuesta exitosa:', data);
                toast.success('¡Propuesta enviada exitosamente! Te contactaremos pronto.');
                setSubmitted(true);

                // Limpiar formulario
                setFormData({
                    nombre_banda: '',
                    integrantes: [],
                    genero: '',
                    comuna: '',
                    email_contacto: '',
                    telefono_contacto: '',
                    mensaje: '',
                    links: [],
                    documento_presentacion: ''
                });
            } else {
                const errorData = await response.json();
                console.error('📄 Respuesta del servidor:', errorData);
                console.error('🔢 Código de estado:', response.status);

                let errorMessage = 'Error al enviar la propuesta. Inténtalo de nuevo.';

                if (errorData) {
                    console.log('📋 Datos del error:', errorData);

                    if (typeof errorData === 'object') {
                        // Mostrar errores específicos de campos
                        setErrors(errorData);

                        // Crear mensaje de error más específico
                        const firstError = Object.values(errorData)[0];
                        if (Array.isArray(firstError)) {
                            errorMessage = firstError[0];
                        } else if (typeof firstError === 'string') {
                            errorMessage = firstError;
                        }
                    } else {
                        errorMessage = errorData.toString();
                    }
                }

                toast.error(errorMessage);
                console.log('🚨 Error mostrado al usuario:', errorMessage);
            }
        } catch (error) {
            console.error('❌ Error completo:', error);
            toast.error('Error al enviar la propuesta. Inténtalo de nuevo.');
            console.log('🚨 Error mostrado al usuario:', error.message);
        } finally {
            setIsLoading(false);
        }
    };

    const resetForm = () => {
        setSubmitted(false);
        setFormData({
            nombre_banda: '',
            integrantes: [],
            genero: '',
            comuna: '',
            email_contacto: '',
            telefono_contacto: '',
            mensaje: '',
            links: [],
            documento_presentacion: ''
        });
        setErrors({});
    };

    if (submitted) {
        return (
            <div className="success-container">
                <div className="success-card">
                    <div className="success-animation">
                        <div className="success-icon-wrapper">
                            <CheckCircle className="success-icon" size={80} />
                        </div>
                        <div className="success-waves">
                            <div className="wave wave-1"></div>
                            <div className="wave wave-2"></div>
                            <div className="wave wave-3"></div>
                        </div>
                    </div>
                    
                    <div className="success-content">
                        <h2 className="success-title">¡Propuesta Enviada con Éxito!</h2>
                        <p className="success-message">
                            Tu banda ha sido registrada en nuestro sistema. Nuestro equipo de curaduría 
                            revisará tu propuesta musical y nos pondremos en contacto contigo pronto.
                        </p>
                        
                        <div className="success-info">
                            <div className="info-item">
                                <Music className="info-icon" />
                                <span>Revisión en 3-5 días hábiles</span>
                            </div>
                            <div className="info-item">
                                <Mail className="info-icon" />
                                <span>Te contactaremos por email</span>
                            </div>
                            <div className="info-item">
                                <Radio className="info-icon" />
                                <span>Posible emisión los domingos</span>
                            </div>
                        </div>
                    </div>
                    
                    <div className="success-actions">
                        <button onClick={resetForm} className="btn btn-primary success-btn">
                            <Plus size={20} />
                            Enviar Otra Propuesta
                        </button>
                        <button 
                            onClick={() => window.location.href = '/'} 
                            className="btn btn-outline success-btn"
                        >
                            <Home size={20} />
                            Ir a Página Principal
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="emergente-container">
            <div className="container">
                <div className="page-header">
                    <Music className="page-icon" />
                    <div>
                        <h1 className="page-title">Bandas Emergentes</h1>
                        <p className="page-subtitle">
                            ¿Eres parte de una banda emergente? ¡Queremos conocerte! Envíanos tu información y podrías ser parte de nuestra programación especial para artistas locales.
                        </p>
                    </div>
                </div>

                <div className="emergente-content">
                    <div className="emergente-info">
                        <h2 className="section-title">¿Por qué participar?</h2>
                        
                        <div className="emergente-item">
                            <Users className="emergente-icon" />
                            <div>
                                <h3>Beneficios para tu banda</h3>
                                <ul className="benefits-list">
                                    <li>Tu música puede sonar en nuestro espacio dominical de bandas emergentes, entre las 12:00 y las 15:00 hrs.</li>
                                    <li>Posibilidad de entrevistas en vivo y conversación en profundidad sobre tu proyecto.</li>
                                    <li>Difusión en la programación de Radio Oriente FM y en nuestras redes sociales.</li>
                                    <li>Visibilidad frente a una audiencia que busca descubrir nuevas voces y propuestas serias.</li>
                                    <li>Conexión con otras bandas y solistas que también están construyendo la escena local.</li>
                                    <li>Ser parte de una curaduría donde se valora la calidad, la identidad y la coherencia artística.</li>
                                </ul>
                            </div>
                        </div>

                        <div className="emergente-item">
                            <Link className="emergente-icon" />
                            <div>
                                <h3>Proceso de Selección</h3>
                                <div className="process-steps">
                                    <div className="step"><span>1</span> Envías tu información y material a través de este formulario.</div>
                                    <div className="step"><span>2</span> Nuestro equipo revisa tu propuesta: sonido, mensaje, originalidad y seriedad del proyecto.</div>
                                    <div className="step"><span>3</span> Te contactamos si eres seleccionado para coordinar la emisión de tu música y posibles entrevistas en el programa de Bandas Emergentes.</div>
                                </div>
                            </div>
                        </div>

                        <p className="form-description">
                            Las bandas y solistas seleccionados formarán parte de nuestro espacio de bandas emergentes los domingos, donde dedicamos la franja de 12:00 a 15:00 hrs. a escuchar y compartir nuevas propuestas musicales.
                        </p>
                    </div>

                    <div className="emergente-form-container">
                        <h2 className="section-title">Envíanos tu Información</h2>
                        <p className="form-description">Completa el formulario y nos pondremos en contacto contigo pronto</p>

                                {errors.general && <div className="error-box">{errors.general}</div>}

                                <form onSubmit={handleSubmit}>
                                    {/* Nombre de la banda */}
                                    <div className="form-group">
                                        <label>Nombre de la Banda *</label>
                                        <input
                                            type="text"
                                            name="nombre_banda"
                                            value={formData.nombre_banda}
                                            onChange={handleChange}
                                            className={errors.nombre_banda ? 'error' : ''}
                                            placeholder="Ej: Los Prisioneros"
                                        />
                                        {errors.nombre_banda && <p className="error-text">{errors.nombre_banda}</p>}
                                    </div>

                                {/* Integrantes */}
                                <div className="form-group">
                                    <label>Integrantes *</label>
                                    <div className="integrantes-section">
                                        <div className="add-section">
                                            <input
                                                type="text"
                                                value={newIntegrante}
                                                onChange={(e) => setNewIntegrante(e.target.value)}
                                                placeholder="Nombre del integrante"
                                                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), agregarIntegrante())}
                                            />
                                            <button type="button" onClick={agregarIntegrante} className="btn btn-primary btn-small">
                                                <Plus size={16} />
                                                Agregar
                                            </button>
                                        </div>
                                        {formData.integrantes.length > 0 && (
                                            <div className="integrantes-list">
                                                {formData.integrantes.map((integrante, index) => (
                                                    <div key={index} className="integrante-item">
                                                        <div className="integrante-info">
                                                            <User className="integrante-icon" size={18} />
                                                            <span className="integrante-nombre">{integrante}</span>
                                                        </div>
                                                        <button 
                                                            type="button" 
                                                            onClick={() => eliminarIntegrante(index)}
                                                            className="btn-remove"
                                                            title="Eliminar integrante"
                                                        >
                                                            <X size={14} />
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                    {errors.integrantes && <p className="error-text">{errors.integrantes}</p>}
                                </div>

                                <div className="form-row">
                                    {/* Género Musical */}
                                    <div className="form-group">
                                        <label>Género Musical *</label>
                                        <select
                                            name="genero"
                                            value={formData.genero}
                                            onChange={handleChange}
                                            className={errors.genero ? 'error' : ''}
                                        >
                                            <option value="">Selecciona un género</option>
                                            {generos.map((genero) => (
                                                <option key={genero.id} value={genero.id}>
                                                    {genero.nombre}
                                                </option>
                                            ))}
                                        </select>
                                        {errors.genero && <p className="error-text">{errors.genero}</p>}
                                    </div>
                                </div>

                                {/* Ubicación */}
                                <div className="form-row location-row">
                                    <div className="form-group">
                                        <label htmlFor="pais">País *</label>
                                        <select
                                            id="pais"
                                            name="pais"
                                            value={formData.pais}
                                            onChange={handleChange}
                                            className={errors.pais ? 'error' : ''}
                                            disabled={isLoading}
                                        >
                                            <option value="">Selecciona un país</option>
                                            {paises.map(pais => (
                                                <option key={pais.id} value={pais.id}>
                                                    {pais.nombre}
                                                </option>
                                            ))}
                                        </select>
                                        {errors.pais && <p className="error-text">{errors.pais}</p>}
                                    </div>

                                    <div className={`form-group ${isLoadingCiudades ? 'loading' : ''}`}>
                                        <label htmlFor="ciudad">Región *</label>
                                        <select
                                            id="ciudad"
                                            name="ciudad"
                                            value={formData.ciudad}
                                            onChange={handleChange}
                                            className={errors.ciudad ? 'error' : ''}
                                            disabled={!formData.pais || isLoadingCiudades}
                                        >
                                            <option value="">
                                                {isLoadingCiudades ? 'Cargando regiones...' : 'Selecciona una región'}
                                            </option>
                                            {ciudades.map(ciudad => (
                                                <option key={ciudad.id} value={ciudad.id}>
                                                    {ciudad.nombre}
                                                </option>
                                            ))}
                                        </select>
                                        {errors.ciudad && <p className="error-text">{errors.ciudad}</p>}
                                    </div>

                                    <div className={`form-group ${isLoadingComunas ? 'loading' : ''}`}>
                                        <label htmlFor="comuna">Comuna *</label>
                                        <select
                                            id="comuna"
                                            name="comuna"
                                            value={formData.comuna}
                                            onChange={handleChange}
                                            className={errors.comuna ? 'error' : ''}
                                            disabled={!formData.ciudad || isLoadingComunas}
                                        >
                                            <option value="">
                                                {isLoadingComunas ? 'Cargando comunas...' : 'Selecciona una comuna'}
                                            </option>
                                            {comunas.map(comuna => (
                                                <option key={comuna.id} value={comuna.id}>
                                                    {comuna.nombre}
                                                </option>
                                            ))}
                                        </select>
                                        {errors.comuna && <p className="error-text">{errors.comuna}</p>}
                                    </div>
                                </div>

                                {/* Contacto */}
                                <div className="form-row">
                                    {/* Email */}
                                    <div className="form-group">
                                        <label>Correo Electrónico *</label>
                                        <input
                                            type="email"
                                            name="email_contacto"
                                            value={formData.email_contacto}
                                            onChange={handleChange}
                                            className={errors.email_contacto ? 'error' : ''}
                                            placeholder="banda@ejemplo.com"
                                        />
                                        {errors.email_contacto && <p className="error-text">{errors.email_contacto}</p>}
                                    </div>

                                    {/* Teléfono */}
                                    <div className="form-group">
                                        <label>Teléfono</label>
                                        <input
                                            type="tel"
                                            name="telefono_contacto"
                                            value={formData.telefono_contacto}
                                            onChange={handleChange}
                                            placeholder="+56 9 1234 5678"
                                        />
                                    </div>
                                </div>

                                {/* Links */}
                                <div className="form-group">
                                    <label>Links (Redes Sociales, Música, etc.)</label>
                                    <div className="links-section">
                                        <div className="add-link-container">
                                            <div className="select-with-icon">
                                                <select
                                                    name="tipo"
                                                    value={newLink.tipo}
                                                    onChange={handleLinkChange}
                                                    className="link-type-select"
                                                >
                                                    <option value="">Tipo de link</option>
                                                    <option value="spotify">Spotify</option>
                                                    <option value="youtube">YouTube</option>
                                                    <option value="instagram">Instagram</option>
                                                    <option value="facebook">Facebook</option>
                                                    <option value="soundcloud">SoundCloud</option>
                                                    <option value="website">Sitio Web</option>
                                                    <option value="otro">Otro</option>
                                                </select>
                                                {newLink.tipo && (
                                                    <span className={`select-icon ${newLink.tipo}`}>
                                                        {newLink.tipo === 'spotify' && <FaSpotify size={18} />}
                                                        {newLink.tipo === 'youtube' && <FaYoutube size={18} />}
                                                        {newLink.tipo === 'instagram' && <FaInstagram size={18} />}
                                                        {newLink.tipo === 'facebook' && <FaFacebook size={18} />}
                                                        {newLink.tipo === 'soundcloud' && <FaSoundcloud size={18} />}
                                                        {newLink.tipo === 'website' && <Globe size={18} />}
                                                        {newLink.tipo === 'otro' && <FaLink size={18} />}
                                                    </span>
                                                )}
                                            </div>
                                            <input
                                                type="url"
                                                name="url"
                                                value={newLink.url}
                                                onChange={handleLinkChange}
                                                placeholder="https://..."
                                                className="link-url-input"
                                            />
                                            <button 
                                                type="button" 
                                                onClick={agregarLink} 
                                                className="btn btn-primary btn-small"
                                                disabled={!newLink.tipo || !newLink.url}
                                            >
                                                <Plus size={16} />
                                                Agregar
                                            </button>
                                        </div>
                                        {formData.links.length > 0 && (
                                            <div className="links-list">
                                                {formData.links.map((link, index) => {
                                                    const getSocialIcon = (tipo) => {
                                                        switch(tipo.toLowerCase()) {
                                                            case 'spotify': return <FaSpotify className="social-icon spotify" />;
                                                            case 'youtube': return <FaYoutube className="social-icon youtube" />;
                                                            case 'instagram': return <FaInstagram className="social-icon instagram" />;
                                                            case 'facebook': return <FaFacebook className="social-icon facebook" />;
                                                            case 'tiktok': return <FaTiktok className="social-icon tiktok" />;
                                                            case 'soundcloud': return <FaSoundcloud className="social-icon soundcloud" />;
                                                            case 'twitter': return <FaTwitter className="social-icon twitter" />;
                                                            case 'bandcamp': return <FaBandcamp className="social-icon bandcamp" />;
                                                            case 'apple music': return <FaApple className="social-icon apple" />;
                                                            case 'sitio web': return <Globe className="social-icon website" />;
                                                            default: return <FaLink className="social-icon default" />;
                                                        }
                                                    };
                                                    
                                                    return (
                                                        <div key={index} className="link-item">
                                                            <div className="link-info">
                                                                <div className="link-icon-wrapper">
                                                                    {getSocialIcon(link.tipo)}
                                                                </div>
                                                                <div className="link-details">
                                                                    <span className="link-type">{link.tipo}</span>
                                                                    <span className="link-url">{link.url}</span>
                                                                </div>
                                                            </div>
                                                            <button 
                                                                type="button" 
                                                                onClick={() => eliminarLink(index)}
                                                                className="btn-remove"
                                                                title="Eliminar link"
                                                            >
                                                                <X size={16} />
                                                            </button>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Documento de presentación */}
                                <div className="form-group">
                                    <label>Documento de Presentación (URL)</label>
                                    <input
                                        type="url"
                                        name="documento_presentacion"
                                        value={formData.documento_presentacion}
                                        onChange={handleChange}
                                        placeholder="https://drive.google.com/... o enlace a tu EPK"
                                    />
                                    <small>Enlace a tu EPK, portfolio o material promocional</small>
                                </div>

                                {/* Mensaje */}
                                <div className="form-group">
                                    <label>Mensaje *</label>
                                    <textarea
                                        name="mensaje"
                                        value={formData.mensaje}
                                        onChange={handleChange}
                                        className={errors.mensaje ? 'error' : ''}
                                        rows="4"
                                        placeholder="Cuéntanos sobre tu banda, tu música y por qué quieres participar..."
                                    />
                                    {errors.mensaje && <p className="error-text">{errors.mensaje}</p>}
                                </div>

                                <button 
                                    type="submit" 
                                    className="btn btn-primary" 
                                    disabled={isLoading}
                                >
                                    <Send size={16} />
                                    {isLoading ? 'Enviando...' : 'Enviar Propuesta'}
                                </button>
                                </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Emergente;
