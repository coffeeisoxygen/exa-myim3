app/
├── core/ # Komponen inti aplikasi
│ ├── config/ # Konfigurasi aplikasi
│ ├── database.py # Setup database
│ ├── events.py # Event system
│ ├── logging.py # Konfigurasi logging
│ └── state.py # State machine
├── devices/ # Domain: Device Management
│ ├── models.py # Model device
│ ├── repository.py # Database operations
│ ├── service.py # Business logic
│ ├── schemas.py # Pydantic schemas untuk API
│ ├── adb.py # ADB operations
│ └── routes.py # API endpoints
├── automation/ # Domain: Automation Flow
│ ├── models.py # Model automasi
│ ├── repository.py # Database operations
│ ├── service.py # Business logic
│ ├── flows/ # High-level flows
│ │ ├── login_flow.py
│ │ └── voucher_flow.py
│ ├── actions/ # Low-level actions
│ │ ├── input.py
│ │ ├── navigation.py
│ │ └── verification.py
│ └── ui/ # UI interactions
│ ├── elements.py # Resource IDs dan elemen
│ └── popup.py # Popup handling
├── transactions/ # Domain: Transactions
│ ├── models.py
│ ├── repository.py
│ ├── service.py
│ ├── schemas.py
│ └── routes.py
├── web/ # Web UI
│ ├── templates/
│ ├── static/
│ └── routes.py
├── app.py # FastAPI application entry point
└── main.py # Application entry point
