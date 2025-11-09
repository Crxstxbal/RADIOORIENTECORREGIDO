// src/layouts/LayoutPrincipal.jsx
import React from "react";
import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";
import RadioPlayer from "../components/RadioPlayer";
import LiveChat from "../components/LiveChat";
import Footer from "../components/Footer";
import PublicidadCarousel from "../components/PublicidadCarousel";

export default function LayoutPrincipal() {
  return (
    <>
      <Navbar />
      {/* Banner superior 1200x200 */}
      <PublicidadCarousel dimensiones="1200x200" query="Superior" position="top" autoPlayMs={6000} />

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
