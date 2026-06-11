<script setup>
import { onMounted } from 'vue';
import { User, Lock } from '@lucide/vue';
import useLogin from '@/composables/auth/useLogin';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseButton from '@/components/buttons/BaseButton.vue';

const { correo, password, loading, error, handleLogin, handleGoogleLogin } = useLogin();

onMounted(() => {
  /* global google */
  if (typeof google === 'undefined') return;

  google.accounts.id.initialize({
    client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
    callback: ({ credential }) => handleGoogleLogin(credential),
  });

  google.accounts.id.renderButton(
    document.getElementById('google-btn-div'),
    { theme: 'outline', size: 'large', width: '380', text: 'continue_with', shape: 'rectangular', logo_alignment: 'center' }
  );
});
</script>

<template>
  <div class="w-full flex flex-col gap-6">

    <div class="flex flex-col text-center select-none">
      <h1 class="text-3xl font-semibold text-white tracking-tight">
        Bienvenido de vuelta
      </h1>
      <p class="text-sm text-white/40">Ingresa tus credenciales para continuar</p>
    </div>

    <form @submit.prevent="handleLogin" class="flex flex-col gap-3.5">

      <BaseInput id="correo" type="email" v-model="correo" placeholder="Correo electrónico">
        <template #icon>
          <User :size="15" :stroke-width="1.75" />
        </template>
      </BaseInput>

      <div class="flex flex-col gap-1.5">
        <BaseInput id="password" type="password" v-model="password" placeholder="Contraseña">
          <template #icon>
            <Lock :size="15" :stroke-width="1.75" />
          </template>
        </BaseInput>

        <router-link
          to="/auth/password-reset"
          class="self-end text-xs text-white/35 hover:text-white/60 transition-colors duration-200"
        >
          ¿Olvidaste tu contraseña?
        </router-link>
      </div>

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

      <BaseButton id="btn-iniciar" type="submit" :loading="loading" variant="primary" class="mt-1">
        Iniciar sesión
      </BaseButton>

    </form>

    <div class="flex items-center gap-3">
      <div class="flex-1 h-px bg-white/10" />
      <span class="text-[11px] text-white/25 uppercase tracking-widest">o</span>
      <div class="flex-1 h-px bg-white/10" />
    </div>

    <!-- Envuelto para que el botón de Google encaje visualmente -->
    <div class="w-full overflow-hidden rounded-[10px] opacity-90 hover:opacity-100 transition-opacity duration-200">
      <div id="google-btn-div" class="w-full flex justify-center" />
    </div>

  </div>
</template>