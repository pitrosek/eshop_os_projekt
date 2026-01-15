
Projekt doplněn: přidán Košík, SQLite databáze, Přihlášení uživatelů a Admin pro správu produktů.

Kroky, co jsem udělal (postupně):
1) Přidal jsem SQLite DB (flask_eshop_pretty/flask_eshop_pretty/eshop.db created via /initdb route).
2) Přidal jsem registraci a přihlášení (routes /register, /login, /logout).
3) Přidal jsem košík (session-based) a stránku /cart, a akce add/remove.
4) Přidal jsem jednoduché admin rozhraní /admin/products s CRUD pro produkty.
5) Přidal jsem checkout, který vytvoří objednávku v DB (/checkout).
6) Upravil jsem šablony: base, index, product, cart, login, register, admin.

Jak spustit:
- Nainstalujte závislosti z requirements.txt (Flask, Pillow).
- Spusťte app: python app.py
- Přejděte na http://localhost:5000 a navštivte /initdb pro inicializaci DB (vytvoří admin/admin).
- Přihlaste se (admin / admin) a spravujte produkty.

Poznámka: heslo admin je "admin" po inicializaci pomocí /initdb. Z bezpečnostních důvodů změňte v produkci.
