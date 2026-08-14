<script setup>
import {
  CalendarDays,
  ChevronRight,
  CircleUserRound,
  Cpu,
  HardDrive,
  MapPin,
  ShieldAlert,
  Wrench,
  X,
} from '@lucide/vue';

import BaseButton from '@/components/buttons/BaseButton.vue';

defineProps({
  equipment: { type: Object, default: null },
});

defineEmits(['close', 'report']);

const statusClasses = {
  en_uso: 'bg-success-50 text-success-700',
  en_mantenimiento: 'bg-warning-50 text-warning-700',
  dañado: 'bg-danger-50 text-danger-700',
  de_baja: 'bg-slate-100 text-slate-600',
};
</script>

<template>
  <Teleport to="body">
    <Transition enter-active-class="transition-opacity duration-200" enter-from-class="opacity-0" leave-active-class="transition-opacity duration-150" leave-to-class="opacity-0">
      <div v-if="equipment" class="fixed inset-0 z-50 bg-slate-950/35 backdrop-blur-[2px]" @click.self="$emit('close')">
        <Transition appear enter-active-class="transition-transform duration-300 ease-out" enter-from-class="translate-x-full">
          <aside class="ml-auto flex h-full w-full max-w-md flex-col bg-white shadow-2xl">
            <header class="border-b border-slate-100 px-6 py-5">
              <div class="flex items-start justify-between gap-4">
                <div>
                  <p class="text-[10px] font-extrabold uppercase tracking-[0.2em] text-primary-600">Ficha del equipo</p>
                  <h2 class="mt-1 font-mono text-2xl font-extrabold text-slate-950">{{ equipment.codigo }}</h2>
                  <span class="mt-2 inline-flex rounded-full px-2.5 py-1 text-xs font-bold" :class="statusClasses[equipment.estado]">
                    {{ equipment.estado_display }}
                  </span>
                </div>
                <button type="button" class="rounded-xl p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700" aria-label="Cerrar detalle" @click="$emit('close')">
                  <X :size="20" />
                </button>
              </div>
            </header>

            <div class="flex-1 overflow-y-auto px-6 py-6">
              <section class="rounded-2xl bg-secondary-950 p-5 text-white">
                <div class="flex items-center gap-4">
                  <span class="grid size-12 place-items-center rounded-xl bg-primary-500/20 text-primary-300">
                    <Cpu :size="25" />
                  </span>
                  <div>
                    <p class="text-xs font-semibold text-white/45">{{ equipment.tipo_equipo_display }}</p>
                    <p class="text-lg font-bold">{{ equipment.marca }} {{ equipment.modelo }}</p>
                  </div>
                </div>
              </section>

              <dl class="mt-6 grid grid-cols-2 gap-3">
                <div class="rounded-xl border border-slate-200 p-3">
                  <dt class="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide text-slate-400"><HardDrive :size="13" /> Serie</dt>
                  <dd class="mt-1.5 truncate font-mono text-xs font-semibold text-slate-700">{{ equipment.numero_serie }}</dd>
                </div>
                <div class="rounded-xl border border-slate-200 p-3">
                  <dt class="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide text-slate-400"><MapPin :size="13" /> MAC</dt>
                  <dd class="mt-1.5 truncate font-mono text-xs font-semibold text-slate-700">{{ equipment.numero_mac || 'Sin registrar' }}</dd>
                </div>
                <div class="rounded-xl border border-slate-200 p-3">
                  <dt class="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide text-slate-400"><CircleUserRound :size="13" /> Responsable</dt>
                  <dd class="mt-1.5 truncate text-xs font-semibold text-slate-700">{{ equipment.responsable_usuario || 'Sin asignar' }}</dd>
                </div>
                <div class="rounded-xl border border-slate-200 p-3">
                  <dt class="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide text-slate-400"><CalendarDays :size="13" /> Adquisición</dt>
                  <dd class="mt-1.5 text-xs font-semibold text-slate-700">{{ equipment.fecha_adquisicion }}</dd>
                </div>
              </dl>

              <section class="mt-6 rounded-2xl border border-warning-200 bg-warning-50/60 p-4">
                <div class="flex gap-3">
                  <ShieldAlert :size="21" class="mt-0.5 shrink-0 text-warning-600" />
                  <div>
                    <p class="text-sm font-bold text-slate-900">¿Este equipo presenta una falla?</p>
                    <p class="mt-1 text-xs leading-5 text-slate-500">Registra el problema y decide si queda pendiente o ingresa directamente a mantenimiento.</p>
                  </div>
                </div>
                <BaseButton class="mt-4" variant="accent" @click="$emit('report')">
                  <template #icon><Wrench :size="17" /></template>
                  Registrar falla
                </BaseButton>
              </section>

              <RouterLink :to="{ path: '/mantenimiento', query: { equipo_id: equipment.id } }" class="mt-4 flex items-center justify-between rounded-xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-600 hover:border-primary-200 hover:bg-primary-50 hover:text-primary-700">
                Abrir módulo de mantenimiento
                <ChevronRight :size="17" />
              </RouterLink>
            </div>
          </aside>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>
