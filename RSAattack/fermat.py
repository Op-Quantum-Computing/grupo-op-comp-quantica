import math
from typing import Optional, Tuple
from BaseAttack import RSABenchmark

def fermat_factor(n: int, e: int = 0, max_iters: Optional[int] = None) -> Optional[Tuple[int,int]]:
    
    if n <= 1:
        return None

    if n % 2 == 0:
        return 2, n // 2

    a = math.isqrt(n)
    if a * a < n:
        a += 1

    it = 0
    while True:
        b2 = a*a - n
        if b2 < 0:
            a += 1
            it += 1
            if max_iters and it > max_iters:
                return None
            continue

        b = math.isqrt(b2)
        if b*b == b2:
            p = a - b
            q = a + b
            if 1 < p < n and 1 < q < n:
                return (p, q) if p <= q else (q, p)
            return None

        a += 1
        it += 1
        if max_iters and it > max_iters:
            return None


if __name__ == "__main__":
    bench = RSABenchmark(
        key_sizes_bits=(32, 64, 128, 256, 512, 1024, 2048),
        seed=42,
    )

    results = bench.run(
        fermat_factor,
    )

    print(f"{'Bits':4} {'Sucesso':8} {'Tempo (s)':10} Extra")
    print("-" * 60)
    for r in results:
        print(
            f"{r.key_bits:4} "
            f"{str(r.success):8} "
            f"{r.elapsed_seconds:10.6f} "
            f"{r.extra}"
        )

    bench.print_final_report(results)
