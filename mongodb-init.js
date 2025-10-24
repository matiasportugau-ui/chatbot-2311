// Script de inicialización de MongoDB para BMC
db = db.getSiblingDB('bmc_quotes');

// Crear colecciones principales
db.createCollection('quotes');
db.createCollection('sessions');
db.createCollection('context');
db.createCollection('products');
db.createCollection('analytics');
db.createCollection('conversaciones');
db.createCollection('sync_logs');
db.createCollection('reportes_diarios');

// Crear índices para optimizar consultas
db.quotes.createIndex({ "arg": 1 }, { unique: true });
db.quotes.createIndex({ "telefono": 1 });
db.quotes.createIndex({ "estado": 1 });
db.quotes.createIndex({ "fecha": 1 });
db.quotes.createIndex({ "origen": 1 });

db.sessions.createIndex({ "session_id": 1 }, { unique: true });
db.sessions.createIndex({ "user_phone": 1 });
db.sessions.createIndex({ "status": 1 });
db.sessions.createIndex({ "last_activity": 1 });

db.context.createIndex({ "session_id": 1 });
db.context.createIndex({ "user_phone": 1 });
db.context.createIndex({ "timestamp": 1 });

db.analytics.createIndex({ "timestamp": 1 });
db.analytics.createIndex({ "tipo": 1 });

db.conversaciones.createIndex({ "timestamp": 1 });
db.conversaciones.createIndex({ "telefono": 1 });
db.conversaciones.createIndex({ "tipo": 1 });

db.sync_logs.createIndex({ "timestamp": 1 });
db.reportes_diarios.createIndex({ "fecha": 1 });

// Insertar datos iniciales de productos BMC
db.products.insertMany([
  {
    id: "isodec",
    nombre: "Isodec EPS",
    categoria: "paneles",
    descripcion: "Panel aislante de poliestireno expandido",
    especificaciones: {
      grosor: [50, 100, 150, 200],
      colores: ["blanco", "gris", "azul"],
      dimensiones: {
        largo: [6000, 12000],
        ancho: [1000, 1200]
      },
      unidades: ["m2", "panel"]
    },
    precios: {
      base: 45,
      unidad: "m2",
      variaciones: {
        grosor: {
          50: 1.0,
          100: 1.2,
          150: 1.4,
          200: 1.6
        },
        color: {
          "blanco": 1.0,
          "gris": 1.1,
          "azul": 1.15
        }
      }
    },
    servicios: {
      instalacion: true,
      flete: true,
      accesorios: true
    },
    aplicaciones: ["galpones", "techos", "paredes", "aislamiento"],
    sinonimos: ["poliestireno", "eps", "placa aislante"],
    palabras_clave: ["isodec", "poliestireno", "aislante", "panel", "eps"]
  },
  {
    id: "isoroof",
    nombre: "Isoroof",
    categoria: "paneles",
    descripcion: "Panel aislante para techos",
    especificaciones: {
      grosor: [30, 50, 80],
      colores: ["blanco", "gris"],
      dimensiones: {
        largo: [6000, 12000],
        ancho: [1000, 1200]
      },
      unidades: ["m2", "panel"]
    },
    precios: {
      base: 65,
      unidad: "m2",
      variaciones: {
        grosor: {
          30: 1.0,
          50: 1.2,
          80: 1.4
        }
      }
    },
    servicios: {
      instalacion: true,
      flete: true,
      accesorios: true
    },
    aplicaciones: ["techos", "cubiertas", "aislamiento térmico"],
    sinonimos: ["techo aislante", "panel techo"],
    palabras_clave: ["isoroof", "techo", "cubierta", "aislante"]
  }
]);

// Insertar configuración inicial del sistema
db.analytics.insertOne({
  tipo: "configuracion_inicial",
  timestamp: new Date(),
  data: {
    version: "1.0.0",
    empresa: "BMC Construcciones",
    productos_configurados: 2,
    zonas_flete: {
      "montevideo": { flete_base: 50, multiplicador: 1.0 },
      "canelones": { flete_base: 80, multiplicador: 1.2 },
      "maldonado": { flete_base: 120, multiplicador: 1.5 },
      "rivera": { flete_base: 200, multiplicador: 2.0 },
      "artigas": { flete_base: 250, multiplicador: 2.5 }
    },
    servicios: {
      instalacion: { base: 100, por_m2: 15, minimo: 200 },
      flete: { base: 50, por_km: 2.5, minimo: 80 }
    }
  }
});

print("✅ Base de datos BMC inicializada correctamente");
print("📊 Colecciones creadas: quotes, sessions, context, products, analytics, conversaciones, sync_logs, reportes_diarios");
print("🔍 Índices creados para optimizar consultas");
print("🏗️ Productos BMC insertados: Isodec EPS, Isoroof");
print("⚙️ Configuración inicial del sistema establecida");
