#!/usr/bin/env python3
"""
Test clean_domain function.
"""
import sys
sys.path.append('.')
from services.favorites import clean_domain

test_cases = [
    ("www.google.com", "google.com"),
    ("www.github.com", "github.com"),
    ("listado.mercadolibre.com.ar", "mercadolibre.com.ar"),
    ("mercadolibre.com.ar", "mercadolibre.com.ar"),
    ("www.amazon.co.uk", "amazon.co.uk"),
    ("m.facebook.com", "facebook.com"),
    ("news.ycombinator.com", "ycombinator.com"),
    ("stackoverflow.com", "stackoverflow.com"),
    ("www.reddit.com", "reddit.com"),
    ("subdomain.example.org", "example.org"),
    ("api.github.com", "github.com"),
    ("docs.python.org", "python.org"),
    ("www.chapasplasticasmyca.com", "chapasplasticasmyca.com"),
    ("www.deepseek.com", "deepseek.com"),
    ("www.pagina12.com.ar", "pagina12.com.ar"),
    ("www.tiempoar.com.ar", "tiempoar.com.ar"),
]

print("Testing clean_domain:")
all_pass = True
for domain, expected in test_cases:
    result = clean_domain(domain)
    status = "OK" if result == expected else "FAIL"
    if status == "FAIL":
        all_pass = False
    print(f"{status} {domain} -> {result} (expected: {expected})")

if all_pass:
    print("\nAll tests passed!")
else:
    print("\nSome tests failed!")
    sys.exit(1)