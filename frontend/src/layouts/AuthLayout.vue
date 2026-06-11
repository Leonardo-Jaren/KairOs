<template>
  <div class="relative min-h-screen w-full flex items-center justify-center bg-kairos-blue overflow-hidden p-6">
    
    <!-- Contenedor del fondo estetico (curvas y circulos) -->
    <div class="absolute inset-0 w-full h-full pointer-events-none select-none z-0">
      
      <!-- Circulos concentricos en el lateral izquierdo (fiel al diseno de Figma) -->
      <div class="absolute left-0 top-0 bottom-0 flex items-center justify-start">
        <svg 
          class="w-[280px] h-[560px] md:w-[450px] md:h-[900px] -translate-x-[45%] text-kairos-navy-light/95 transition-all duration-300"
          viewBox="0 0 300 600" 
          fill="none" 
          xmlns="http://www.w3.org/2000/svg"
        >
          <!-- Circulo exterior en tono medio -->
          <circle 
            cx="50" 
            cy="300" 
            r="230" 
            stroke="currentColor" 
            stroke-width="48" 
          />
          <!-- Circulo intermedio en tono oscuro -->
          <circle 
            cx="50" 
            cy="300" 
            r="160" 
            stroke="#1c2b3e" 
            stroke-width="40" 
          />
          <!-- Circulo central en color azul brillante -->
          <circle 
            cx="50" 
            cy="300" 
            r="90" 
            fill="#488dfe" 
          />
        </svg>
      </div>

      <!-- Curva abstracta ondulada en el lado derecho (fiel al diseno de Figma) -->
      <div class="absolute right-0 top-0 bottom-0 w-full h-full flex justify-end">
        <svg 
          class="h-full w-full md:w-[60%] lg:w-[45%] xl:w-[40%] text-kairos-navy transition-all duration-300"
          viewBox="0 0 400 800" 
          preserveAspectRatio="none" 
          fill="currentColor"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path 
            d="M 400 0 L 150 0 C 230 180, 50 380, 200 580 C 280 680, 120 750, 150 800 L 400 800 Z" 
          />
        </svg>
      </div>

    </div>

    <!-- Contenedor del formulario central flotante con router-view -->
    <div class="relative w-full max-w-[380px] z-10 bg-transparent flex flex-col items-center">
      <router-view />
    </div>
    
  </div>
</template>

<style scoped>
/* Los estilos se resuelven completamente con clases de Tailwind CSS */
</style>
