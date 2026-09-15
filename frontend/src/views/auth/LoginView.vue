<script setup>
import {
  AlertCircle,
  Eye,
  EyeOff,
  Lock,
  LogIn,
  Mail,
  ShieldCheck,
} from '@lucide/vue';
import useLogin from '@/composables/auth/useLogin';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseButton from '@/components/buttons/BaseButton.vue';

const {
  correo,
  password,
  showPassword,
  rememberMe,
  toggleShowPassword,
  loading,
  googleButtonElement,
  googleLoading,
  error,
  handleLogin,
} = useLogin();
</script>

<template>
  <div class="w-full bg-white border border-slate-200/90 shadow-xl shadow-slate-200/50 rounded-2xl p-6 sm:p-7 flex flex-col gap-4 sm:gap-5 transition-all duration-200">

    <!-- Encabezado del formulario de inicio de sesion -->
    <div class="flex flex-col items-center text-center select-none gap-1.5">
      <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-primary-50 border border-primary-200 text-[10px] font-semibold text-primary-700">
        <ShieldCheck :size="12" class="text-primary-600" />
        <span>Portal Institucional KairOs</span>
      </div>

      <h1 class="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
        Acceso a Laboratorios
      </h1>
      <p class="text-xs text-slate-500 max-w-xs leading-normal">
        Ingresa tus credenciales para administrar salas, estaciones y recursos tecnológicos.
      </p>
    </div>

    <!-- Formulario principal de credenciales -->
    <form @submit.prevent="handleLogin" class="flex flex-col gap-3.5">

      <!-- Campo de correo institucional -->
      <BaseInput
        id="correo"
        type="email"
        v-model="correo"
        appearance="light"
        label="Correo institucional"
        placeholder="usuario@institucion.edu"
        autocomplete="username"
      >
        <template #icon>
          <Mail :size="16" :stroke-width="1.8" />
        </template>
      </BaseInput>

      <!-- Campo de contrasena con alternancia de visibilidad -->
      <div class="flex flex-col gap-1.5">
        <BaseInput
          id="password"
          :type="showPassword ? 'text' : 'password'"
          v-model="password"
          appearance="light"
          label="Contraseña"
          placeholder="••••••••••••"
          autocomplete="current-password"
        >
          <template #icon>
            <Lock :size="16" :stroke-width="1.8" />
          </template>
          <template #action>
            <button
              type="button"
              @click="toggleShowPassword"
              class="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 focus:outline-none focus:text-primary-600 transition-colors cursor-pointer"
              :title="showPassword ? 'Ocultar contraseña' : 'Ver contraseña'"
              :aria-label="showPassword ? 'Ocultar contraseña' : 'Ver contraseña'"
            >
              <EyeOff v-if="showPassword" :size="16" />
              <Eye v-else :size="16" />
            </button>
          </template>
        </BaseInput>

        <!-- Fila de opciones: Recordar sesion y Recuperacion de contrasena -->
        <div class="flex items-center justify-between pt-0.5 select-none">
          <label class="flex items-center gap-1.5 cursor-pointer group">
            <input
              type="checkbox"
              v-model="rememberMe"
              class="size-3.5 rounded border-slate-300 bg-white text-primary-600 focus:ring-primary-500/20 focus:ring-2 accent-primary-600 cursor-pointer"
            />
            <span class="text-xs text-slate-600 group-hover:text-slate-900 transition-colors">Recordar sesión</span>
          </label>

          <router-link
            to="/auth/password-reset"
            class="text-xs font-semibold text-primary-600 hover:text-primary-700 transition-colors"
          >
            ¿Olvidaste tu contraseña?
          </router-link>
        </div>
      </div>

      <!-- Alerta visual de errores en login -->
      <Transition
        enter-from-class="opacity-0 -translate-y-1"
        enter-active-class="transition-all duration-200"
        leave-to-class="opacity-0"
        leave-active-class="transition-all duration-150"
      >
        <div
          v-if="error"
          role="alert"
          class="flex items-start gap-2 p-2.5 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 text-left"
        >
          <AlertCircle :size="14" class="shrink-0 mt-0.5 text-red-500" />
          <span class="leading-snug">{{ error }}</span>
        </div>
      </Transition>

      <!-- Boton de accion principal -->
      <BaseButton
        id="btn-iniciar"
        type="submit"
        :loading="loading"
        variant="accent"
        class="mt-0.5 font-semibold text-sm shadow-sm hover:shadow py-2.5 rounded-xl cursor-pointer"
      >
        <template #icon>
          <LogIn v-if="!loading" :size="16" />
        </template>
        Ingresar al Sistema
      </BaseButton>

    </form>

    <!-- Separador limpio -->
    <div class="flex items-center gap-3 select-none my-0.5">
      <div class="flex-1 h-px bg-slate-200" />
      <span class="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">o continuar con</span>
      <div class="flex-1 h-px bg-slate-200" />
    </div>

    <!-- Contenedor del boton oficial de Google Identity -->
    <div class="relative w-full min-h-[40px] flex items-center justify-center rounded-xl bg-white border border-slate-200 p-0.5 hover:bg-slate-50 transition-all duration-200 overflow-hidden shadow-2xs">
      <div
        v-if="googleLoading"
        class="absolute inset-0 flex items-center justify-center text-xs text-slate-500"
      >
        Cargando acceso institucional con Google...
      </div>
      <div ref="googleButtonElement" class="w-full flex justify-center" />
    </div>

    <!-- Pie de pagina de seguridad y soporte institucional -->
    <div class="flex items-center justify-between pt-2 border-t border-slate-100 text-[11px] text-slate-400 select-none">
      <span class="flex items-center gap-1.5 text-slate-500">
        <ShieldCheck :size="12" class="text-emerald-600" />
        <span>Cifrado TLS 1.3 activo</span>
      </span>
      <span>Mesa de Ayuda TI</span>
    </div>

  </div>
</template>
