# 🛒 Flask E‑shop (OS projekt)

Moderní a přehledný **ukázkový e‑shop** vytvořený ve **Flasku** jako semestrální projekt do předmětu **Operační systémy**. Projekt demonstruje práci s webovou aplikací, databází, Dockerem i základními principy bezpečnosti a výkonu.

---

## ✨ Funkce

* 🛍️ **Katalog produktů**
* 🔎 Detail produktu
* 🧺 **Košík** (uložený v session)
* 👤 **Registrace a přihlášení uživatelů**
* 🧑‍💼 **Admin rozhraní** pro správu produktů (CRUD)
* 📦 **Checkout a objednávky**
* 🗄️ **SQLite databáze**
* 🐳 **Docker & docker‑compose**
* ⚙️ **Performance tester** (zátěžové testy)

---

## 🧰 Použité technologie

* **Python 3**
* **Flask**
* **SQLite**
* **HTML / Jinja2 / CSS**
* **Docker & Docker Compose**

---

## 📁 Struktura projektu

```
eshop_os_projekt-main/
├── app.py                  # Hlavní Flask aplikace
├── eshop.db                # SQLite databáze
├── templates/              # HTML šablony (Jinja2)
├── static/                 # Statické soubory (obrázky, CSS)
├── requirements.txt        # Python závislosti
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker Compose konfigurace
├── performance_tester.py   # Testování výkonu aplikace
└── README.md
```

---

## 🚀 Spuštění projektu

### 🔹 Lokálně (bez Dockeru)

1. Naklonujte repozitář:

   ```bash
   git clone https://github.com/uzivatel/eshop_os_projekt.git
   cd eshop_os_projekt-main
   ```

2. Nainstalujte závislosti:

   ```bash
   pip install -r requirements.txt
   ```

3. Spusťte aplikaci:

   ```bash
   python app.py
   ```

4. Otevřete v prohlížeči:

   ```
   http://localhost:5000
   ```

5. Inicializujte databázi:

   ```
   http://localhost:5000/initdb
   ```

---

### 🔹 Přihlášení admina

* **Uživatel:** `admin`
* **Heslo:** `admin`

> ⚠️ Heslo je pouze pro demonstrační účely – v produkci jej změňte.

Admin rozhraní:

```
/admin/products
```

---

## 🐳 Spuštění pomocí Dockeru

```bash
docker-compose up --build
```

Aplikace poběží na:

```
http://localhost:5000
```

---

## 📊 Testování výkonu

Součástí projektu je skript `performance_tester.py`, který umožňuje simulovat více požadavků na aplikaci a měřit odezvu serveru.

```bash
python performance_tester.py
```

---

## 🎯 Cíl projektu

* Procvičení práce s **Flaskem**
* Základy **webové architektury**
* Práce s **databází a session**
* Nasazení aplikace pomocí **Dockeru**
* Základy **bezpečnosti a výkonu**

---

## 📸 Náhled

*(Volitelné – lze doplnit screenshoty aplikace)*

---

## 📄 Licence

Projekt je určen pro **studijní účely**.

---

💡 *Pokud se ti projekt líbí, dej ⭐ na GitHubu!*
