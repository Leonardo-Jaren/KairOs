<template>
  <div class="flex min-w-0 flex-col gap-4 sm:gap-6">
    <header class="flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
      <div>
        <div class="flex items-center gap-3 mb-1">
          <p class="text-xs font-bold uppercase tracking-[0.2em] text-primary-600">Administración</p>
          <span class="text-slate-300">·</span>
          <!-- Selector de Modo de Visualización (Pestañas) -->
          <div class="inline-flex rounded-xl bg-slate-200/70 p-1 text-xs">
            <button
              type="button"
              class="flex items-center gap-1.5 rounded-lg px-3 py-1 font-bold transition-all"
              :class="viewMode === 'tabla' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'"
              @click="viewMode = 'tabla'"
            >
              <Table :size="14" />
              <span>Lista</span>
            </button>
            <button
              type="button"
              class="flex items-center gap-1.5 rounded-lg px-3 py-1 font-bold transition-all"
              :class="viewMode === 'organigrama' ? 'bg-white text-primary-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'"
              @click="switchToOrganigrama"
            >
              <Network :size="14" />
              <span>Organigrama</span>
            </button>
          </div>
        </div>

        <h1 class="text-2xl font-extrabold tracking-tight text-slate-950 sm:text-3xl">
          {{ viewMode === 'organigrama' ? 'Organigrama Jerárquico' : 'Usuarios' }}
        </h1>
        <p class="mt-1.5 max-w-2xl text-sm text-slate-500">
          {{ viewMode === 'organigrama'
            ? 'Estructura visual de subordinación, responsabilidades por sede y supervisores directos.'
            : 'Gestiona accesos, roles institucionales, jerarquías y matriz de permisos.' }}
        </p>
      </div>

      <div class="flex items-center gap-3">
        <BaseButton v-if="canCreate" variant="accent" :full-width="false" @click="openCreate">
          <template #icon>
            <Plus :size="18" />
          </template>
          Nuevo usuario
        </BaseButton>
      </div>
    </header>

    <!-- Indicadores de métricas temporalmente ocultos para priorizar el área de gestión.
    <section class="grid grid-cols-2 gap-2 sm:gap-4 xl:grid-cols-4">
      <StatCard label="Usuarios registrados" :value="stats.total" tone="blue">
        <template #icon>
          <UsersRound :size="20" />
        </template>
      </StatCard>
      <StatCard label="Cuentas activas" :value="stats.activos" tone="emerald">
        <template #icon>
          <UserCheck :size="20" />
        </template>
      </StatCard>
      <StatCard label="Administradores y Globales" :value="stats.administradores" tone="violet">
        <template #icon>
          <ShieldCheck :size="20" />
        </template>
      </StatCard>
      <StatCard label="Técnicos y docentes" :value="stats.tecnicos + stats.docentes" tone="amber">
        <template #icon>
          <Wrench :size="20" />
        </template>
      </StatCard>
    </section>
    -->

    <!-- Barra de Filtros -->
    <section class="rounded-2xl border border-slate-200 bg-white p-3 shadow-sm sm:p-4">
      <form
        class="grid gap-3"
        :class="viewMode === 'tabla' ? 'md:grid-cols-2 xl:grid-cols-[minmax(220px,1.4fr)_minmax(170px,0.7fr)_minmax(220px,1fr)_minmax(160px,0.65fr)_auto]' : 'md:grid-cols-[minmax(200px,1fr)_auto]'"
        @submit.prevent="onFilterSubmit"
      >
        <template v-if="viewMode === 'tabla'">
          <BaseInput
            id="users-search"
            v-model="filters.search"
            appearance="light"
            placeholder="Buscar por nombre, correo, usuario o DNI"
          >
            <template #icon>
              <Search :size="17" />
            </template>
          </BaseInput>

          <BaseSelect
            id="users-role"
            v-model="filters.rol"
            :options="filterRoleOptions"
            placeholder="Todos los roles"
          />

          <BaseSelect
            id="users-sede"
            v-model="filters.local_id"
            :options="[{ value: '', label: 'Todas las sedes' }, ...sedeOptions]"
            placeholder="Todas las sedes"
          />

          <BaseSelect
            id="users-status"
            v-model="filters.activo"
            :options="[
              { value: 'true', label: 'Activos' },
              { value: 'false', label: 'Inactivos' },
            ]"
            placeholder="Todos los estados"
          />

          <BaseButton variant="ghost" :full-width="false" @click="clearFilters">Limpiar</BaseButton>
        </template>

        <template v-else>
          <!-- Filtro exclusivo para Organigrama: Selector de Sede -->
          <div class="flex min-w-0 flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
            <label for="org-sede-select" class="whitespace-nowrap text-xs font-bold text-slate-600">
              Filtrar por sede:
            </label>
            <div class="min-w-0 w-full sm:w-72">
              <BaseSelect
                id="org-sede-select"
                v-model="organigrama.selectedLocalId.value"
                :options="[{ value: '', label: 'Visión Global (Todas las sedes)' }, ...sedeOptions]"
                placeholder="Seleccionar sede física"
                @update:model-value="onOrganigramaSedeChange"
              />
            </div>
          </div>

          <div class="flex justify-end">
            <BaseButton class="sm:w-auto!" variant="ghost" :full-width="true" @click="organigrama.loadOrganigrama">
              <template #icon>
                <RefreshCw :size="15" />
              </template>
              Recargar árbol
            </BaseButton>
          </div>
        </template>
      </form>
    </section>

    <!-- Vista 1: Tabla de Usuarios -->
    <template v-if="viewMode === 'tabla'">
      <div class="hidden sm:block">
        <BaseTable
          :columns="columns"
          :items="usuarios"
          :loading="loading"
          empty-message="No se encontraron usuarios con los filtros actuales."
        >
        <template #cell-usuario="{ item }">
          <div class="flex items-center gap-3">
            <div class="grid size-10 shrink-0 place-items-center rounded-xl font-bold text-sm"
              :class="avatarClasses[item.rol] || 'bg-slate-100 text-slate-700'">
              {{ item.nombre?.charAt(0) }}{{ item.apellido?.charAt(0) }}
            </div>
            <div>
              <p class="font-semibold text-slate-900">{{ item.nombre_completo }}</p>
              <p class="text-xs text-slate-500">{{ item.correo }} · @{{ item.username }}</p>
            </div>
          </div>
        </template>

        <template #cell-dni="{ item }">
          <span class="font-mono text-xs text-slate-600">{{ item.dni || '—' }}</span>
        </template>

        <template #cell-rol="{ item }">
          <span
            class="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset"
            :class="roleClasses[item.rol] || 'bg-slate-100 text-slate-700 ring-slate-400/20'"
          >
            {{ roleLabels[item.rol] ?? item.rol }}
          </span>
        </template>

        <template #cell-supervisor="{ item }">
          <span v-if="item.supervisor" class="text-xs font-medium text-slate-700">
            {{ item.supervisor.nombre_completo }}
          </span>
          <span v-else class="text-xs text-slate-400 italic">Ninguno</span>
        </template>

        <template #cell-estado="{ item }">
          <span
            class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
            :class="item.is_active ? 'bg-success-50 text-success-700' : 'bg-slate-100 text-slate-500'"
          >
            <span class="size-1.5 rounded-full" :class="item.is_active ? 'bg-success-500' : 'bg-slate-400'" />
            {{ item.is_active ? 'Activo' : 'Inactivo' }}
          </span>
        </template>

        <template #cell-acciones="{ item }">
          <div class="flex justify-end gap-1">
            <button
              type="button"
              class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
              title="Ver ficha de usuario"
              aria-label="Ver detalle"
              @click="detailUsuario = item"
            >
              <Eye :size="17" />
            </button>

            <!-- Botón para gestionar permisos granulares CRUD -->
            <button
              v-if="canManagePermisos(item)"
              type="button"
              class="rounded-lg p-2 text-slate-400 hover:bg-amber-50 hover:text-amber-700"
              title="Configurar matriz de permisos"
              aria-label="Gestionar permisos"
              @click="abrirPermisosModal(item)"
            >
              <KeyRound :size="17" />
            </button>

            <template v-if="canEditUser(item) || canDeleteUser(item)">
              <button
                v-if="canEditUser(item)"
                type="button"
                class="rounded-lg p-2 text-slate-400 hover:bg-primary-50 hover:text-primary-600"
                title="Editar usuario"
                aria-label="Editar usuario"
                @click="openEdit(item)"
              >
                <Pencil :size="17" />
              </button>
              <button
                v-if="canDeleteUser(item)"
                type="button"
                class="rounded-lg p-2 text-slate-400 hover:bg-danger-50 hover:text-danger-600"
                title="Desactivar usuario"
                aria-label="Desactivar usuario"
                @click="askDelete(item)"
              >
                <UserX :size="17" />
              </button>
            </template>
          </div>
        </template>
        </BaseTable>
      </div>

      <!-- En móvil cada registro se presenta como tarjeta para evitar una tabla horizontal ilegible. -->
      <section class="space-y-3 sm:hidden" aria-label="Listado de usuarios">
        <div
          v-if="loading"
          class="flex min-h-40 items-center justify-center rounded-2xl border border-slate-200 bg-white"
        >
          <div class="size-7 animate-spin rounded-full border-2 border-primary-200 border-t-primary-600" />
        </div>

        <div
          v-else-if="usuarios.length === 0"
          class="rounded-2xl border border-dashed border-slate-300 bg-white px-5 py-10 text-center text-sm text-slate-500"
        >
          No se encontraron usuarios con los filtros actuales.
        </div>

        <template v-else>
        <article
          v-for="item in usuarios"
          :key="item.id"
          class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xs"
        >
          <div class="p-4">
            <div class="flex min-w-0 items-start gap-3">
              <div
                class="grid size-11 shrink-0 place-items-center rounded-xl text-sm font-bold"
                :class="avatarClasses[item.rol] || 'bg-slate-100 text-slate-700'"
              >
                {{ item.nombre?.charAt(0) }}{{ item.apellido?.charAt(0) }}
              </div>
              <div class="min-w-0 flex-1">
                <p class="truncate font-bold text-slate-900">{{ item.nombre_completo }}</p>
                <p class="truncate text-xs text-slate-500">@{{ item.username }}</p>
                <p class="mt-0.5 break-all text-xs text-slate-500">{{ item.correo }}</p>
              </div>
              <span
                class="inline-flex shrink-0 items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-semibold"
                :class="item.is_active ? 'bg-success-50 text-success-700' : 'bg-slate-100 text-slate-500'"
              >
                <span class="size-1.5 rounded-full" :class="item.is_active ? 'bg-success-500' : 'bg-slate-400'" />
                {{ item.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </div>

            <div class="mt-4 flex flex-wrap items-center gap-2">
              <span
                class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset"
                :class="roleClasses[item.rol] || 'bg-slate-100 text-slate-700 ring-slate-400/20'"
              >
                {{ roleLabels[item.rol] ?? item.rol }}
              </span>
              <span class="rounded-full bg-slate-100 px-2.5 py-1 font-mono text-xs text-slate-600">
                DNI: {{ item.dni || 'Sin registrar' }}
              </span>
            </div>

            <div class="mt-4 rounded-xl bg-slate-50 px-3 py-2.5">
              <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Supervisor directo</p>
              <p class="mt-0.5 text-xs font-semibold text-slate-700">
                {{ item.supervisor?.nombre_completo || 'Ninguno' }}
              </p>
            </div>
          </div>

          <div class="grid grid-flow-col auto-cols-fr border-t border-slate-200 bg-slate-50/70 p-2">
            <button
              type="button"
              class="flex min-h-11 items-center justify-center gap-1.5 rounded-xl text-xs font-semibold text-slate-600 transition-colors hover:bg-white hover:text-slate-900"
              aria-label="Ver detalle"
              @click="detailUsuario = item"
            >
              <Eye :size="17" />
              <span>Ver</span>
            </button>
            <button
              v-if="canManagePermisos(item)"
              type="button"
              class="flex min-h-11 items-center justify-center gap-1.5 rounded-xl text-xs font-semibold text-amber-700 transition-colors hover:bg-amber-50"
              aria-label="Gestionar permisos"
              @click="abrirPermisosModal(item)"
            >
              <KeyRound :size="17" />
              <span>Permisos</span>
            </button>
            <button
              v-if="canEditUser(item)"
              type="button"
              class="flex min-h-11 items-center justify-center gap-1.5 rounded-xl text-xs font-semibold text-primary-700 transition-colors hover:bg-primary-50"
              aria-label="Editar usuario"
              @click="openEdit(item)"
            >
              <Pencil :size="17" />
              <span>Editar</span>
            </button>
            <button
              v-if="canDeleteUser(item)"
              type="button"
              class="flex min-h-11 items-center justify-center gap-1.5 rounded-xl text-xs font-semibold text-danger-600 transition-colors hover:bg-danger-50"
              aria-label="Desactivar usuario"
              @click="askDelete(item)"
            >
              <UserX :size="17" />
              <span class="sr-only">Desactivar</span>
            </button>
          </div>
        </article>
        </template>
      </section>

      <BasePagination
        :page="filters.page"
        :total-pages="pagination.totalPages"
        :total="pagination.total"
        :loading="loading"
        @change="changePage"
      />
    </template>

    <!-- Vista 2: Organigrama Jerárquico Interactivo -->
    <template v-else>
      <OrgChartTree
        ref="orgChartRef"
        :arbol="organigrama.arbol.value"
        :raw-arbol="organigrama.rawArbol.value"
        :grupos="organigrama.grupos.value"
        :meta="organigrama.meta.value"
        :active-view="organigrama.activeView.value"
        :dock-open="organigrama.dockOpen.value"
        :dock-tab="organigrama.dockTab.value"
        :supervisores="supervisorOptions"
        :total-nodos="organigrama.totalNodos.value"
        :sede-info="organigrama.sedeInfo.value"
        :loading="organigrama.loading.value"
        :selected-id="organigrama.selectedUser.value?.id"
        :zoom="organigrama.zoom.value"
        :pan="organigrama.pan"
        :is-dragging="organigrama.isDragging.value"
        :has-dragged="organigrama.hasDragged.value"
        :collapsed-nodes="organigrama.collapsedNodes.value"
        :assigning-user-id="organigrama.assigningUserId.value"
        :zoom-in="organigrama.zoomIn"
        :zoom-out="organigrama.zoomOut"
        :reset-view="organigrama.resetView"
        :expand-all="organigrama.expandAll"
        :collapse-all="organigrama.collapseAll"
        :toggle-collapse="organigrama.toggleCollapse"
        :on-mouse-down="organigrama.onMouseDown"
        :on-mouse-move="organigrama.onMouseMove"
        :on-mouse-up="organigrama.onMouseUp"
        :on-touch-start="organigrama.onTouchStart"
        :on-touch-move="organigrama.onTouchMove"
        :on-touch-end="organigrama.onTouchEnd"
        :on-wheel="organigrama.onWheel"
        @change-view="organigrama.setActiveView"
        @open-dock="organigrama.openDock"
        @close-dock="organigrama.closeDock"
        @update:dock-tab="organigrama.setDockTab"
        @assign-supervisor="onAssignSupervisorFromDock"
        @select="organigrama.openDrawer"
        @manage-permisos="abrirPermisosModal"
        @export-success="onOrgExportSuccess"
        @export-error="onOrgExportError"
      />
    </template>


    <!-- Drawer lateral de información y subordinados del organigrama -->
    <OrgUserDrawer
      :open="organigrama.drawerOpen.value"
      :user="organigrama.selectedUser.value"
      @close="organigrama.closeDrawer"
      @edit="onEditFromDrawer"
      @delete="onDeleteFromDrawer"
      @manage-permisos="abrirPermisosModal"
      @add-subordinate="onAddSubordinateFromDrawer"
    />

    <!-- Modal de la Matriz de Permisos CRUD por módulo -->
    <PermisosModal
      :open="permisosModalOpen"
      :user="permisosTargetUser"
      @close="cerrarPermisosModal"
      @saved="onPermisosSaved"
    />

    <!-- Modal de Creación / Edición de Usuario -->
    <BaseModal
      :open="modalOpen"
      :title="isEditing ? 'Editar usuario' : 'Nuevo usuario'"
      description="Completa los datos institucionales, asigna la sede y define su supervisor jerárquico."
      size="md"
      @close="closeModal"
    >
      <form id="user-form" class="grid grid-cols-1 min-[480px]:grid-cols-2 gap-3 sm:gap-3.5" @submit.prevent="submit">
        <!-- Par 1: Nombre y Apellido -->
        <BaseInput
          id="user-name"
          v-model="form.nombre"
          appearance="light"
          label="Nombre"
          placeholder="Ej. Carlos"
          :error="formErrors.nombre"
        />
        <BaseInput
          id="user-lastname"
          v-model="form.apellido"
          appearance="light"
          label="Apellido"
          placeholder="Ej. Mendoza"
        />

        <!-- Par 2: Correo institucional y Nombre de usuario -->
        <BaseInput
          id="user-email"
          v-model="form.correo"
          type="email"
          appearance="light"
          label="Correo institucional"
          placeholder="cmendoza@udh.edu.pe"
          :error="formErrors.correo"
          autocomplete="email"
        />
        <BaseInput
          id="user-username"
          v-model="form.username"
          appearance="light"
          label="Nombre de usuario"
          placeholder="cmendoza"
          :error="formErrors.username"
        />

        <!-- Par 3: DNI y Contraseña -->
        <BaseInput
          id="user-dni"
          v-model="form.dni"
          appearance="light"
          label="DNI"
          placeholder="12345678"
          :error="formErrors.dni"
        />
        <BaseInput
          id="user-password"
          v-model="form.password"
          type="password"
          appearance="light"
          :label="isEditing ? 'Nueva contraseña (opcional)' : 'Contraseña'"
          placeholder="Mínimo 8 caracteres"
          :error="formErrors.password"
          autocomplete="new-password"
        />

        <!-- Par 4: Rol y Sede física asignada -->
        <BaseSelect
          id="user-role"
          v-model="form.rol"
          label="Rol institucional"
          :options="availableRoleOptions"
          :error="formErrors.rol"
        />
        <div>
          <BaseSelect
            id="user-sede-form"
            :model-value="form.sede_ids[0] ?? ''"
            label="Sede física asignada *"
            :options="localesLoading ? [] : sedeOptions"
            :placeholder="localesLoading ? 'Cargando sedes…' : 'Seleccionar sede física'"
            :disabled="localesLoading"
            :error="formErrors.sede_ids"
            @update:model-value="onSedeFormChange"
          />
          <div
            v-if="localesError"
            class="mt-1 flex items-center justify-between gap-2 text-xs text-danger-600"
            role="alert"
          >
            <span>{{ localesError }}</span>
            <button
              type="button"
              class="shrink-0 font-semibold text-primary-600 transition-colors hover:text-primary-700"
              @click="loadLocales()"
            >
              Reintentar
            </button>
          </div>
        </div>

        <!-- Par 5: Supervisor directo y Estado de cuenta -->
        <div class="flex flex-col gap-1.5">
          <label class="text-xs font-semibold tracking-wide text-slate-600 pl-0.5 select-none">
            Línea de supervisión
          </label>
          <div
            v-if="form.rol === 'docente'"
            class="flex min-h-11 items-center gap-2 rounded-xl border border-sky-100 bg-sky-50/80 px-3 text-xs text-sky-800"
          >
            <UserCheck :size="15" class="shrink-0 text-sky-600" />
            <span class="truncate">Exento de supervisión</span>
          </div>
          <BaseSelect
            v-else
            id="user-supervisor-form"
            v-model="form.supervisor_id"
            :options="[{ value: null, label: 'Ninguno (Nivel superior)' }, ...supervisorOptions]"
            placeholder="Seleccionar supervisor"
          />
        </div>

        <div class="flex flex-col gap-1.5">
          <span class="text-xs font-semibold tracking-wide text-slate-600 pl-0.5 select-none">
            Estado de acceso
          </span>
          <label class="flex min-h-11 cursor-pointer items-center gap-2.5 rounded-xl border border-slate-200 bg-slate-50/70 px-3.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100">
            <input v-model="form.is_active" type="checkbox" class="size-4 rounded accent-primary-600" />
            <span>Cuenta activa en KairOs</span>
          </label>
        </div>
      </form>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="closeModal">Cancelar</BaseButton>
        <BaseButton type="submit" form="user-form" variant="accent" :loading="saving" :full-width="false">
          {{ isEditing ? 'Guardar cambios' : 'Crear usuario' }}
        </BaseButton>
      </template>
    </BaseModal>

    <!-- Modal de confirmación para desactivar -->
    <BaseModal :open="deleteModalOpen" title="Desactivar usuario" size="sm" @close="cancelDelete">
      <p class="text-sm leading-6 text-slate-600">
        La cuenta de <strong class="text-slate-900">{{ pendingDelete?.nombre_completo }}</strong> perderá el acceso,
        pero se conservarán sus relaciones e historial en el organigrama.
      </p>
      <template #footer>
        <BaseButton variant="ghost" :full-width="false" @click="cancelDelete">Cancelar</BaseButton>
        <BaseButton variant="danger" :loading="saving" :full-width="false" @click="confirmDelete">
          Desactivar
        </BaseButton>
      </template>
    </BaseModal>

    <!-- Modal de detalle simple -->
    <EntityDetailModal
      :open="detailUsuario !== null"
      :title="detailUsuario?.nombre_completo ?? ''"
      description="Información de la cuenta y registro de auditoría."
      modulo="usuario"
      :object-id="detailUsuario?.id"
      @close="detailUsuario = null"
    >
      <template #info>
        <div v-if="detailUsuario" class="grid grid-cols-1 gap-x-8 gap-y-5 sm:grid-cols-2">
          <div class="flex flex-col gap-0.5">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Nombre</p>
            <p class="text-sm font-semibold text-slate-800">{{ detailUsuario.nombre }}</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Apellido</p>
            <p class="text-sm font-semibold text-slate-800">{{ detailUsuario.apellido }}</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Usuario</p>
            <p class="font-mono text-sm text-slate-700">@{{ detailUsuario.username }}</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">DNI</p>
            <p class="font-mono text-sm text-slate-700">{{ detailUsuario.dni || '—' }}</p>
          </div>
          <div class="sm:col-span-2 flex flex-col gap-0.5">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Correo institucional</p>
            <p class="text-sm text-slate-700">{{ detailUsuario.correo }}</p>
          </div>
          <div class="flex flex-col gap-0.5">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Rol</p>
            <span
              class="inline-flex w-fit rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset"
              :class="roleClasses[detailUsuario.rol]"
            >
              {{ roleLabels[detailUsuario.rol] ?? detailUsuario.rol }}
            </span>
          </div>
          <div class="flex flex-col gap-0.5">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Estado</p>
            <span
              class="inline-flex w-fit items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
              :class="detailUsuario.is_active ? 'bg-success-50 text-success-700' : 'bg-slate-100 text-slate-500'"
            >
              <span
                class="size-1.5 rounded-full"
                :class="detailUsuario.is_active ? 'bg-success-500' : 'bg-slate-400'"
              />
              {{ detailUsuario.is_active ? 'Activo' : 'Inactivo' }}
            </span>
          </div>
        </div>
      </template>
    </EntityDetailModal>

    <BaseToast :show="toast.show" :message="toast.message" :type="toast.type" @close="closeToast" />
  </div>
</template>

<script setup>
import {
  Eye,
  KeyRound,
  Network,
  Pencil,
  Plus,
  RefreshCw,
  Search,
  ShieldCheck,
  Table,
  UserCheck,
  UsersRound,
  UserX,
  Wrench,
} from '@lucide/vue';
import { ref, shallowRef } from 'vue';

import EntityDetailModal from '@/components/shared/EntityDetailModal.vue';
import BaseButton from '@/components/buttons/BaseButton.vue';
import StatCard from '@/components/cards/StatCard.vue';
import BaseInput from '@/components/inputs/BaseInput.vue';
import BaseModal from '@/components/modals/BaseModal.vue';
import BasePagination from '@/components/pagination/BasePagination.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import BaseTable from '@/components/tables/BaseTable.vue';
import BaseToast from '@/components/toasts/BaseToast.vue';
import OrgChartTree from '@/components/organigrama/OrgChartTree.vue';
import OrgUserDrawer from '@/components/organigrama/OrgUserDrawer.vue';
import PermisosModal from '@/components/organigrama/PermisosModal.vue';

import { useOrganigrama } from '@/composables/usuarios/useOrganigrama';
import { useUsuarios } from '@/composables/usuarios/useUsuarios';

const viewMode = ref('tabla');
const detailUsuario = shallowRef(null);
const permisosModalOpen = ref(false);
const permisosTargetUser = shallowRef(null);
const orgChartRef = ref(null);

const organigrama = useOrganigrama();

const columns = [
  { key: 'usuario', label: 'Usuario' },
  { key: 'dni', label: 'DNI' },
  { key: 'rol', label: 'Rol' },
  { key: 'supervisor', label: 'Supervisor' },
  { key: 'estado', label: 'Estado' },
  { key: 'acciones', label: 'Acciones', class: 'text-right' },
];

const {
  usuarios,
  loading,
  saving,
  modalOpen,
  deleteModalOpen,
  pendingDelete,
  form,
  formErrors,
  filters,
  pagination,
  stats,
  toast,
  isEditing,
  canManageAll,
  canCreate,
  canEditUser,
  canDeleteUser,
  canManagePermisos,
  filterRoleOptions,
  availableRoleOptions,
  localesLoading,
  localesError,
  sedeOptions,
  supervisorOptions,
  loadLocales,
  openCreate,
  openEdit,
  closeModal,
  submit: submitUser,
  askDelete,
  cancelDelete,
  confirmDelete: confirmDeleteUser,
  applyFilters,
  clearFilters,
  changePage,
  closeToast,
} = useUsuarios();

const onSedeFormChange = (val) => {
  form.sede_ids = val ? [Number(val)] : [];
  form.sede_principal_id = val ? Number(val) : null;
};

const submit = async () => {
  const saved = await submitUser();
  if (saved) {
    await organigrama.loadOrganigrama();
  }
  return saved;
};

const confirmDelete = async () => {
  const deleted = await confirmDeleteUser();
  if (deleted) {
    await organigrama.loadOrganigrama();
  }
  return deleted;
};

const onFilterSubmit = () => {
  if (viewMode.value === 'tabla') {
    applyFilters();
  } else {
    organigrama.loadOrganigrama();
  }
};

const switchToOrganigrama = () => {
  viewMode.value = 'organigrama';
  organigrama.loadOrganigrama();
};

const onOrganigramaSedeChange = (sedeId) => {
  organigrama.selectedLocalId.value = sedeId;
  organigrama.loadOrganigrama();
};

const abrirPermisosModal = (user) => {
  organigrama.closeDrawer();
  permisosTargetUser.value = user;
  permisosModalOpen.value = true;
};

const cerrarPermisosModal = () => {
  permisosModalOpen.value = false;
  permisosTargetUser.value = null;
};

const onPermisosSaved = () => {
  toast.show = true;
  toast.message = 'Permisos actualizados correctamente.';
  toast.type = 'success';
  if (viewMode.value === 'organigrama') {
    organigrama.loadOrganigrama();
  }
};

const onAssignSupervisorFromDock = async ({ usuarioId, supervisorId }) => {
  try {
    await organigrama.assignSupervisor(usuarioId, supervisorId);
    toast.show = true;
    toast.message = 'Supervisor asignado correctamente.';
    toast.type = 'success';
  } catch {
    toast.show = true;
    toast.message = organigrama.error.value || 'Error al asignar el supervisor.';
    toast.type = 'danger';
  }
};

const onEditFromDrawer = (user) => {
  organigrama.closeDrawer();
  openEdit(user);
};

const onDeleteFromDrawer = (user) => {
  organigrama.closeDrawer();
  askDelete(user);
};

const onAddSubordinateFromDrawer = (supervisor) => {
  organigrama.closeDrawer();
  openCreate();
  // Preseleccionar supervisor directo
  form.supervisor_id = supervisor.id;
  // Preseleccionar sede física del supervisor si existe
  if (supervisor.sedes && supervisor.sedes.length > 0) {
    const sedeId = Number(supervisor.sedes[0].id);
    form.sede_ids = [sedeId];
    form.sede_principal_id = sedeId;
  }
};

const onOrgExportSuccess = ({ filename }) => {
  toast.show = true;
  toast.message = `Organigrama exportado exitosamente como ${filename}`;
  toast.type = 'success';
};

const onOrgExportError = () => {
  toast.show = true;
  toast.message = 'No se pudo generar la imagen del organigrama. Intente nuevamente.';
  toast.type = 'danger';
};

const roleClasses = {
  superadmin: 'bg-amber-50 text-amber-800 ring-amber-500/20',
  admin: 'bg-violet-50 text-violet-700 ring-violet-600/10',
  responsable: 'bg-purple-50 text-purple-700 ring-purple-600/10',
  tecnico: 'bg-primary-50 text-primary-700 ring-primary-600/10',
  docente: 'bg-success-50 text-success-700 ring-success-600/10',
  usuario: 'bg-slate-100 text-slate-700 ring-slate-500/10',
};

const roleLabels = {
  superadmin: 'Superadministrador',
  admin: 'Administrador',
  responsable: 'Responsable',
  tecnico: 'Técnico',
  docente: 'Docente',
  usuario: 'Usuario',
};

const avatarClasses = {
  superadmin: 'bg-amber-100 text-amber-800',
  admin: 'bg-primary-100 text-primary-800',
  responsable: 'bg-purple-100 text-purple-800',
  tecnico: 'bg-emerald-100 text-emerald-800',
  docente: 'bg-sky-100 text-sky-800',
  usuario: 'bg-slate-100 text-slate-700',
};
</script>
