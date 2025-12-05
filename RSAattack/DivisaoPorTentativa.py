import math
from typing import Tuple, Dict, Any
import pandas as pd
from datetime import datetime
import time


class TimeoutFlag:
    def __init__(self, timeout_seconds=10):
        self.timeout_seconds = timeout_seconds
        self.start_time = time.perf_counter()
        self.timeout_flag = False


def trial_division_basic(n: int, e: int, timeout_flag=None, **kwargs) -> Tuple[int | None, int | None, Dict[str, Any]]:
    limit = math.isqrt(n)
    steps = 0

    if n % 2 == 0:
        return (2, n // 2, {"steps": 1, "method": "basic", "found_at": 2})

    for d in range(3, limit + 1, 2):
        steps += 1
        if steps % 100 == 0 and timeout_flag:
            elapsed = time.perf_counter() - timeout_flag.start_time
            if elapsed > timeout_flag.timeout_seconds:
                timeout_flag.timeout_flag = True
                return (None, None, {"steps": steps, "method": "basic", "limit": limit, "status": "timeout"})
        
        if n % d == 0:
            return (d, n // d, {"steps": steps, "method": "basic", "found_at": d, "limit": limit})

    return (None, None, {"steps": steps, "method": "basic", "limit": limit, "status": "prime"})


def trial_division_with_primes(n: int, e: int, primes: list = None, timeout_flag=None, **kwargs) -> Tuple[int | None, int | None, Dict[str, Any]]:
    if primes is None:
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    
    steps = 0
    limit = math.isqrt(n)

    for p in primes:
        steps += 1
        if p > limit:
            break
        if n % p == 0:
            return (p, n // p, {"steps": steps, "method": "with_primes", "found_at": p, "used_prime_list": True, "primes_tested": steps})

    d = 101
    composite_steps = 0
    while d <= limit:
        steps += 1
        composite_steps += 1
        if composite_steps % 100 == 0 and timeout_flag:
            elapsed = time.perf_counter() - timeout_flag.start_time
            if elapsed > timeout_flag.timeout_seconds:
                timeout_flag.timeout_flag = True
                return (None, None, {"steps": steps, "method": "with_primes", "limit": limit, "status": "timeout"})
        
        if n % d == 0:
            return (d, n // d, {"steps": steps, "method": "with_primes", "found_at": d, "used_prime_list": True, "primes_tested": len([p for p in primes if p <= limit]), "composite_tested": composite_steps})
        d += 2

    return (None, None, {"steps": steps, "method": "with_primes", "limit": limit, "status": "prime"})


def trial_division_wheel(n: int, e: int, timeout_flag=None, **kwargs) -> Tuple[int | None, int | None, Dict[str, Any]]:
    for p in [2, 3, 5]:
        if n % p == 0:
            return (p, n // p, {"steps": 1, "method": "wheel", "found_at": p, "wheel_optimized": True})

    increments = [4, 2, 4, 2, 4, 6, 2, 6]
    d = 7
    steps = 3
    i = 0
    limit = math.isqrt(n)

    while d <= limit:
        steps += 1
        
        if steps % 100 == 0 and timeout_flag:
            elapsed = time.perf_counter() - timeout_flag.start_time
            if elapsed > timeout_flag.timeout_seconds:
                timeout_flag.timeout_flag = True
                return (None, None, {"steps": steps, "method": "wheel", "limit": limit, "status": "timeout"})
        
        if n % d == 0:
            return (d, n // d, {"steps": steps, "method": "wheel", "found_at": d, "wheel_optimized": True, "pattern_cycles": steps // len(increments)})
        d += increments[i]
        i = (i + 1) % len(increments)

    return (None, None, {"steps": steps, "method": "wheel", "limit": limit, "status": "prime"})


def trial_division_factorization(n: int, e: int, timeout_flag=None, **kwargs) -> Tuple[int | None, int | None, Dict[str, Any]]:
    factors = []
    original_n = n
    steps = 0
    two_count = 0

    while n % 2 == 0:
        factors.append(2)
        n //= 2
        steps += 1
        two_count += 1

    d = 3
    limit = math.isqrt(n)

    while d <= limit:
        steps += 1
        
        if steps % 100 == 0 and timeout_flag:
            elapsed = time.perf_counter() - timeout_flag.start_time
            if elapsed > timeout_flag.timeout_seconds:
                timeout_flag.timeout_flag = True
                return (None, None, {"steps": steps, "method": "full_factorization", "status": "timeout"})
        
        factor_count = 0
        while n % d == 0:
            factors.append(d)
            n //= d
            factor_count += 1
        d += 2

    if n > 1:
        factors.append(n)

    if len(factors) >= 2:
        return (factors[0], original_n // factors[0], {
            "steps": steps, 
            "method": "full_factorization",
            "all_factors": factors,
            "unique_factors": len(set(factors)),
            "total_factors": len(factors),
            "power_of_2": two_count
        })
    
    return (None, None, {"steps": steps, "method": "full_factorization", "status": "prime"})


def trial_division_progress(n: int, e: int, timeout_flag=None, **kwargs) -> Tuple[int | None, int | None, Dict[str, Any]]:
    progress_interval = kwargs.get("progress_interval", 100)
    limit = math.isqrt(n)
    steps = 0
    progress_logs = []

    if n % 2 == 0:
        return (2, n // 2, {"steps": 1, "method": "with_progress", "found_at": 2})

    for d in range(3, limit + 1, 2):
        steps += 1

        if steps % progress_interval == 0:
            percent = (d / limit) * 100
            print(f"   [Trial Division] {percent:.1f}% ({d}/{limit}) testados...")
            progress_logs.append({"step": steps, "divisor": d, "percent": percent})
            
            if timeout_flag:
                elapsed = time.perf_counter() - timeout_flag.start_time
                if elapsed > timeout_flag.timeout_seconds:
                    timeout_flag.timeout_flag = True
                    return (None, None, {"steps": steps, "method": "with_progress", "limit": limit, "status": "timeout"})

        if n % d == 0:
            return (d, n // d, {
                "steps": steps, 
                "method": "with_progress",
                "found_at": d,
                "progress_checkpoints": len(progress_logs),
                "last_checkpoint": progress_logs[-1] if progress_logs else None
            })

    return (None, None, {"steps": steps, "method": "with_progress", "limit": limit, "status": "prime", "progress_checkpoints": len(progress_logs)})


def export_all_results_to_excel(all_results_dict, filename=None):
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trial_division_complete_analysis_{timestamp}.xlsx"
    
    detailed_data = []
    for method_name, results in all_results_dict.items():
        for r in results:
            row = {
                "Método": method_name,
                "Bits": r.key_bits,
                "N": r.n,
                "Sucesso": "✓" if r.success else "✗",
                "P": r.p if r.p else "N/A",
                "Q": r.q if r.q else "N/A",
                "Tempo (s)": round(r.elapsed_seconds, 6),
                "Steps": r.extra.get("steps", "N/A"),
                "Divisor Encontrado": r.extra.get("found_at", "N/A"),
                "Limite √N": r.extra.get("limit", "N/A"),
                "Status": r.extra.get("status", "factored"),
            }
            
            if "all_factors" in r.extra:
                row["Fatores Completos"] = str(r.extra["all_factors"])
                row["Fatores Únicos"] = r.extra.get("unique_factors", "N/A")
                row["Total Fatores"] = r.extra.get("total_factors", "N/A")
            
            if "used_prime_list" in r.extra:
                row["Usou Lista Primos"] = "Sim"
                row["Primos Testados"] = r.extra.get("primes_tested", "N/A")
            
            if "wheel_optimized" in r.extra:
                row["Otimização Wheel"] = "Sim"
                row["Ciclos Padrão"] = r.extra.get("pattern_cycles", "N/A")
            
            if "progress_checkpoints" in r.extra:
                row["Checkpoints Progresso"] = r.extra.get("progress_checkpoints", "N/A")
            
            detailed_data.append(row)
    
    df_detailed = pd.DataFrame(detailed_data)
    
    comparison_data = []
    for method_name, results in all_results_dict.items():
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
            min_steps = min(steps_list) if steps_list else 0
            max_steps = max(steps_list) if steps_list else 0
            
            comparison_data.append({
                "Método": method_name,
                "Bits": bits,
                "Total Testes": total_b,
                "Sucessos": ok_b,
                "Taxa Sucesso (%)": round(rate_b, 2),
                "Tempo Médio (s)": round(avg_time, 6),
                "Steps Médio": round(avg_steps, 2),
                "Steps Mínimo": min_steps,
                "Steps Máximo": max_steps,
            })
    
    df_comparison = pd.DataFrame(comparison_data)
    
    summary_data = []
    for method_name, results in all_results_dict.items():
        total = len(results)
        success = sum(1 for r in results if r.success)
        avg_time = sum(r.elapsed_seconds for r in results) / total if total > 0 else 0
        steps_list = [r.extra.get("steps") for r in results if isinstance(r.extra.get("steps"), (int, float))]
        avg_steps = sum(steps_list) / len(steps_list) if steps_list else 0
        
        summary_data.append({
            "Método": method_name,
            "Total de Testes": total,
            "Sucessos": success,
            "Falhas": total - success,
            "Taxa de Sucesso (%)": round((success / total * 100) if total > 0 else 0, 2),
            "Tempo Total (s)": round(sum(r.elapsed_seconds for r in results), 3),
            "Tempo Médio (s)": round(avg_time, 6),
            "Steps Médio": round(avg_steps, 2)
        })
    
    df_summary = pd.DataFrame(summary_data)
    
    info_data = [{
        "Item": "Data de Execução",
        "Valor": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, {
        "Item": "Total de Métodos Testados",
        "Valor": len(all_results_dict)
    }, {
        "Item": "Total de Testes Realizados",
        "Valor": sum(len(r) for r in all_results_dict.values())
    }, {
        "Item": "Descrição",
        "Valor": "Análise comparativa de 5 variantes do algoritmo Trial Division para fatoração RSA"
    }, {
        "Item": "Métodos",
        "Valor": ", ".join(all_results_dict.keys())
    }]
    
    df_info = pd.DataFrame(info_data)
        
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df_info.to_excel(writer, sheet_name='📋 Informações', index=False)
        df_summary.to_excel(writer, sheet_name='📊 Resumo Geral', index=False)
        df_comparison.to_excel(writer, sheet_name='📈 Comparação por Bits', index=False)
        df_detailed.to_excel(writer, sheet_name='📝 Resultados Detalhados', index=False)
        
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
                adjusted_width = min(max_length + 2, 60)
                sheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"\n" + "="*70)
    print(f"📊 ANÁLISE COMPLETA EXPORTADA COM SUCESSO!")
    print(f"📁 Arquivo: {filename}")
    print(f"📑 Abas criadas:")
    print(f"   • 📋 Informações Gerais")
    print(f"   • 📊 Resumo Geral (comparação entre métodos)")
    print(f"   • 📈 Comparação por Bits (detalhamento por tamanho)")
    print(f"   • 📝 Resultados Detalhados (todos os testes)")
    print("="*70 + "\n")
    return filename


if __name__ == "__main__":
    from BaseAttack import RSABenchmark

    all_results = {}

    print("\n" + "="*70)
    print("🚀 INICIANDO ANÁLISE COMPLETA: TRIAL DIVISION")
    print("="*70)

    key_sizes = (16, 32, 64, 128, 256, 512, 1024, 2048)
    timeout_seconds = 10

    bench1 = RSABenchmark(key_sizes_bits=key_sizes, seed=42)
    print("\n========== TESTE 1: TRIAL DIVISION BÁSICO ==========")
    all_results["1. Básico"] = bench1.run(trial_division_basic, timeout_flag=TimeoutFlag(timeout_seconds))
    bench1.print_final_report(all_results["1. Básico"])

    bench2 = RSABenchmark(key_sizes_bits=key_sizes, seed=42)
    print("\n========== TESTE 2: TRIAL DIVISION COM PRIMOS ==========")
    all_results["2. Com Primos"] = bench2.run(trial_division_with_primes, timeout_flag=TimeoutFlag(timeout_seconds))
    bench2.print_final_report(all_results["2. Com Primos"])

    bench3 = RSABenchmark(key_sizes_bits=key_sizes, seed=42)
    print("\n========== TESTE 3: TRIAL DIVISION WHEEL ==========")
    all_results["3. Wheel Optimization"] = bench3.run(trial_division_wheel, timeout_flag=TimeoutFlag(timeout_seconds))
    bench3.print_final_report(all_results["3. Wheel Optimization"])

    bench4 = RSABenchmark(key_sizes_bits=key_sizes, seed=42)
    print("\n========== TESTE 4: TRIAL DIVISION FATORAÇÃO COMPLETA ==========")
    all_results["4. Fatoração Completa"] = bench4.run(trial_division_factorization, timeout_flag=TimeoutFlag(timeout_seconds))
    bench4.print_final_report(all_results["4. Fatoração Completa"])

    bench5 = RSABenchmark(key_sizes_bits=key_sizes, seed=42)
    print("\n========== TESTE 5: TRIAL DIVISION COM PROGRESSO ==========")
    all_results["5. Com Progresso"] = bench5.run(trial_division_progress, timeout_flag=TimeoutFlag(timeout_seconds), progress_interval=50)
    bench5.print_final_report(all_results["5. Com Progresso"])

    export_all_results_to_excel(all_results)