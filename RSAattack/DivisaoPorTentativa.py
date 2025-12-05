import math
from typing import Tuple, Dict, Any
import pandas as pd
from datetime import datetime


def trial_division_basic(n: int, e: int) -> Tuple[int | None, int | None, Dict[str, Any]]:
    limit = math.isqrt(n)
    steps = 0

    if n % 2 == 0:
        return (2, n // 2, {"steps": 1})

    for d in range(3, limit + 1, 2):
        steps += 1
        if n % d == 0:
            return (d, n // d, {"steps": steps})

    return (None, None, {"steps": steps})


def trial_division_with_primes(n: int, e: int, primes: list = None) -> Tuple[int | None, int | None, Dict[str, Any]]:
    if primes is None:
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    
    steps = 0
    limit = math.isqrt(n)

    for p in primes:
        steps += 1
        if p > limit:
            break
        if n % p == 0:
            return (p, n // p, {"steps": steps, "used_prime_list": True})

    d = 101
    while d <= limit:
        steps += 1
        if n % d == 0:
            return (d, n // d, {"steps": steps, "used_prime_list": True})
        d += 2

    return (None, None, {"steps": steps, "used_prime_list": True})


def trial_division_wheel(n: int, e: int) -> Tuple[int | None, int | None, Dict[str, Any]]:
    for p in [2, 3, 5]:
        if n % p == 0:
            return (p, n // p, {"steps": 1, "wheel_optimized": True})

    increments = [4, 2, 4, 2, 4, 6, 2, 6]
    d = 7
    steps = 3
    i = 0
    limit = math.isqrt(n)

    while d <= limit:
        steps += 1
        if n % d == 0:
            return (d, n // d, {"steps": steps, "wheel_optimized": True})
        d += increments[i]
        i = (i + 1) % len(increments)

    return (None, None, {"steps": steps, "wheel_optimized": True})


def trial_division_factorization(n: int, e: int) -> Tuple[int | None, int | None, Dict[str, Any]]:
    factors = []
    original_n = n
    steps = 0

    while n % 2 == 0:
        factors.append(2)
        n //= 2
        steps += 1

    d = 3
    limit = math.isqrt(n)

    while d <= limit:
        steps += 1
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 2

    if n > 1:
        factors.append(n)

    if len(factors) >= 2:
        return (factors[0], original_n // factors[0], {"steps": steps, "all_factors": factors})
    
    return (None, None, {"steps": steps, "all_factors": factors})


def trial_division_progress(n: int, e: int, progress_interval: int = 100) -> Tuple[int | None, int | None, Dict[str, Any]]:
    limit = math.isqrt(n)
    steps = 0
    max_progress_printed = 0

    if n % 2 == 0:
        return (2, n // 2, {"steps": 1})

    for d in range(3, limit + 1, 2):
        steps += 1

        if steps % progress_interval == 0:
            percent = (d / limit) * 100
            print(f"   [Trial Division] {percent:.1f}% ({d}/{limit}) testados...")
            max_progress_printed = steps

        if n % d == 0:
            return (d, n // d, {"steps": steps, "max_progress": max_progress_printed})

    return (None, None, {"steps": steps, "max_progress": max_progress_printed})


def export_results_to_excel(results, attack_name, filename=None):
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_attack_name = attack_name.replace(" ", "_").lower()
        filename = f"trial_division_{safe_attack_name}_{timestamp}.xlsx"
    
    data = []
    for r in results:
        row = {
            "Bits": r.key_bits,
            "N": r.n,
            "Sucesso": r.success,
            "P": r.p if r.p else "",
            "Q": r.q if r.q else "",
            "Tempo (s)": r.elapsed_seconds,
            "Steps": r.extra.get("steps", ""),
        }
        
        for key, value in r.extra.items():
            if key not in ["steps"]:
                if isinstance(value, list):
                    row[key] = str(value)
                else:
                    row[key] = value
        
        data.append(row)
    
    df = pd.DataFrame(data)
    
    summary_data = []
    stats = {}
    for r in results:
        stats.setdefault(r.key_bits, []).append(r)
    
    for bits, group in sorted(stats.items()):
        total_b = len(group)
        ok_b = sum(1 for r in group if r.success)
        rate_b = (ok_b / total_b * 100) if total_b > 0 else 0.0
        avg_time = sum(r.elapsed_seconds for r in group) / total_b if total_b > 0 else 0.0
        
        steps_list = [r.extra.get("steps") for r in group if isinstance(r.extra.get("steps"), (int, float))]
        avg_steps = sum(steps_list) / len(steps_list) if steps_list else 0.0
        
        summary_data.append({
            "Bits": bits,
            "Total": total_b,
            "Sucessos": ok_b,
            "Taxa Sucesso (%)": rate_b,
            "Tempo Médio (s)": avg_time,
            "Steps Médio": avg_steps
        })
    
    df_summary = pd.DataFrame(summary_data)
    
    total = len(results)
    success_count = sum(1 for r in results if r.success)
    fail_count = total - success_count
    success_rate = (success_count / total * 100) if total > 0 else 0.0
    
    global_summary = pd.DataFrame([{
        "Métrica": "Total de Testes",
        "Valor": total
    }, {
        "Métrica": "Sucessos",
        "Valor": success_count
    }, {
        "Métrica": "Falhas",
        "Valor": fail_count
    }, {
        "Métrica": "Taxa de Sucesso (%)",
        "Valor": f"{success_rate:.2f}"
    }, {
        "Métrica": "Método",
        "Valor": attack_name
    }])
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        global_summary.to_excel(writer, sheet_name='Resumo Global', index=False)
        df_summary.to_excel(writer, sheet_name='Resumo por Bits', index=False)
        df.to_excel(writer, sheet_name='Resultados Detalhados', index=False)
        
        workbook = writer.book
        
        for sheet in workbook.worksheets:
            for column in sheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                sheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"\n📊 Resultados exportados para: {filename}\n")
    return filename


if __name__ == "__main__":
    from BaseAttack import RSABenchmark, print_final_report

    bench = RSABenchmark(
        key_sizes_bits=(16, 20, 24, 28),
        seed=42,
    )

    print("\n========== TESTE 1: TRIAL DIVISION BÁSICO ==========")
    results_basic = bench.run(trial_division_basic)
    print_final_report(results_basic)
    export_results_to_excel(results_basic, "Básico")

    bench = RSABenchmark(
        key_sizes_bits=(16, 20, 24, 28),
        seed=42,
    )

    print("\n========== TESTE 2: TRIAL DIVISION COM PRIMOS ==========")
    results_primes = bench.run(trial_division_with_primes)
    print_final_report(results_primes)
    export_results_to_excel(results_primes, "Com Primos")

    bench = RSABenchmark(
        key_sizes_bits=(16, 20, 24, 28),
        seed=42,
    )

    print("\n========== TESTE 3: TRIAL DIVISION WHEEL ==========")
    results_wheel = bench.run(trial_division_wheel)
    print_final_report(results_wheel)
    export_results_to_excel(results_wheel, "Wheel")

    bench = RSABenchmark(
        key_sizes_bits=(16, 20, 24, 28),
        seed=42,
    )

    print("\n========== TESTE 4: TRIAL DIVISION FATORAÇÃO COMPLETA ==========")
    results_factorization = bench.run(trial_division_factorization)
    print_final_report(results_factorization)
    export_results_to_excel(results_factorization, "Fatoração Completa")

    bench = RSABenchmark(
        key_sizes_bits=(16, 20, 24, 28),
        seed=42,
    )

    print("\n========== TESTE 5: TRIAL DIVISION COM PROGRESSO ==========")
    results_progress = bench.run(trial_division_progress, progress_interval=50)
    print_final_report(results_progress)
    export_results_to_excel(results_progress, "Com Progresso")