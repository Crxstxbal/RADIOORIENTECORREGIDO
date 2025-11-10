// src/layouts/LayoutPrincipal.jsx
import React from "react";
import { Outlet, useLocation } from "react-router-dom";
import Navbar from "../components/Navbar";
import RadioPlayer from "../components/RadioPlayer";
import LiveChat from "../components/LiveChat";
import Footer from "../components/Footer";
import PublicidadCarousel from "../components/PublicidadCarousel";

export default function LayoutPrincipal() {
  const location = useLocation();
  const isHomePage = location.pathname === '/';

  return (
    <>
      <Navbar />
      
      {/* Panel izquierdo fijo 300x600 */}
      <PublicidadCarousel dimensiones="300x600" query="Izquierdo" position="left-fixed" autoPlayMs={7000} />
      {/* Panel derecho fijo 300x600 */}
      <PublicidadCarousel dimensiones="300x600" query="Derecho" position="right-fixed" autoPlayMs={7000} />
      <Outlet />
      <RadioPlayer />
      <LiveChat />
      <Footer />
    </>
  );
}
