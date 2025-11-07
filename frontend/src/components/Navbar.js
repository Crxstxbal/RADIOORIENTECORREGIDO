import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Menu, X, Radio, User, Sun, Moon, LayoutDashboard } from "lucide-react";
import { useTheme } from "../contexts/ThemeContext";
import "./Navbar.css";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { user, logout, isAuthenticated, isAdmin } = useAuth();
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const dashboardUrl = import.meta.env.VITE_DASHBOARD_URL || 'http://localhost:8000/dashboard/';

  const navItems = [
    { name: "Inicio", path: "/" },
    { name: "Programación", path: "/programacion" },
    { name: "Artículos", path: "/articulos" },
    { name: "Contacto", path: "/contacto" },
    { name: "Suscripción", path: "/suscripcion" }
  ];

  const isActive = (path) => location.pathname === path;

  const handleLogout = () => {
    logout();
    setIsOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="container">
        <div className="nav-content">
          {/* Logo */}
          <Link to="/" className="nav-logo">
            <img
              src="/images/logo.png"
              alt="Radio Oriente FM"
              className="logo-icon"
            />
            <span className="logo-text">Radio Oriente FM</span>
          </Link>

          {/* Links desktop */}
          <div className="nav-links desktop">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${isActive(item.path) ? "active" : ""}`}
              >
                {item.icon && <span className="nav-icon">{item.icon}</span>}
                {item.name}
              </Link>
            ))}
            {/* Link Dashboard solo para administradores */}
            {isAdmin && (
              <a
                href={dashboardUrl}
                className="nav-link dashboard-link"
                target="_blank"
                rel="noopener noreferrer"
              >
                <LayoutDashboard size={18} />
                Dashboard
              </a>
            )}
          </div>

          {/* Sección autenticación desktop */}
          <div className="nav-auth desktop">
            {isAuthenticated ? (
              <div className="user-menu">
                <User className="user-icon" size={35 } />
                <span className="user-name">Hola, {user.username}</span>
                <button onClick={handleLogout} className="btn btn-primary">
                  Cerrar Sesión
                </button>
              </div>
            ) : (
              <Link to="/login" className="btn btn-primary">
                Iniciar Sesión
              </Link>
            )}
            <button
              className="theme-toggle"
              onClick={toggleTheme}
              aria-label="Cambiar tema"
              title={theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>

          {/* Botón de menú en dispositivo mobil */}
          <button
            className="mobile-menu-btn"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Navegación mobile */}
        {isOpen && (
          <div className="mobile-nav">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`mobile-nav-link ${isActive(item.path) ? "active" : ""}`}
                onClick={() => setIsOpen(false)}
              >
                {item.icon && <span className="nav-icon">{item.icon}</span>}
                {item.name}
              </Link>
            ))}
            {/* Link Dashboard solo para administradores - Mobile */}
            {isAdmin && (
              <a
                href={dashboardUrl}
                className="mobile-nav-link dashboard-link"
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => setIsOpen(false)}
              >
                <LayoutDashboard size={18} />
                Dashboard
              </a>
            )}
            <button
              className="theme-toggle mobile"
              onClick={() => { toggleTheme(); setIsOpen(false); }}
              aria-label="Cambiar tema"
              title={theme === 'dark' ? 'Modo claro' : 'Modo oscuro'}
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
              <span className="theme-toggle-text">{theme === 'dark' ? 'Claro' : 'Oscuro'}</span>
            </button>
            <div className="mobile-auth">
              {isAuthenticated ? (
                <>
                  <User className="user-icon" size={18} />
                  <span className="user-name">Hola {user.username}</span>
                  <button onClick={handleLogout} className="btn btn-primary">
                    Cerrar Sesión
                  </button>
                </>
              ) : (
                <Link
                  to="/login"
                  className="btn btn-primary"
                  onClick={() => setIsOpen(false)}
                >
                  Iniciar Sesión
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
