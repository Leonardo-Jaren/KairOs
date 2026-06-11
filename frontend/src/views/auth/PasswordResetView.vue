<script setup>
import { onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { User, Lock, Key } from '@lucide/vue';
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
  <div class="w-full flex flex-col gap-6">
    
    <!-- Encabezado de la vista adaptado al flujo actual -->
    <div class="flex flex-col gap-1 text-center select-none">
      <h1 class="text-xl font-semibold text-white tracking-tight">
        {{ token ? 'Establecer contraseña' : 'Recuperar contraseña' }}
      </h1>
      <p class="text-sm text-white/40">
        {{ token ? 'Ingresa el código y tu nueva contraseña' : 'Ingresa tu correo para recibir un código' }}
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
        placeholder="Código de verificación"
      >
        <template #icon>
          <Key :size="15" :stroke-width="1.75" />
        </template>
      </BaseInput>

      <!-- Nueva Contrasena -->
      <BaseInput
        id="reset-password"
        type="password"
        v-model="password"
        placeholder="Nueva contraseña"
      >
        <template #icon>
          <Lock :size="15" :stroke-width="1.75" />
        </template>
      </BaseInput>

      <!-- Confirmar Nueva Contrasena -->
      <BaseInput
        id="reset-confirm-password"
        type="password"
        v-model="confirmPassword"
        placeholder="Confirmar contraseña"
      >
        <template #icon>
          <Lock :size="15" :stroke-width="1.75" />
        </template>
      </BaseInput>

      <!-- Alertas de exito o error -->
      <Transition
        enter-from-class="opacity-0 -translate-y-1"
        enter-active-class="transition-all duration-200"
        leave-to-class="opacity-0"
        leave-active-class="transition-all duration-150"
      >
        <p v-if="error" class="text-xs text-red-300 bg-red-500/10 border border-red-500/20 rounded-lg px-3.5 py-2.5 text-center">
          {{ error }}
        </p>
      </Transition>

      <Transition
        enter-from-class="opacity-0 -translate-y-1"
        enter-active-class="transition-all duration-200"
        leave-to-class="opacity-0"
        leave-active-class="transition-all duration-150"
      >
        <p v-if="success" class="text-xs text-emerald-300 bg-emerald-500/10 border border-emerald-500/20 rounded-lg px-3.5 py-2.5 text-center">
          {{ successMessage }}
        </p>
      </Transition>

      <!-- Botones de accion -->
      <div class="flex flex-col gap-3 mt-1">
        <BaseButton
          id="btn-confirm-reset"
          type="submit"
          :loading="loading"
          variant="primary"
        >
          Restablecer contraseña
        </BaseButton>

        <router-link
          to="/auth/login"
          class="text-center text-xs text-white/35 hover:text-white/60 transition-colors duration-200"
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
        placeholder="Correo electrónico"
      >
        <template #icon>
          <User :size="15" :stroke-width="1.75" />
        </template>
      </BaseInput>

      <!-- Alertas de exito o error -->
      <Transition
        enter-from-class="opacity-0 -translate-y-1"
        enter-active-class="transition-all duration-200"
        leave-to-class="opacity-0"
        leave-active-class="transition-all duration-150"
      >
        <p v-if="error" class="text-xs text-red-300 bg-red-500/10 border border-red-500/20 rounded-lg px-3.5 py-2.5 text-center">
          {{ error }}
        </p>
      </Transition>

      <Transition
        enter-from-class="opacity-0 -translate-y-1"
        enter-active-class="transition-all duration-200"
        leave-to-class="opacity-0"
        leave-active-class="transition-all duration-150"
      >
        <p v-if="success" class="text-xs text-emerald-300 bg-emerald-500/10 border border-emerald-500/20 rounded-lg px-3.5 py-2.5 text-center">
          {{ successMessage }}
        </p>
      </Transition>

      <!-- Botones de accion -->
      <div class="flex flex-col gap-3 mt-1">
        <BaseButton
          id="btn-request-reset"
          type="submit"
          :loading="loading"
          variant="primary"
        >
          Solicitar código
        </BaseButton>

        <router-link
          to="/auth/login"
          class="text-center text-xs text-white/35 hover:text-white/60 transition-colors duration-200"
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
