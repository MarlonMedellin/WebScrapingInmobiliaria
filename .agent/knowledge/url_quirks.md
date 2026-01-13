# Portal URL Quirks & Pagination Patterns

This document catalogs non-standard URL behaviors discovered across real estate portals.

## 🔴 Critical: Double Ampersand Pagination

### Santa Fe Portal
**Verified Golden URL:** `https://arrendamientossantafe.com/propiedades/?page=X&&bussines_type=Arrendar`

**Quirks:** 
1. **Double Ampersand (`&&`):** Required separator.
2. **First Parameter:** `page=X` must remain the first parameter.
3. **Filter Order:** Adding extra filters (price, area) often breaks pagination unless strictly ordered. The minimal URL above is safest.

**Scraper Implementation:**
```python
# backend/scrapers/santafe.py
current_url = f"{self.base_url}/propiedades/?page={page_num}&&bussines_type=Arrendar"
# backend/scrapers/santafe.py
current_url = f"{self.base_url}/propiedades/?page={page_num}&&bussines_type=Arrendar"
```

### Protebienes Portal
**Verified Golden URL:** `https://www.inmobiliariaprotebienes.com/inmuebles/Arriendo/{page_num}`

**Quirks:**
1. **Domain:** Prefers `.com` over `.com.co`.
2. **Simple Path:** Direct path pagination `/inmuebles/Arriendo/X` works best.

---

## ⚠️ To Audit

### Conquistadores Portal
**Status:** Uses standard `&page=` - needs verification if working correctly

**File:** `backend/scrapers/conquistadores.py` line 36

---

## Standard Pagination Patterns

### Alberto Alvarez
- Uses JSON API, not URL pagination
- Property type iteration via `types` array

### Ayura
- Standard `&page=` parameter
- Works correctly

---

## Best Practices

1. **Always test pagination manually** before deep scraping
2. **Verify page 1 vs page 2** return different content
3. **Document quirks** in this file immediately upon discovery
4. **Add inline comments** in scraper code explaining non-standard behavior
