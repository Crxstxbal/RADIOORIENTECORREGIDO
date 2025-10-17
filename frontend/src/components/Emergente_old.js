import React, { useState, useEffect } from 'react';
import { Upload, Music, Users, Link, Send } from 'lucide-react';
import axios from 'axios';
import './emergente.css'; // Importamos los estilos externos

const Emergente = () => {
    const [formData, setFormData] = useState({
        nombre_banda: '',
        integrantes: [], // Array de integrantes
        genero: '',
        comuna: '',
        email_contacto: '',
        telefono_contacto: '',
        mensaje: '',
        links: [], // Array de links
        documento_presentacion: ''
    });

    const [isLoading, setIsLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [errors, setErrors] = useState({});
    const [generos, setGeneros] = useState([]);
    const [comunas, setComunas] = useState([]);
    const [newIntegrante, setNewIntegrante] = useState('');
    const [newLink, setNewLink] = useState({ tipo: '', url: '' });

    const token = localStorage.getItem('token');
    const isLoggedIn = Boolean(token);

    // Cargar géneros y comunas
    useEffect(() => {
        const cargarDatos = async () => {
            try {
                // Cargar géneros musicales
                const generosResponse = await axios.get('/api/radio/api/generos/');
                setGeneros(generosResponse.data);
                
                // Cargar comunas
                const comunasResponse = await axios.get('/api/ubicacion/comunas/');
                setComunas(comunasResponse.data);
            } catch (error) {
                console.error('Error al cargar datos:', error);
            }
        };
        
        cargarDatos();
    }, []);

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

    // Función para manejar cambios en campos de links
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

        // Validación de sesión
        if (!isLoggedIn) {
            setErrors({ general: 'Debes iniciar sesión para enviar tu propuesta.' });
            return;
        }

        const newErrors = validateForm();
        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            return;
        }

        setIsLoading(true);

        try {
            // Preparar datos para envío
            const dataToSend = {
                nombre_banda: formData.nombre_banda,
                email_contacto: formData.email_contacto,
                telefono_contacto: formData.telefono_contacto || null,
                mensaje: formData.mensaje,
                documento_presentacion: formData.documento_presentacion || null,
                genero: formData.genero,
                comuna: formData.comuna || null,
                integrantes: formData.integrantes,
                links: formData.links
            };

            const response = await axios.post('/api/emergente/bandas/', dataToSend, {
                headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            const text = await response.text();
            let data;
            try { data = JSON.parse(text); } catch { data = text; }

            if (!response.ok) {
                let userMessage = 'Hubo un error al enviar el formulario. Revisa los datos ingresados.';
                if (data && typeof data === 'object') {
                    const firstKey = Object.keys(data)[0];
                    if (firstKey) {
                        const firstError = data[firstKey][0];
                        userMessage = firstError;
                    }
                }
                setErrors({ general: userMessage });
                return;
            }

            console.log('Banda registrada:', data);
            setSubmitted(true);
            setFormData({
                nombre_banda: '',
                integrantes: '',
                genero: '',
                ciudad: '',
                correo_contacto: '',
                telefono_contacto: '',
                mensaje: '',
                links: '',
                press_kit: null
            });

        } catch (error) {
            console.error('Fetch error:', error);
            setErrors({ general: 'Error al enviar el formulario. Revisa la consola o la red.' });
        } finally {
            setIsLoading(false);
        }
    };

    if (submitted) {
        return (
            <div className="success-container">
                <div className="card success-card">
                    <div className="success-icon">
                        <img 
                            src="/images/radiooriente.png" 
                            alt="Radio Oriente" 
                            style={{ width: '60px', height: '60px' }} 
                        />
                    </div>
                    <h2>¡Formulario Enviado Exitosamente!</h2>
                    <p>Gracias por enviar tu propuesta. Nuestro equipo revisará tu información y nos pondremos en contacto contigo pronto.</p>
                    <br />
                    <div className="buttons-container">
                        <button onClick={() => setSubmitted(false)}>Enviar Otra Propuesta</button>
                        <button 
                            onClick={() => window.location.href = 'http://localhost:3000'} 
                            style={{ marginLeft: '10px' }}
                        >
                            Ir a Página Principal
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="emergente-container">
            <div className="emergente-wrapper">
                {/* Header */}
                <div className="emergente-header">
                    <div className="logo-title">
                        <div className="logo-circle">
                            <Music className="icon" />
                        </div>
                        <h1>Radio Oriente FM</h1>
                    </div>
                    <h2 className="gradient-text">Bandas Emergentes</h2>
                    <p>
                        ¿Eres parte de una banda emergente? ¡Queremos conocerte! Envíanos tu información 
                        y podrías ser parte de nuestra programación especial para artistas locales.
                    </p>
                </div>

                <div className="grid grid-cols-2">
                    {/* Información */}
                    <div className="info-section">
                        <div className="card">
                            <div className="card-header">
                                <h3 className="card-title">
                                    <Music className="icon-red" />
                                    ¿Qué Necesitas Enviar?
                                </h3>
                            </div>
                            <ul className="info-list">
                                <li><Music className="icon-red" /> Información básica de la banda</li>
                                <li><Users className="icon-red" /> Lista de integrantes</li>
                                <li><Link className="icon-red" /> Enlaces a tu música</li>
                                <li><Upload className="icon-red" /> Press kit (opcional)</li>
                            </ul>
                        </div>

                        <div className="card">
                            <div className="card-header">
                                <h3 className="card-title">Proceso de Selección</h3>
                            </div>
                            <div className="steps">
                                <div className="step"><span>1</span> Envías tu propuesta</div>
                                <div className="step"><span>2</span> Revisamos tu material</div>
                                <div className="step"><span>3</span> Te contactamos</div>
                            </div>
                        </div>
                    </div>

                    {/* Formulario */}
                    <div className="form-section">
                        <div className="card">
                            <div className="card-header">
                                <h3 className="card-title">Envíanos tu Información</h3>
                            </div>

                            {errors.general && <div className="error-box">{errors.general}</div>}

                            <form onSubmit={handleSubmit}>
                                <div className="form-group">
                                    <label>Nombre de la Banda *</label>
                                    <input
                                        type="text"
                                        name="nombre_banda"
                                        value={formData.nombre_banda}
                                        onChange={handleChange}
                                        className={errors.nombre_banda ? 'error' : ''}
                                    />
                                    {errors.nombre_banda && <p className="error-text">{errors.nombre_banda}</p>}
                                </div>

                                <div className="form-group">
                                    <label>Integrantes</label>
                                    <textarea name="integrantes" value={formData.integrantes} onChange={handleChange} />
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Género Musical *</label>
                                        <input
                                            type="text"
                                            name="genero"
                                            value={formData.genero}
                                            onChange={handleChange}
                                            className={errors.genero ? 'error' : ''}
                                        />
                                        {errors.genero && <p className="error-text">{errors.genero}</p>}
                                    </div>
                                    <div className="form-group">
                                        <label>Ciudad</label>
                                        <input type="text" name="ciudad" value={formData.ciudad} onChange={handleChange} />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Correo Electrónico *</label>
                                        <input
                                            type="email"
                                            name="correo_contacto"
                                            value={formData.correo_contacto}
                                            onChange={handleChange}
                                            className={errors.correo_contacto ? 'error' : ''}
                                        />
                                        {errors.correo_contacto && <p className="error-text">{errors.correo_contacto}</p>}
                                    </div>
                                    <div className="form-group">
                                        <label>Teléfono</label>
                                        <input type="tel" name="telefono_contacto" value={formData.telefono_contacto} onChange={handleChange} />
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label>Enlaces a tu Música</label>
                                    <textarea name="links" value={formData.links} onChange={handleChange} />
                                </div>

                                <div className="form-group">
                                    <label>Mensaje *</label>
                                    <textarea
                                        name="mensaje"
                                        value={formData.mensaje}
                                        onChange={handleChange}
                                        className={errors.mensaje ? 'error' : ''}
                                    />
                                    {errors.mensaje && <p className="error-text">{errors.mensaje}</p>}
                                </div>

                                <div className="form-group">
                                    <label>Press Kit (PDF, DOC, ZIP - Opcional)</label>
                                    <input type="file" name="press_kit" onChange={handleFileChange} accept=".pdf,.doc,.docx,.zip,.rar" />
                                </div>

                                <button
                                    type="submit"
                                    className="submit-btn"
                                    disabled={isLoading || !isLoggedIn}
                                >
                                    {isLoading ? <div className="spinner"></div> : <Send className="icon" />}
                                    {isLoading ? ' Enviando...' : isLoggedIn ? ' Enviar Propuesta' : 'Debes iniciar sesión'}
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Emergente;
