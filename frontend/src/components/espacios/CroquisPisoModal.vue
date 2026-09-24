<script setup>
import { ExternalLink, Layers, X } from '@lucide/vue';
import BaseButton from '@/components/buttons/BaseButton.vue';
import CroquisPiso from '@/components/espacios/CroquisPiso.vue';

defineProps({
  open: { type: Boolean, default: false },
  floor: { type: Object, default: () => null },
  canEdit: { type: Boolean, default: false },
});

const emit = defineEmits(['close', 'assign-technician', 'create-space', 'edit-space', 'delete-space']);
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      leave-active-class="transition duration-150 ease-in"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open && floor"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-2.5 backdrop-blur-sm sm:p-4"
        role="dialog"
        aria-modal="true"
        aria-label="Croquis 2D del piso"
        @keydown.esc="emit('close')"
        @click.self="emit('close')"
      >
        <section
          class="flex max-h-[min(900px,calc(100dvh-2rem))] w-full max-w-5xl flex-col overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-2xl"
        >
          <!-- Cabecera del modal de croquis -->
          <header class="flex shrink-0 items-center justify-between border-b border-slate-100 px-5 py-4">
            <div class="flex items-center gap-3">
              <span class="grid size-10 place-items-center rounded-xl bg-primary-50 text-primary-600">
                <Layers :size="20" />
              </span>
              <div>
                <h2 class="text-base font-bold text-slate-900 sm:text-lg">
                  Croquis 2D · {{ floor.label }}
                </h2>
                <p class="text-xs text-slate-500">
                  {{ floor.edificio_nombre }} · Distribución arquitectónica de ambientes y pasillos.
                </p>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <RouterLink
                :to="{
                  path: '/espacios/mapa',
                  query: { pabellon: floor.edificio_id, piso: floor.piso }
                }"
                class="hidden sm:inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-xs hover:border-primary-300 hover:text-primary-600 transition"
              >
                <ExternalLink :size="14" />
                Abrir editor en Mapa
              </RouterLink>
              <button
                type="button"
                class="grid size-9 place-items-center rounded-xl text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition"
                aria-label="Cerrar croquis"
                @click="emit('close')"
              >
                <X :size="18" />
              </button>
            </div>
          </header>

          <!-- Cuerpo: Componente CroquisPiso 2D -->
          <div class="dock-scrollbar flex-1 overflow-y-auto p-4 sm:p-6 bg-slate-50/50">
            <CroquisPiso
              :floor="floor"
              :can-edit="false"
              @assign-technician="emit('assign-technician', $event)"
              @create-space="emit('create-space', $event)"
              @edit-space="emit('edit-space', $event)"
              @delete-space="emit('delete-space', $event)"
            />
          </div>

          <!-- Pie del modal -->
          <footer class="flex shrink-0 items-center justify-between border-t border-slate-100 bg-slate-50/80 px-5 py-3">
            <span class="text-xs text-slate-500">
              {{ floor.spaces.length }} {{ floor.spaces.length === 1 ? 'ambiente ubicado' : 'ambientes ubicados' }} en este piso.
            </span>
            <BaseButton
              variant="ghost"
              size="sm"
              :full-width="false"
              @click="emit('close')"
            >
              Cerrar
            </BaseButton>
          </footer>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>
