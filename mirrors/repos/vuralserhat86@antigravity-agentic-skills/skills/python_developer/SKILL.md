---
name: python_developer
router_kit: AIKit
description: Python best practices, FastAPI, Pandas ve veri bilimi kütüphaneleri kullanımı.
metadata:
  skillport:
    category: development
    tags: [architecture, automation, best practices, clean code, coding, collaboration, compliance, debugging, design patterns, development, documentation, efficiency, git, optimization, productivity, programming, project management, python developer, quality assurance, refactoring, software engineering, standards, testing, utilities, version control, workflow]      - data-science
---

# 🐍 Python Developer

> Modern Python geliştirme standartları ve kütüphane ekosistemi.

---

*Python Developer v1.1 - Enhanced*

## 🔄 Workflow

> **Kaynak:** [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/) & [FastAPI Documentation](https://fastapi.tiangolo.com/learn/)

### Aşama 1: Environment & Dependency
- [ ] **Venv**: Her proje için izole bir sanal ortam (`venv` veya `poetry`) kur.
- [ ] **Type Hints**: Python 3.9+ tip belirteçlerini (Type Hints) kullanarak kodun okunabilirliğini artır.

### Aşama 2: API & Application Logic
- [ ] **Backend**: FastAPI ile asenkron (`async def`) endpointler oluştur.
- [ ] **Validation**: Girdi verilerini `Pydantic` modelleriyle doğrula.
- [ ] **Concurrency**: CPU heavy işler için `Multiprocessing`, I/O heavy işler için `AsyncIO` kullan.

### Aşama 3: Testing & Code Quality
- [ ] **Linting**: `Ruff` veya `Flake8` ile kod statik analizini yap.
- [ ] **Testing**: `Pytest` ile kapsamlı unit ve entegrasyon testlerini yaz.

### Kontrol Noktaları
| Aşama | Doğrulama |
|-------|-----------|
| 1 | Kod PEP 8 standartlarına uygun mu? |
| 2 | Dependencies (`requirements.txt` veya `pyproject.toml`) güncel mi? |
| 3 | Global interpreter lock (GIL) sınırlamaları dikkate alındı mı? |
