<template>
  <BaseModal
    :open="open"
    title="Matriz de Permisos Granulares (CRUD)"
    description="Configura los accesos específicos por módulo para esta cuenta o restablece a los predeterminados de su rol."
    size="lg"
    @close="$emit('close')"
  >
    <div v-if="loading" class="flex flex-col items-center justify-center py-12">
      <div class="size-8 animate-spin rounded-full border-3 border-primary-200 border-t-primary-600" />
      <p class="mt-3 text-xs font-semibold text-slate-600">Cargando matriz de permisos...</p>
    </div>

    <div v-else class="space-y-6">
      <!-- Tarjeta informativa del usuario y rol -->
      <div class="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-slate-50/70 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex items-center gap-3">
          <div class="grid size-10 place-items-center rounded-xl bg-primary-100 font-bold text-sm text-primary-700">
            {{ (usuarioNombre || 'U').charAt(0) }}
          </div>
          <div>
            <h3 class="text-sm font-bold text-slate-900">{{ usuarioNombre }}</h3>
            <div class="flex items-center gap-2 mt-0.5">
              <span class="inline-flex rounded-full bg-slate-200 px-2 py-0.5 text-[11px] font-semibold text-slate-700">
                Rol base: {{ roleLabels[usuarioRol] || usuarioRol }}
              </span>
            </div>
          </div>
        </div>

        <div v-if="totalPersonalizados > 0" class="flex items-center gap-2 rounded-xl bg-amber-50 border border-amber-200/80 px-3 py-1.5 text-xs text-amber-800">
          <AlertCircle :size="15" class="text-amber-600 shrink-0" />
          <span><strong>{{ totalPersonalizados }}</strong> {{ totalPersonalizados === 1 ? 'permiso personalizado' : 'permisos personalizados' }}</span>
        </div>
        <div v-else class="text-xs text-slate-500 font-medium">
          Usando plantilla estándar del rol
        </div>
      </div>

      <!-- Tabla de Matriz de Permisos -->
      <div class="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-slate-200 bg-slate-50/80 text-[11px] font-bold uppercase tracking-wider text-slate-500">
              <th class="py-3 px-4">Módulo del Sistema</th>
              <th v-for="accion in acciones" :key="accion" class="py-3 px-4 text-center w-24">
                {{ accion.toUpperCase() }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-xs">
            <tr
              v-for="mod in modulos"
              :key="mod"
              class="hover:bg-slate-50/60 transition-colors"
            >
              <td class="py-3.5 px-4">
                <div class="flex items-center gap-3">
                  <div class="grid size-9 place-items-center rounded-xl bg-slate-100 text-slate-600 border border-slate-200/80 shrink-0">
                    <component :is="modulosIconos[mod]" :size="18" :stroke-width="1.8" />
                  </div>
                  <div class="min-w-0">
                    <p class="font-bold text-slate-900">{{ modulosEtiquetas[mod] || mod }}</p>
                    <p class="text-[11px] text-slate-400 mt-0.5">{{ modulosDescripciones[mod] }}</p>
                  </div>
                </div>
              </td>

              <td
                v-for="acc in acciones"
                :key="acc"
                class="py-3.5 px-4 text-center"
              >
                <div class="flex flex-col items-center justify-center gap-1">
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      :checked="permisosEfectivos[mod]?.[acc]"
                      class="peer sr-only"
                      @change="togglePermiso(mod, acc)"
                    />
                    <div
                      class="size-5 rounded-md border-2 border-slate-300 bg-white peer-checked:border-primary-600 peer-checked:bg-primary-600 flex items-center justify-center transition-all peer-focus-visible:ring-2 peer-focus-visible:ring-primary-400"
                    >
                      <Check
                        v-if="permisosEfectivos[mod]?.[acc]"
                        :size="13"
                        class="text-white stroke-[3]"
                      />
                    </div>
                  </label>

                  <!-- Indicador de cambio frente a la plantilla base -->
                  <span
                    v-if="isCustomized(mod, acc)"
                    class="text-[9px] font-bold text-amber-600 tracking-tight uppercase"
                    title="Permiso modificado respecto a la plantilla original del rol"
                  >
                    Custom
                  </span>

                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Leyenda aclaratoria -->
      <div class="flex flex-wrap items-center justify-between gap-4 text-xs text-slate-500 bg-slate-50/60 p-3 rounded-xl border border-slate-200/60">
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5">
            <div class="size-3.5 rounded-sm bg-primary-600" />
            <span>Permitido</span>
          </div>
          <div class="flex items-center gap-1.5">
            <div class="size-3.5 rounded-sm border-2 border-slate-300 bg-white" />
            <span>Denegado</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-[10px] font-bold text-amber-600 uppercase">Custom</span>
            <span>Modificado del estándar</span>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex w-full items-center justify-between">
        <BaseButton
          variant="ghost"
          :disabled="saving || loading || totalPersonalizados === 0"
          :full-width="false"
          @click="ejecutarRestablecer"
        >
          <template #icon>
            <RotateCcw :size="15" />
          </template>
          Restablecer a plantilla del rol
        </BaseButton>

        <div class="flex items-center gap-2">
          <BaseButton
            variant="ghost"
            :disabled="saving"
            :full-width="false"
            @click="$emit('close')"
          >
            Cancelar
          </BaseButton>

          <BaseButton
            variant="accent"
            :loading="saving"
            :disabled="loading"
            :full-width="false"
            @click="ejecutarGuardar"
          >
            Guardar permisos
          </BaseButton>
        </div>
      </div>
    </template>
  </BaseModal>
</template>

<script setup>
import { watch } from 'vue';
import {
  AlertCircle,
  AppWindow,
  Building2,
  Check,
  Clock3,
  MonitorCog,
  RotateCcw,
  ShieldAlert,
  UsersRound,
  Wrench,
} from '@lucide/vue';

import BaseButton from '@/components/buttons/BaseButton.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import { usePermisos } from '@/composables/usuarios/usePermisos';

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  user: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['close', 'saved']);

const {
  loading,
  saving,
  usuarioNombre,
  usuarioRol,
  modulos,
  modulosEtiquetas,
  modulosDescripciones,
  acciones,
  permisosBase,
  permisosEfectivos,
  totalPersonalizados,
  cargarPermisos,
  togglePermiso,
  isCustomized,
  guardar,
  restablecer,
} = usePermisos();

const modulosIconos = {
  espacios: Building2,
  equipos: MonitorCog,
  mantenimiento: Wrench,
  incidencias: ShieldAlert,
  software: AppWindow,
  usuarios: UsersRound,
  auditoria: Clock3,
};

watch(
  () => [props.open, props.user],
  ([isOpen, targetUser]) => {
    if (isOpen && targetUser?.id) {
      cargarPermisos(targetUser.id);
    }
  },
  { immediate: true },
);

const notificarCambioPermisos = () => {
  if (typeof BroadcastChannel !== 'undefined') {
    try {
      const channel = new BroadcastChannel('kairos_permisos_channel');
      channel.postMessage({ type: 'PERMISOS_ACTUALIZADOS', userId: props.user?.id });
      channel.close();
    } catch {
      // Ignorar si el entorno no cuenta con soporte
    }
  }
};

const ejecutarGuardar = async () => {
  const exito = await guardar();
  if (exito) {
    notificarCambioPermisos();
    emit('saved');
    emit('close');
  }
};

const ejecutarRestablecer = async () => {
  const exito = await restablecer();
  if (exito) {
    notificarCambioPermisos();
    emit('saved');
  }
};

const roleLabels = {
  superadmin: 'Superadministrador',
  admin: 'Administrador',
  responsable: 'Responsable',
  tecnico: 'Técnico',
  docente: 'Docente',
  usuario: 'Usuario',
};
</script>
