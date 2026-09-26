"""
Empirical Challenger Stress Harness
Tests:
1. Floor name stress tests (UTF-8 non-ASCII, length boundaries, punctuation, types).
2. Multi-threaded concurrency race conditions (high contention duplicate creation, reactivation race, parallel distinct creations).
"""

import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# Setup Django
sys.path.insert(0, os.path.abspath('backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
import django
django.setup()

from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from django.db import connection, connections
from rest_framework.test import APIClient
from espacios.models import Local, Edificio, Espacio, EspacioUsuario
from usuarios.models import Usuario, UsuarioSede


def run_challenger_stress():
    print("=" * 80)
    print("EMPIRICAL CHALLENGER STRESS HARNESS — ITERATION 2 VERIFICATION")
    print("=" * 80)

    # Clean up any leftover test data
    cleanup_prefixes = ['challenger_']
    EspacioUsuario.objects.filter(usuario__username__startswith='challenger_').delete()
    Espacio.objects.filter(codigo_espacio__startswith='CHALL-').delete()
    Edificio.objects.filter(codigo__startswith='CHALL-').delete()
    Local.objects.filter(codigo__startswith='CHALL-').delete()
    UsuarioSede.objects.filter(usuario__username__startswith='challenger_').delete()
    Usuario.objects.filter(username__startswith='challenger_').delete()

    admin = Usuario.objects.filter(rol='superadmin').first() or Usuario.objects.filter(is_superuser=True).first()
    if not admin:
        admin = Usuario.objects.create_superuser(
            username='challenger_admin',
            correo='challenger_admin@udh.pe',
            nombre='Challenger',
            apellido='Admin',
        )

    # Test Local and Edificio
    local = Local.objects.create(codigo='CHALL-LOC-1', nombre='Sede Challenger Central', tipo='sede')
    edificio = Edificio.objects.create(codigo='CHALL-EDIF-1', nombre='Pabellón Challenger Alpha', local=local)

    # Base test technician
    tec = Usuario.objects.create_user(
        username='challenger_tec1',
        correo='challenger_tec1@udh.pe',
        nombre='Tecnico',
        apellido='Challenger1',
        rol='tecnico',
    )

    client = APIClient()
    client.force_authenticate(user=admin)

    failures = []

    # =========================================================================
    # PART 1: FLOOR NAMES COMPREHENSIVE STRESS TESTING
    # =========================================================================
    print("\n" + "-" * 80)
    print("PART 1: FLOOR NAMES STRESS TESTING (UTF-8, LENGTH BOUNDARIES, PUNCTUATION, TYPES)")
    print("-" * 80)

    floor_test_cases = [
        # (name, floor_value, expected_status, description)
        # 1. UTF-8 non-ASCII characters & accents
        ("utf8_accents_sotano", "Sótano -1", 201, "Spanish accent and hyphen"),
        ("utf8_accents_subterraneo", "Subterráneo", 201, "Spanish double r + accent"),
        ("utf8_accents_area_tec", "Área Técnica", 201, "Multiple accents + space"),
        ("utf8_tilde_ano", "Año 2026", 201, "Spanish eñe character"),
        ("utf8_numero_sym", "Piso № 5", 201, "Numero symbol №"),
        ("utf8_middle_dot", "Piso · 2", 201, "Middle dot symbol ·"),
        ("utf8_em_dash", "Piso — 1", 201, "Em-dash symbol —"),
        ("utf8_guillemets", "Piso «A»", 201, "Guillemet quotation marks"),
        ("utf8_kanji", "階 1", 201, "CJK / Kanji characters"),
        ("utf8_thai", "ชั้น 2", 201, "Thai script characters"),
        ("utf8_arabic", "الطابق 3", 201, "Arabic script characters"),
        ("utf8_hebrew", "קומה 4", 201, "Hebrew script characters"),
        ("utf8_emoji", "🏢 Piso 1", 201, "Unicode emoji (building)"),

        # 2. Length boundaries (max_length = 20)
        ("len_1_digit", "1", 201, "Minimum length: 1 digit"),
        ("len_1_char", "A", 201, "Minimum length: 1 alpha"),
        ("len_19_chars", "Piso Diecinueve-123", 201, "Boundary: exactly 19 characters"),
        ("len_20_chars", "12345678901234567890", 201, "Boundary: exactly 20 characters"),
        ("len_20_chars_utf8", "áéíóúáéíóúáéíóúáéíóú", 201, "Boundary: exactly 20 non-ASCII chars"),
        ("len_21_chars_exceed", "123456789012345678901", 400, "Boundary failure: 21 characters (limit 20)"),
        ("len_50_chars_exceed", "P" * 50, 400, "Extreme failure: 50 characters"),
        ("len_500_chars_exceed", "X" * 500, 400, "Extreme failure: 500 characters"),

        # 3. Punctuation and Special Characters
        ("punct_ground_pb", "PB", 201, "Planta Baja standard"),
        ("punct_ground_ss", "SS", 201, "Sub-sótano standard"),
        ("punct_mezzanine", "Mezzanine", 201, "Mezzanine standard"),
        ("punct_hash", "Piso #2", 201, "Hash character"),
        ("punct_dash", "P-01", 201, "Hyphen/dash"),
        ("punct_plus", "Nivel +3", 201, "Plus sign"),
        ("punct_colon", "Piso: 4", 201, "Colon"),
        ("punct_slash", "PB/Entrepiso", 201, "Forward slash"),
        ("punct_parentheses", "Piso (VIP)", 201, "Parentheses"),
        ("punct_ampersand", "Piso & Terraza", 201, "Ampersand"),
        ("punct_at", "Piso @ 3", 201, "At symbol @"),
        ("punct_brackets", "Piso [A]", 201, "Square brackets"),
        ("punct_quotes", 'Piso "1"', 201, "Double quotes"),
        ("punct_single_quote", "Piso '2'", 201, "Single quotes"),
        ("punct_xss_payload", "<script>x</script>", 201, "HTML/XSS raw string (19 chars)"),
        ("punct_sql_payload", "1; DROP TABLE; --", 201, "SQL injection attempt string (17 chars)"),

        # 4. Whitespace & Empty
        ("white_empty_str", "", 400, "Empty string"),
        ("white_spaces_only", "   ", 400, "Spaces only"),
        ("white_tab_only", "\t", 400, "Tab character only"),
        ("white_newline_only", "\n", 400, "Newline character only"),
        ("white_padded_trim", "  Piso 99  ", 201, "Padded whitespace (should trim)"),

        # 5. Types & Non-string inputs
        ("type_int_0", 0, 201, "Integer 0 (numeric zero floor)"),
        ("type_int_1", 1, 201, "Integer 1 (numeric floor)"),
        ("type_null", None, 400, "Explicit null/None"),
        ("type_list", [1, 2], 400, "List input"),
        ("type_dict", {"num": 1}, 400, "Dictionary input"),
    ]

    p1_passed = 0
    p1_failed = 0

    for name, floor_val, expected_status, desc in floor_test_cases:
        # Create a unique user for each test to avoid unique collision interference
        test_u = Usuario.objects.create_user(
            username=f'challenger_u_{name[:15]}',
            correo=f'{name[:15]}@udh.pe',
            rol='tecnico',
        )

        res = client.post('/api/v1/espacios/usuarios/', {
            'ambito': 'piso',
            'edificio_id': edificio.id,
            'piso': floor_val,
            'usuario_id': test_u.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')

        status_ok = (res.status_code == expected_status)
        if status_ok:
            # If 201, also verify that if it was padded, it trimmed properly
            if expected_status == 201:
                saved = EspacioUsuario.objects.get(id=res.data['id'])
                if name == "white_padded_trim":
                    if saved.piso != "Piso 99":
                        status_ok = False
                        print(f"  [FAIL] {name}: Saved piso was not trimmed: '{saved.piso}'")
                elif isinstance(floor_val, str):
                    if saved.piso != floor_val.strip():
                        status_ok = False
                        print(f"  [FAIL] {name}: Saved piso mismatch: '{saved.piso}' != '{floor_val.strip()}'")
                elif isinstance(floor_val, int):
                    if saved.piso != str(floor_val):
                        status_ok = False
                        print(f"  [FAIL] {name}: Saved int piso mismatch: '{saved.piso}' != '{str(floor_val)}'")

        if status_ok:
            p1_passed += 1
            print(f"  [PASS] {name:<26} | Status: {res.status_code} | Desc: {desc}")
        else:
            p1_failed += 1
            err_msg = f"Part 1 Failure: {name} (expected {expected_status}, got {res.status_code}, data={res.data})"
            failures.append(err_msg)
            print(f"  [FAIL] {name:<26} | Expected: {expected_status}, Got: {res.status_code} | Err: {res.data}")

    print(f"\nPart 1 Summary: {p1_passed}/{len(floor_test_cases)} PASSED, {p1_failed} FAILED")

    # =========================================================================
    # PART 2: MULTI-THREADED CONCURRENCY & RACE CONDITIONS
    # =========================================================================
    print("\n" + "-" * 80)
    print("PART 2: MULTI-THREADED CONCURRENCY & RACE CONDITIONS")
    print("-" * 80)

    # Test 2.1: 10 Threads Concurrent Duplicate Creation (High Contention)
    print("\n>>> Test 2.1: 10 Concurrent Threads attempting IDENTICAL active assignment...")
    thread_count = 10
    barrier = threading.Barrier(thread_count)
    results_21 = [None] * thread_count

    def worker_concurrent_create(idx, u_id, edif_id, floor_str):
        # Close old db connections so thread opens a fresh one
        connections.close_all()
        c = APIClient()
        c.force_authenticate(user=admin)
        barrier.wait()  # synchronize all threads to fire simultaneously
        r = c.post('/api/v1/espacios/usuarios/', {
            'ambito': 'piso',
            'edificio_id': edif_id,
            'piso': floor_str,
            'usuario_id': u_id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        results_21[idx] = (r.status_code, r.data)
        connections.close_all()

    target_user = Usuario.objects.create_user(
        username='challenger_race_user',
        correo='race_user@udh.pe',
        rol='tecnico',
    )

    threads = []
    for i in range(thread_count):
        t = threading.Thread(
            target=worker_concurrent_create,
            args=(i, target_user.id, edificio.id, 'Piso-Race-1'),
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    statuses_21 = [r[0] for r in results_21]
    count_201 = statuses_21.count(201)
    count_400 = statuses_21.count(400)
    count_500 = statuses_21.count(500)
    other_codes = [c for c in statuses_21 if c not in (201, 400)]

    db_active_count = EspacioUsuario.objects.filter(
        ambito='piso',
        edificio=edificio,
        piso='Piso-Race-1',
        usuario=target_user,
        activo=True,
        is_deleted=False,
    ).count()

    print(f"  - Results: 201 Created: {count_201}, 400 Bad Request: {count_400}, 500 Error: {count_500}, Others: {other_codes}")
    print(f"  - Active DB records for this exact assignment: {db_active_count}")

    t21_pass = (count_201 == 1 and count_400 == (thread_count - 1) and count_500 == 0 and db_active_count == 1)
    if t21_pass:
        print("  [PASS] Test 2.1 passed: Exactly 1 thread created the assignment, 9 threads received HTTP 400, 0 received 500, 1 active in DB.")
    else:
        print("  [FAIL] Test 2.1 failed!")
        failures.append(f"Test 2.1 failed: 201 count={count_201}, 400 count={count_400}, 500 count={count_500}, db_count={db_active_count}")

    # Test 2.2: 10 Threads Concurrent Reactivation of Soft-Deleted Record
    print("\n>>> Test 2.2: 10 Concurrent Threads attempting to RESTORE the same soft-deleted assignment...")
    # First, get the created assignment and soft-delete it
    asig_to_delete = EspacioUsuario.objects.get(
        ambito='piso',
        edificio=edificio,
        piso='Piso-Race-1',
        usuario=target_user,
    )
    del_res = client.delete(f'/api/v1/espacios/usuarios/{asig_to_delete.id}/')
    assert del_res.status_code == 204
    asig_to_delete.refresh_from_db()
    assert asig_to_delete.is_deleted is True and asig_to_delete.activo is False

    barrier_restore = threading.Barrier(thread_count)
    results_22 = [None] * thread_count

    def worker_concurrent_restore(idx, u_id, edif_id, floor_str):
        connections.close_all()
        c = APIClient()
        c.force_authenticate(user=admin)
        barrier_restore.wait()
        r = c.post('/api/v1/espacios/usuarios/', {
            'ambito': 'piso',
            'edificio_id': edif_id,
            'piso': floor_str,
            'usuario_id': u_id,
            'tipo_responsabilidad': 'responsable',  # change responsibility
        }, format='json')
        results_22[idx] = (r.status_code, r.data)
        connections.close_all()

    threads_restore = []
    for i in range(thread_count):
        t = threading.Thread(
            target=worker_concurrent_restore,
            args=(i, target_user.id, edificio.id, 'Piso-Race-1'),
        )
        threads_restore.append(t)
        t.start()

    for t in threads_restore:
        t.join()

    statuses_22 = [r[0] for r in results_22]
    count_201_res = statuses_22.count(201)
    count_400_res = statuses_22.count(400)
    count_500_res = statuses_22.count(500)

    db_active_after_restore = EspacioUsuario.objects.filter(
        ambito='piso',
        edificio=edificio,
        piso='Piso-Race-1',
        usuario=target_user,
        activo=True,
        is_deleted=False,
    ).count()

    print(f"  - Results: 201 Restored: {count_201_res}, 400 Bad Request: {count_400_res}, 500 Error: {count_500_res}")
    print(f"  - Active DB records after concurrent restore: {db_active_after_restore}")

    t22_pass = (count_201_res == 1 and count_400_res == (thread_count - 1) and count_500_res == 0 and db_active_after_restore == 1)
    if t22_pass:
        print("  [PASS] Test 2.2 passed: Exactly 1 thread restored the assignment, 9 threads received HTTP 400, 0 received 500, 1 active in DB.")
    else:
        print("  [FAIL] Test 2.2 failed!")
        failures.append(f"Test 2.2 failed: 201 count={count_201_res}, 400 count={count_400_res}, 500 count={count_500_res}, db_count={db_active_after_restore}")

    # Test 2.3: 10 Threads creating 10 DIFFERENT floors for the same technician in parallel
    print("\n>>> Test 2.3: 10 Concurrent Threads assigning 10 DISTINCT floors to the same technician...")
    barrier_distinct_floors = threading.Barrier(thread_count)
    results_23 = [None] * thread_count

    def worker_distinct_floors(idx, u_id, edif_id):
        connections.close_all()
        c = APIClient()
        c.force_authenticate(user=admin)
        floor_label = f'Piso-Distinct-{idx}'
        barrier_distinct_floors.wait()
        r = c.post('/api/v1/espacios/usuarios/', {
            'ambito': 'piso',
            'edificio_id': edif_id,
            'piso': floor_label,
            'usuario_id': u_id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        results_23[idx] = (r.status_code, r.data)
        connections.close_all()

    threads_distinct = []
    for i in range(thread_count):
        t = threading.Thread(
            target=worker_distinct_floors,
            args=(i, target_user.id, edificio.id),
        )
        threads_distinct.append(t)
        t.start()

    for t in threads_distinct:
        t.join()

    statuses_23 = [r[0] for r in results_23]
    count_201_distinct = statuses_23.count(201)
    print(f"  - Results: 201 Created: {count_201_distinct}/{thread_count}")
    t23_pass = (count_201_distinct == thread_count)
    if t23_pass:
        print("  [PASS] Test 2.3 passed: All 10 distinct floors successfully created in parallel without deadlock or false collision.")
    else:
        print(f"  [FAIL] Test 2.3 failed: Only {count_201_distinct}/{thread_count} succeeded. Statuses: {statuses_23}")
        failures.append(f"Test 2.3 failed: {count_201_distinct}/{thread_count} succeeded")

    # Test 2.4: 10 Threads assigning 10 DIFFERENT technicians to the SAME floor in parallel (Collaborative Non-Exclusivity R2)
    print("\n>>> Test 2.4: 10 Concurrent Threads assigning 10 DISTINCT technicians to the SAME floor (R2 Collaborative)...")
    shared_floor_users = [
        Usuario.objects.create_user(
            username=f'challenger_shared_u_{i}',
            correo=f'shared_u_{i}@udh.pe',
            rol='tecnico',
        ) for i in range(thread_count)
    ]

    barrier_shared_floor = threading.Barrier(thread_count)
    results_24 = [None] * thread_count

    def worker_shared_floor(idx, user_obj, edif_id):
        connections.close_all()
        c = APIClient()
        c.force_authenticate(user=admin)
        barrier_shared_floor.wait()
        r = c.post('/api/v1/espacios/usuarios/', {
            'ambito': 'piso',
            'edificio_id': edif_id,
            'piso': 'Piso-Shared-All',
            'usuario_id': user_obj.id,
            'tipo_responsabilidad': 'tecnico',
        }, format='json')
        results_24[idx] = (r.status_code, r.data)
        connections.close_all()

    threads_shared = []
    for i in range(thread_count):
        t = threading.Thread(
            target=worker_shared_floor,
            args=(i, shared_floor_users[i], edificio.id),
        )
        threads_shared.append(t)
        t.start()

    for t in threads_shared:
        t.join()

    statuses_24 = [r[0] for r in results_24]
    count_201_shared = statuses_24.count(201)
    print(f"  - Results: 201 Created: {count_201_shared}/{thread_count}")
    t24_pass = (count_201_shared == thread_count)
    if t24_pass:
        print("  [PASS] Test 2.4 passed: All 10 technicians successfully assigned to the same floor simultaneously (R2 non-exclusive).")
    else:
        print(f"  [FAIL] Test 2.4 failed: Only {count_201_shared}/{thread_count} succeeded. Statuses: {statuses_24}")
        failures.append(f"Test 2.4 failed: {count_201_shared}/{thread_count} succeeded")

    # =========================================================================
    # FINAL VERDICT AND REPORT
    # =========================================================================
    print("\n" + "=" * 80)
    print("CHALLENGER STRESS HARNESS EXECUTION FINISHED")
    print("=" * 80)

    # Cleanup test data
    try:
        EspacioUsuario.objects.filter(usuario__username__startswith='challenger_').delete()
        UsuarioSede.objects.filter(usuario__username__startswith='challenger_').delete()
        edificio.delete()
        local.delete()
        Usuario.objects.filter(username__startswith='challenger_').delete()
    except Exception as e:
        print(f"Warning during cleanup: {e}")

    if len(failures) == 0:
        print("\n>>> VERDICT: ALL ADVERSARIAL CHALLENGES AND STRESS TESTS PASSED (100% GREEN) <<<")
        return True
    else:
        print(f"\n>>> VERDICT: CHALLENGE FAILED with {len(failures)} failures:")
        for f in failures:
            print(f"  - {f}")
        return False


if __name__ == '__main__':
    success = run_challenger_stress()
    sys.exit(0 if success else 1)
