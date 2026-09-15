<script setup>
import { onMounted } from 'vue';
import { useRoute } from 'vue-router';
import {
  AlertCircle,
  CheckCircle2,
  Key,
  Lock,
  Mail,
} from '@lucide/vue';
import usePasswordReset from '@/composables/auth/usePasswordReset';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseButton from '@/components/buttons/BaseButton.vue';

const route = useRoute();

// Extraer estados y funciones desde el composable
const {
  correo,
  token,
  password,
  confirmPassword,
  loading,
  error,
  success,
  successMessage,
  handleRequestReset,
  handleConfirmReset,
} = usePasswordReset();

// Capturar automaticamente el token de la URL si se proporciona
onMounted(() => {
  if (route.query.token) {
    token.value = route.query.token;
  }
});
</script>

<template>
  <div class="w-full bg-white border border-slate-200/90 shadow-xl shadow-slate-200/50 rounded-2xl p-6 sm:p-7 flex flex-col gap-4 sm:gap-5 transition-all duration-200">
    
    <!-- Encabezado de la vista adaptado al flujo actual -->
    <div class="flex flex-col gap-1.5 text-center select-none">
      <h1 class="text-2xl font-bold text-slate-900 tracking-tight">
        {{ token ? 'Establecer contraseña' : 'Recuperar contraseña' }}
      </h1>
      <p class="text-xs sm:text-sm text-slate-500">
        {{ token ? 'Ingresa el código y tu nueva contraseña' : 'Ingresa tu correo institucional para recibir un código' }}
      </p>
    </div>

    <!-- 1. Formulario de confirmacion de cambio de contrasena (si existe un token) -->
    <form 
      v-if="token" 
      @submit.prevent="handleConfirmReset" 
      class="flex flex-col gap-4"
    >
      <!-- Campo de Token -->
      <BaseInput
        id="reset-token"
        type="text"
        v-model="token"
        appearance="light"
        label="Código de verificación"
        placeholder="Ej. 123456"
      >
        <template #icon>
          <Key :size="16" :stroke-width="1.8" />
        </template>
      </BaseInput>

      <!-- Nueva Contrasena -->
      <BaseInput
        id="reset-password"
        type="password"
        v-model="password"
        appearance="light"
        label="Nueva contraseña"
        placeholder="••••••••••••"
      >
        <template #icon>
          <Lock :size="16" :stroke-width="1.8" />
        </template>
      </BaseInput>

      <!-- Confirmar Nueva Contrasena -->
      <BaseInput
        id="reset-confirm-password"
        type="password"
        v-model="confirmPassword"
        appearance="light"
        label="Confirmar contraseña"
        placeholder="••••••••••••"
      >
        <template #icon>
          <Lock :size="16" :stroke-width="1.8" />
        </template>
      </BaseInput>

      <!-- Alertas de exito o error -->
      <Transition
        enter-from-class="opacity-0 -translate-y-1"
        enter-active-class="transition-all duration-200"
        leave-to-class="opacity-0"
        leave-active-class="transition-all duration-150"
      >
        <div
          v-if="error"
          role="alert"
          class="flex items-start gap-2.5 p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 text-left"
        >
          <AlertCircle :size="15" class="shrink-0 mt-0.5 text-red-500" />
          <span class="leading-snug">{{ error }}</span>
        </div>
      </Transition>

      <Transition
        enter-from-class="opacity-0 -translate-y-1"
        enter-active-class="transition-all duration-200"
        leave-to-class="opacity-0"
        leave-active-class="transition-all duration-150"
      >
        <div
          v-if="success"
          role="status"
          class="flex items-start gap-2.5 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-700 text-left"
        >
          <CheckCircle2 :size="15" class="shrink-0 mt-0.5 text-emerald-500" />
          <span class="leading-snug">{{ successMessage }}</span>
        </div>
      </Transition>

      <!-- Botones de accion -->
      <div class="flex flex-col gap-3 mt-1">
        <BaseButton
          id="btn-confirm-reset"
          type="submit"
          :loading="loading"
          variant="accent"
          class="font-semibold shadow-sm hover:shadow py-2.5 rounded-xl cursor-pointer"
        >
          Restablecer contraseña
        </BaseButton>

        <router-link
          to="/auth/login"
          class="text-center text-xs font-semibold text-primary-600 hover:text-primary-700 transition-colors"
        >
          Volver al inicio de sesión
        </router-link>
      </div>
    </form>

    <!-- 2. Formulario de solicitud inicial de restablecimiento (si NO hay token) -->
    <form 
      v-else 
      @submit.prevent="handleRequestReset" 
      class="flex flex-col gap-4"
    >
      <!-- Campo de Correo Electronico -->
      <BaseInput
        id="reset-correo"
        type="email"
        v-model="correo"
        appearance="light"
        label="Correo institucional"
        placeholder="usuario@institucion.edu"
      >
        <template #icon>
          <Mail :size="16" :stroke-width="1.8" />
        </template>
      </BaseInput>

      <!-- Alertas de exito o error -->
      <Transition
        enter-from-class="opacity-0 -translate-y-1"
        enter-active-class="transition-all duration-200"
        leave-to-class="opacity-0"
        leave-active-class="transition-all duration-150"
      >
        <div
          v-if="error"
          role="alert"
          class="flex items-start gap-2.5 p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 text-left"
        >
          <AlertCircle :size="15" class="shrink-0 mt-0.5 text-red-500" />
          <span class="leading-snug">{{ error }}</span>
        </div>
      </Transition>

      <Transition
        enter-from-class="opacity-0 -translate-y-1"
        enter-active-class="transition-all duration-200"
        leave-to-class="opacity-0"
        leave-active-class="transition-all duration-150"
      >
        <div
          v-if="success"
          role="status"
          class="flex items-start gap-2.5 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-700 text-left"
        >
          <CheckCircle2 :size="15" class="shrink-0 mt-0.5 text-emerald-500" />
          <span class="leading-snug">{{ successMessage }}</span>
        </div>
      </Transition>

      <!-- Botones de accion -->
      <div class="flex flex-col gap-3 mt-1">
        <BaseButton
          id="btn-request-reset"
          type="submit"
          :loading="loading"
          variant="accent"
          class="font-semibold shadow-sm hover:shadow py-2.5 rounded-xl cursor-pointer"
        >
          Solicitar código
        </BaseButton>

        <router-link
          to="/auth/login"
          class="text-center text-xs font-semibold text-primary-600 hover:text-primary-700 transition-colors"
        >
          Volver al inicio de sesión
        </router-link>
      </div>
    </form>
  </div>
</template>

<style scoped>
/* Los estilos se resuelven completamente con clases de Tailwind CSS */
</style>
