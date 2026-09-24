"""
Adversarial Probe & Stress Harness for Milestone 1
Tests:
1. Edge cases of scope fields (combinations, invalid IDs, missing fields, foreign sedes).
2. Concurrency & duplicate prevention (sequential duplicates, parallel thread race conditions).
3. Soft-delete reactivation lifecycle (restore, role change, audit trails).
4. Non-ASCII / edge-case floor names ('Sótano -1', 'Mezzanine', 'Piso 14', etc.).
"""

import os
import sys
import threading
import concurrent.futures
from unittest import TestCase

# Setup Django
sys.path.insert(0, os.path.abspath('backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
import django
django.setup()
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from django.db import connection, transaction
from rest_framework.test import APIClient
from rest_framework import status
from espacios.models import Local, Edificio, Espacio, EspacioUsuario
from usuarios.models import Usuario, UsuarioSede
from historial.models import Historial


def run_probe():
    print("=" * 70)
    print("STARTING EMPIRICAL ADVERSARIAL PROBE FOR MILESTONE 1")
    print("=" * 70)

    # 0. Clean prior run artifacts
    cleanup_usernames = ['tec.stress', 'tec2.stress', 'resp.stress', 'admin.stress', 'u_dup_sede', 'u_dup_edif', 'u_dup_piso', 'u_dup_esp', 'u_resp_test']
    EspacioUsuario.objects.filter(usuario__username__in=cleanup_usernames).delete()
    Espacio.objects.filter(codigo_espacio='LAB-ADV-101').delete()
    Edificio.objects.filter(codigo__in=['EDIF-ADV-1', 'EDIF-ADV-2']).delete()
    Local.objects.filter(codigo__in=['LOC-ADV-1', 'LOC-ADV-2']).delete()
    UsuarioSede.objects.filter(usuario__username__in=cleanup_usernames).delete()
    Usuario.objects.filter(username__in=cleanup_usernames).delete()

    # 1. Setup Test Data in Transaction / clean state
    admin = Usuario.objects.filter(rol='superadmin').first() or Usuario.objects.filter(is_superuser=True).first()
    if not admin:
        admin, _ = Usuario.objects.get_or_create(
            username='admin.stress',
            defaults={
                'correo': 'admin.stress@udh.edu.pe',
                'nombre': 'Admin',
                'apellido': 'Stress',
                'rol': 'admin',
            }
        )

    # Test users
    tecnico, _ = Usuario.objects.get_or_create(
        username='tec.stress',
        defaults={
            'correo': 'tec.stress@udh.edu.pe',
            'nombre': 'Tecnico',
            'apellido': 'Stress',
            'rol': 'tecnico',
        }
    )

    tecnico2 = Usuario.objects.create_user(
        correo='tec2.stress@udh.edu.pe',
        username='tec2.stress',
        nombre='Tecnico2',
        apellido='Stress',
        rol='tecnico',
    )

    responsable, _ = Usuario.objects.get_or_create(
        username='resp.stress',
        defaults={
            'correo': 'resp.stress@udh.edu.pe',
            'nombre': 'Resp',
            'apellido': 'Stress',
            'rol': 'responsable',
        }
    )

    # Locales and Edificios
    local1 = Local.objects.create(codigo='LOC-ADV-1', nombre='Sede Arequipa', tipo='sede')
    local2 = Local.objects.create(codigo='LOC-ADV-2', nombre='Sede Cusco', tipo='sede')

    edificio1 = Edificio.objects.create(codigo='EDIF-ADV-1', nombre='Pabellón Ingeniería', local=local1)
    edificio2 = Edificio.objects.create(codigo='EDIF-ADV-2', nombre='Pabellón Ciencias', local=local2)

    espacio1 = Espacio.objects.create(
        codigo_espacio='LAB-ADV-101',
        tipo='laboratorio',
        pabellon='Pabellón Ingeniería',
        edificio=edificio1,
        piso='1',
    )

    UsuarioSede.objects.create(usuario=responsable, local=local1, activo=True, es_sede_principal=True)

    client = APIClient()
    client.force_authenticate(user=admin)

    results = {
        'area1_edge_cases': {},
        'area2_duplicates_concurrency': {},
        'area3_soft_delete_lifecycle': {},
        'area4_floor_names': {},
    }

    print("\n[AREA 1] PROBING SCOPE FIELD COMBINATIONS & EDGE CASES...")

    edge_cases = [
        ("piso_missing_piso", {"ambito": "piso", "edificio_id": edificio1.id, "usuario_id": tecnico.id}, 400),
        ("piso_missing_edificio", {"ambito": "piso", "piso": "1", "usuario_id": tecnico.id}, 400),
        ("piso_missing_both", {"ambito": "piso", "usuario_id": tecnico.id}, 400),
        ("piso_with_espacio_id", {"ambito": "piso", "edificio_id": edificio1.id, "piso": "1", "espacio_id": espacio1.id, "usuario_id": tecnico.id}, 400),
        ("sede_missing_local", {"ambito": "sede", "usuario_id": tecnico.id}, 400),
        ("sede_invalid_local", {"ambito": "sede", "local_id": 9999999, "usuario_id": tecnico.id}, 400),
        ("sede_with_edificio_id", {"ambito": "sede", "local_id": local1.id, "edificio_id": edificio1.id, "usuario_id": tecnico.id}, 400),
        ("sede_with_piso", {"ambito": "sede", "local_id": local1.id, "piso": "1", "usuario_id": tecnico.id}, 400),
        ("edificio_missing_edificio", {"ambito": "edificio", "usuario_id": tecnico.id}, 400),
        ("edificio_invalid_edificio", {"ambito": "edificio", "edificio_id": 9999999, "usuario_id": tecnico.id}, 400),
        ("edificio_mismatched_local", {"ambito": "edificio", "edificio_id": edificio1.id, "local_id": local2.id, "usuario_id": tecnico.id}, 400),
        ("espacio_missing_espacio", {"ambito": "espacio", "usuario_id": tecnico.id}, 400),
        ("espacio_invalid_espacio", {"ambito": "espacio", "espacio_id": 9999999, "usuario_id": tecnico.id}, 400),
        ("espacio_mismatched_piso", {"ambito": "espacio", "espacio_id": espacio1.id, "piso": "99", "usuario_id": tecnico.id}, 400),
        ("invalid_ambito_name", {"ambito": "campus_invalido", "usuario_id": tecnico.id}, 400),
    ]

    for test_name, payload, expected_status in edge_cases:
        res = client.post('/api/v1/espacios/usuarios/', payload, format='json')
        passed = (res.status_code == expected_status)
        results['area1_edge_cases'][test_name] = {
            'status_code': res.status_code,
            'passed': passed,
            'response': res.data,
        }
        status_str = "PASS" if passed else "FAIL"
        print(f"  - {test_name:<30}: Expected {expected_status}, got {res.status_code} [{status_str}]")
        if not passed:
            print(f"    Details: {res.data}")

    print("\n[AREA 2] PROBING DUPLICATE PREVENTION & CONCURRENCY...")

    usr_dup_sede = Usuario.objects.create_user(username='u_dup_sede', correo='u_dup_sede@udh.pe', rol='tecnico')
    usr_dup_edif = Usuario.objects.create_user(username='u_dup_edif', correo='u_dup_edif@udh.pe', rol='tecnico')
    usr_dup_piso = Usuario.objects.create_user(username='u_dup_piso', correo='u_dup_piso@udh.pe', rol='tecnico')
    usr_dup_esp  = Usuario.objects.create_user(username='u_dup_esp', correo='u_dup_esp@udh.pe', rol='tecnico')

    # 2.1 Sequential Duplicates across all 4 scopes
    scopes_dup = [
        ("dup_sede", {"ambito": "sede", "local_id": local1.id, "usuario_id": usr_dup_sede.id, "tipo_responsabilidad": "responsable"}),
        ("dup_edificio", {"ambito": "edificio", "edificio_id": edificio1.id, "usuario_id": usr_dup_edif.id, "tipo_responsabilidad": "tecnico"}),
        ("dup_piso", {"ambito": "piso", "edificio_id": edificio1.id, "piso": "1", "usuario_id": usr_dup_piso.id, "tipo_responsabilidad": "tecnico"}),
        ("dup_espacio", {"ambito": "espacio", "espacio_id": espacio1.id, "usuario_id": usr_dup_esp.id, "tipo_responsabilidad": "docente"}),
    ]

    for name, payload in scopes_dup:
        res1 = client.post('/api/v1/espacios/usuarios/', payload, format='json')
        res2 = client.post('/api/v1/espacios/usuarios/', payload, format='json')
        passed = (res1.status_code == 201 and res2.status_code == 400)
        results['area2_duplicates_concurrency'][name] = {
            'res1': res1.status_code,
            'res2': res2.status_code,
            'passed': passed,
            'response2': res2.data if res2.status_code != 201 else None,
        }
        print(f"  - {name:<20}: 1st POST={res1.status_code}, 2nd POST={res2.status_code} [{'PASS' if passed else 'FAIL'}]")

    # 2.2 Concurrency / Race Condition test
    print("  - Running concurrent race condition test (2 threads attempting identical active assignment)...")
    
    def attempt_create(user_id, res_list, idx):
        c = APIClient()
        c.force_authenticate(user=admin)
        r = c.post('/api/v1/espacios/usuarios/', {
            'ambito': 'piso',
            'edificio_id': edificio2.id,
            'piso': '3',
            'usuario_id': user_id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        res_list[idx] = r

    concurrency_res = [None, None]
    t1 = threading.Thread(target=attempt_create, args=(tecnico2.id, concurrency_res, 0))
    t2 = threading.Thread(target=attempt_create, args=(tecnico2.id, concurrency_res, 1))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    statuses = sorted([r.status_code for r in concurrency_res if r is not None])
    # Exactly one should succeed (201) and one should fail (400 or 500 if DB constraint caught it)
    # The important part is that NO duplicate active record was created in DB!
    db_count = EspacioUsuario.objects.filter(
        ambito='piso', edificio=edificio2, piso='3', usuario=tecnico2, activo=True, is_deleted=False
    ).count()
    
    race_passed = (db_count == 1)
    results['area2_duplicates_concurrency']['race_condition'] = {
        'statuses': statuses,
        'db_count': db_count,
        'passed': race_passed,
    }
    print(f"  - race_condition    : Thread responses={statuses}, Active DB count={db_count} [{'PASS' if race_passed else 'FAIL'}]")

    print("\n[AREA 3] PROBING SOFT-DELETE REACTIVATION LIFECYCLE...")

    # Create assignment
    payload_lc = {
        'ambito': 'edificio',
        'edificio_id': edificio2.id,
        'usuario_id': tecnico.id,
        'tipo_responsabilidad': 'tecnico',
    }
    res_create = client.post('/api/v1/espacios/usuarios/', payload_lc, format='json')
    asig_id = res_create.data['id']
    print(f"  - Initial creation: ID={asig_id}, tipo={res_create.data['tipo_responsabilidad']}")

    # Soft delete
    res_del = client.delete(f'/api/v1/espacios/usuarios/{asig_id}/')
    asig_obj = EspacioUsuario.objects.get(id=asig_id)
    deleted_ok = (res_del.status_code == 204 and asig_obj.is_deleted and not asig_obj.activo)
    print(f"  - Soft delete     : Status={res_del.status_code}, is_deleted={asig_obj.is_deleted}, activo={asig_obj.activo} [{'PASS' if deleted_ok else 'FAIL'}]")

    # Recreate with DIFFERENT responsibility ('responsable')
    payload_recreate = {
        'ambito': 'edificio',
        'edificio_id': edificio2.id,
        'usuario_id': tecnico.id,
        'tipo_responsabilidad': 'responsable',
    }
    res_recreate = client.post('/api/v1/espacios/usuarios/', payload_recreate, format='json')
    asig_obj.refresh_from_db()
    restored_ok = (
        res_recreate.status_code == 201
        and res_recreate.data['id'] == asig_id
        and res_recreate.data['tipo_responsabilidad'] == 'responsable'
        and asig_obj.activo is True
        and asig_obj.is_deleted is False
        and asig_obj.tipo_responsabilidad == 'responsable'
    )
    results['area3_soft_delete_lifecycle']['reactivate_with_diff_resp'] = {
        'status_code': res_recreate.status_code,
        'restored_same_id': res_recreate.data.get('id') == asig_id,
        'updated_tipo': res_recreate.data.get('tipo_responsabilidad'),
        'passed': restored_ok,
    }
    print(f"  - Reactivation    : Status={res_recreate.status_code}, Same ID={res_recreate.data.get('id') == asig_id}, Updated tipo={res_recreate.data.get('tipo_responsabilidad')} [{'PASS' if restored_ok else 'FAIL'}]")

    # Check Audit Log for the restore event
    try:
        from historial.models import Historial
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(EspacioUsuario)
        audit_entry = Historial.objects.filter(
            content_type=ct,
            object_id=asig_id,
            tipo_evento='espacio.asignacion_usuario',
        ).order_by('-fecha').first()
        if audit_entry:
            print(f"  - Audit Trail     : Action={audit_entry.tipo_evento}, Detalle='{audit_entry.descripcion}'")
            audit_passed = 'reasignado' in audit_entry.descripcion
        else:
            print("  - Audit Trail     : No audit entry found")
            audit_passed = False
    except Exception as e:
        print(f"  - Audit Trail Check Exception: {e}")
        audit_passed = False
    results['area3_soft_delete_lifecycle']['audit_entry_reasignado'] = audit_passed

    print("\n[AREA 4] PROBING NON-ASCII & EDGE-CASE FLOOR NAMES...")

    test_floors = [
        ('Sótano -1', 'Non-ASCII + negative space string'),
        ('Mezzanine', 'Pure alphabetical string'),
        ('Piso 14', 'Alphanumeric with space'),
        ('PB', 'Planta Baja abbreviation'),
        ('SS', 'Sub-sótano abbreviation'),
        ('0', 'Ground floor digit 0'),
        ('14', 'Pure numeric string (baseline)'),
        ('', 'Empty string'),
    ]

    for floor_val, desc in test_floors:
        res = client.post('/api/v1/espacios/usuarios/', {
            'ambito': 'piso',
            'edificio_id': edificio1.id,
            'piso': floor_val,
            'usuario_id': tecnico2.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')

        results['area4_floor_names'][floor_val] = {
            'desc': desc,
            'status_code': res.status_code,
            'data': res.data,
        }
        print(f"  - Piso '{floor_val:<12}' ({desc:<35}): Status {res.status_code}")
    print("\n[AREA 5] PROBING R5 AUTHORIZATION BOUNDARIES & 403 ENFORCEMENT...")

    client_resp = APIClient()
    client_resp.force_authenticate(user=responsable)

    usr_resp_test = Usuario.objects.create_user(username='u_resp_test', correo='u_resp_test@udh.pe', rol='tecnico')

    # 5.1 Responsable in assigned sede -> 201
    res_resp_own = client_resp.post('/api/v1/espacios/usuarios/', {
        'ambito': 'sede',
        'local_id': local1.id,
        'usuario_id': usr_resp_test.id,
        'tipo_responsabilidad': 'tecnico',
    }, format='json')
    print(f"  - Responsable own sede (local1)     : Status {res_resp_own.status_code} [{'PASS' if res_resp_own.status_code == 201 else 'FAIL'}]")

    # 5.2 Responsable in foreign sede -> 403
    res_resp_for = client_resp.post('/api/v1/espacios/usuarios/', {
        'ambito': 'sede',
        'local_id': local2.id,
        'usuario_id': usr_resp_test.id,
        'tipo_responsabilidad': 'tecnico',
    }, format='json')
    print(f"  - Responsable foreign sede (local2) : Status {res_resp_for.status_code} [{'PASS' if res_resp_for.status_code == 403 else 'FAIL'}]")

    # 5.3 Tecnico write attempt -> 403
    client_tec = APIClient()
    client_tec.force_authenticate(user=tecnico)
    res_tec_write = client_tec.post('/api/v1/espacios/usuarios/', {
        'ambito': 'sede',
        'local_id': local1.id,
        'usuario_id': tecnico.id,
        'tipo_responsabilidad': 'tecnico',
    }, format='json')
    print(f"  - Tecnico write attempt             : Status {res_tec_write.status_code} [{'PASS' if res_tec_write.status_code == 403 else 'FAIL'}]")

    print("\n" + "=" * 70)
    print("PROBE EXECUTION COMPLETED")
    print("=" * 70)

    # Cleanup temporary test objects
    try:
        EspacioUsuario.objects.filter(usuario__in=[tecnico, tecnico2]).delete()
        espacio1.delete()
        edificio1.delete()
        edificio2.delete()
        local1.delete()
        local2.delete()
        tecnico2.delete()
    except Exception as e:
        print(f"Cleanup warning: {e}")

    return results

if __name__ == '__main__':
    run_probe()
