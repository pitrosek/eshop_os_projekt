#!/usr/bin/env python3
"""
Performance Tester pro eshop aplikaci
Testuje výkon jednotlivých endpointů aplikace
"""

import requests
import time
import statistics
from urllib.parse import urljoin

class PerformanceTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = {}
        
    def test_endpoint(self, endpoint, method="GET", name=None, iterations=10, data=None):
        """
        Testuje výkon konkrétního endpointu
        """
        if name is None:
            name = f"{method} {endpoint}"
        
        url = urljoin(self.base_url, endpoint)
        times = []
        errors = 0
        
        print(f"\n🧪 Testuji: {name}")
        print(f"   URL: {url}")
        print(f"   Počet iterací: {iterations}")
        
        for i in range(iterations):
            try:
                start = time.time()
                if method == "GET":
                    response = requests.get(url, timeout=10)
                elif method == "POST":
                    response = requests.post(url, data=data, timeout=10)
                elapsed = time.time() - start
                
                if response.status_code == 200:
                    times.append(elapsed)
                    print(f"   ✓ Iterace {i+1}: {elapsed:.3f}s")
                else:
                    print(f"   ✗ Iterace {i+1}: Status {response.status_code}")
                    errors += 1
                    
            except requests.exceptions.RequestException as e:
                print(f"   ✗ Iterace {i+1}: Chyba - {e}")
                errors += 1
        
        if times:
            result = {
                "endpoint": endpoint,
                "method": method,
                "min": min(times),
                "max": max(times),
                "avg": statistics.mean(times),
                "median": statistics.median(times),
                "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                "errors": errors,
                "successful": len(times)
            }
            self.results[name] = result
            
            print(f"\n📊 Výsledky pro {name}:")
            print(f"   Min:      {result['min']:.3f}s")
            print(f"   Max:      {result['max']:.3f}s")
            print(f"   Průměr:   {result['avg']:.3f}s")
            print(f"   Medián:   {result['median']:.3f}s")
            if result['stdev'] > 0:
                print(f"   StdDev:   {result['stdev']:.3f}s")
            print(f"   Úspěšných: {result['successful']}/{iterations}")
            if errors > 0:
                print(f"   Chyb:     {errors}")
        else:
            print(f"   ❌ Všechny iterace selhaly!")
    
    def print_summary(self):
        """
        Vypíše souhrn všech testů
        """
        if not self.results:
            print("\nNelze vytvořit souhrn - žádné testy nebyly provedeny.")
            return
        
        print("\n" + "="*60)
        print("📋 SOUHRN VÝKONU")
        print("="*60)
        
        for name, result in self.results.items():
            status = "✅" if result['errors'] == 0 else "⚠️"
            print(f"\n{status} {name}")
            print(f"   Průměrný čas: {result['avg']:.3f}s")
            print(f"   Rozpětí: {result['min']:.3f}s - {result['max']:.3f}s")


def main():
    """
    Hlavní funkce pro spuštění testů
    """
    tester = PerformanceTester(base_url="http://localhost:5000")
    
    print("\n" + "="*60)
    print("🚀 PERFORMANCE TESTING - eshop")
    print("="*60)
    print("\nUjistěte se, že je aplikace spuštěná na http://localhost:5000")
    print("\nZačínám testy...\n")
    
    # Testování jednotlivých endpointů
    tester.test_endpoint("/", name="Domovská stránka", iterations=10)
    tester.test_endpoint("/products", name="Produkty", iterations=10)
    tester.test_endpoint("/login", name="Přihlášení (GET)", iterations=5)
    tester.test_endpoint("/register", name="Registrace (GET)", iterations=5)
    
    # Souhrn výsledků
    tester.print_summary()
    
    print("\n" + "="*60)
    print("✅ Testování dokončeno!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
