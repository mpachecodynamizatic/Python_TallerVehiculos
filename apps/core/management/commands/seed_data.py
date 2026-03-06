"""
Comando Django para poblar la base de datos con datos de ejemplo.

Uso:
    python manage.py seed_data          # Crea datos de ejemplo
    python manage.py seed_data --flush  # Borra todo y vuelve a crear
"""
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de ejemplo para todas las tablas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Elimina todos los datos existentes antes de insertar los de ejemplo',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self._flush_data()

        self.stdout.write(self.style.MIGRATE_HEADING('=== Insertando datos de ejemplo ==='))

        with transaction.atomic():
            usuarios = self._crear_usuarios()
            categorias = self._crear_categorias_repuestos()
            repuestos = self._crear_repuestos(categorias)
            proveedores = self._crear_proveedores()
            clientes = self._crear_clientes()
            vehiculos = self._crear_vehiculos(clientes)
            citas = self._crear_citas(clientes, vehiculos, usuarios)
            ordenes = self._crear_ordenes_trabajo(clientes, vehiculos, citas, usuarios)
            self._crear_facturas(clientes, ordenes, usuarios)
            self._crear_ordenes_compra(proveedores, repuestos, usuarios)

        self.stdout.write(self.style.SUCCESS('\n✓ Datos de ejemplo creados correctamente.'))
        self.stdout.write('  Acceso al sistema:')
        self.stdout.write('    Admin       → usuario: admin      | contraseña: Admin1234!')
        self.stdout.write('    Recepción   → usuario: recepcion  | contraseña: Admin1234!')
        self.stdout.write('    Mecánicos   → usuario: mecanico1  | contraseña: Admin1234!')

    # ------------------------------------------------------------------
    # FLUSH
    # ------------------------------------------------------------------
    def _flush_data(self):
        from apps.facturacion.models import Factura, LineaFactura
        from apps.compras.models import OrdenCompra, LineaCompra
        from apps.ordenes.models import OrdenTrabajo, LineaRepuesto, LineaTrabajo
        from apps.citas.models import Cita
        from apps.vehiculos.models import Vehiculo
        from apps.clientes.models import Cliente
        from apps.inventario.models import Repuesto, CategoriaRepuesto
        from apps.compras.models import Proveedor
        from apps.usuarios.models import Usuario

        self.stdout.write(self.style.WARNING('Eliminando datos existentes...'))
        LineaFactura.objects.all().delete()
        Factura.objects.all().delete()
        LineaCompra.objects.all().delete()
        OrdenCompra.objects.all().delete()
        LineaRepuesto.objects.all().delete()
        LineaTrabajo.objects.all().delete()
        OrdenTrabajo.objects.all().delete()
        Cita.objects.all().delete()
        Vehiculo.objects.all().delete()
        Cliente.objects.all().delete()
        Repuesto.objects.all().delete()
        CategoriaRepuesto.objects.all().delete()
        Proveedor.objects.all().delete()
        Usuario.objects.filter(is_superuser=False).delete()
        self.stdout.write('  Tablas vaciadas.')

    # ------------------------------------------------------------------
    # USUARIOS
    # ------------------------------------------------------------------
    def _crear_usuarios(self):
        from apps.usuarios.models import Usuario

        self.stdout.write('  Creando usuarios...')

        password = make_password('Admin1234!')

        datos = [
            {
                'username': 'admin',
                'email': 'admin@taller.es',
                'first_name': 'Carlos',
                'last_name': 'García López',
                'rol': Usuario.Rol.ADMIN,
                'telefono': '600111222',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'recepcion',
                'email': 'recepcion@taller.es',
                'first_name': 'Laura',
                'last_name': 'Martínez Ruiz',
                'rol': Usuario.Rol.RECEPCIONISTA,
                'telefono': '600222333',
            },
            {
                'username': 'recep2',
                'email': 'recep2@taller.es',
                'first_name': 'Ana',
                'last_name': 'Sánchez Pérez',
                'rol': Usuario.Rol.RECEPCIONISTA,
                'telefono': '600222444',
            },
            {
                'username': 'mecanico1',
                'email': 'mecanico1@taller.es',
                'first_name': 'Miguel',
                'last_name': 'Torres Fernández',
                'rol': Usuario.Rol.MECANICO,
                'telefono': '600333444',
            },
            {
                'username': 'mecanico2',
                'email': 'mecanico2@taller.es',
                'first_name': 'José',
                'last_name': 'Rodríguez Navarro',
                'rol': Usuario.Rol.MECANICO,
                'telefono': '600333555',
            },
            {
                'username': 'mecanico3',
                'email': 'mecanico3@taller.es',
                'first_name': 'Pedro',
                'last_name': 'Gómez Castro',
                'rol': Usuario.Rol.MECANICO,
                'telefono': '600333666',
            },
        ]

        usuarios = {}
        for d in datos:
            obj, creado = Usuario.objects.get_or_create(
                username=d['username'],
                defaults={**d, 'password': password, 'activo': True},
            )
            if creado:
                self.stdout.write(f'    + {obj.username} ({obj.get_rol_display()})')
            usuarios[d['username']] = obj

        return usuarios

    # ------------------------------------------------------------------
    # INVENTARIO – Categorías
    # ------------------------------------------------------------------
    def _crear_categorias_repuestos(self):
        from apps.inventario.models import CategoriaRepuesto

        self.stdout.write('  Creando categorías de repuestos...')

        datos = [
            ('Filtros',        'FILT', 'Filtros de aceite, aire, polen y combustible'),
            ('Frenos',         'FREN', 'Pastillas, discos, latiguillos y líquido de frenos'),
            ('Motor',          'MOTO', 'Componentes internos del motor'),
            ('Suspensión',     'SUSP', 'Amortiguadores, muelles y rótulas'),
            ('Electricidad',   'ELEC', 'Baterías, alternadores, bombillas y fusibles'),
            ('Neumáticos',     'NEUM', 'Neumáticos y accesorios de rueda'),
            ('Aceites',        'ACEI', 'Aceites de motor, caja y dirección'),
            ('Carrocería',     'CARR', 'Piezas de carrocería y luna'),
            ('Transmisión',    'TRAN', 'Embrague, caja de cambios y cardán'),
            ('Refrigeración',  'REFR', 'Radiador, termostato y líquido refrigerante'),
        ]

        categorias = {}
        for nombre, codigo, desc in datos:
            obj, creado = CategoriaRepuesto.objects.get_or_create(
                codigo=codigo,
                defaults={'nombre': nombre, 'descripcion': desc, 'activo': True},
            )
            if creado:
                self.stdout.write(f'    + {obj.nombre}')
            categorias[codigo] = obj

        return categorias

    # ------------------------------------------------------------------
    # INVENTARIO – Repuestos
    # ------------------------------------------------------------------
    def _crear_repuestos(self, categorias):
        from apps.inventario.models import Repuesto

        self.stdout.write('  Creando repuestos...')

        datos = [
            # codigo, nombre, cat_code, precio_compra, precio_venta, stock, stock_min, marca, ubicacion
            ('REP-001', 'Filtro de aceite Mann W713/75',     'FILT', '4.50',  '9.90',  '25', '5',  'Mann Filter',  'A1-01'),
            ('REP-002', 'Filtro de aire Bosch S0080',        'FILT', '7.20',  '14.50', '18', '4',  'Bosch',        'A1-02'),
            ('REP-003', 'Filtro de habitáculo Purflux',      'FILT', '5.80',  '11.90', '20', '4',  'Purflux',      'A1-03'),
            ('REP-004', 'Filtro de combustible WIX',         'FILT', '8.40',  '16.90', '12', '3',  'WIX Filters',  'A1-04'),
            ('REP-005', 'Pastillas freno delan. Brembo',     'FREN', '18.00', '36.00', '15', '4',  'Brembo',       'B2-01'),
            ('REP-006', 'Pastillas freno trasero TRW',       'FREN', '14.50', '28.90', '15', '4',  'TRW',          'B2-02'),
            ('REP-007', 'Disco freno delantero Zimmermann',  'FREN', '22.00', '45.00', '10', '3',  'Zimmermann',   'B2-03'),
            ('REP-008', 'Líquido de frenos DOT4 1L',         'FREN', '4.20',  '8.90',  '30', '8',  'ATE',          'B2-04'),
            ('REP-009', 'Correa distribución Gates',         'MOTO', '28.00', '56.00', '8',  '2',  'Gates',        'C3-01'),
            ('REP-010', 'Kit distribución completo INA',     'MOTO', '65.00', '130.00','6',  '2',  'INA',          'C3-02'),
            ('REP-011', 'Bujía NGK Iridium',                 'MOTO', '7.50',  '15.00', '40', '10', 'NGK',          'C3-03'),
            ('REP-012', 'Sensor oxígeno Bosch',              'MOTO', '35.00', '70.00', '5',  '2',  'Bosch',        'C3-04'),
            ('REP-013', 'Amortiguador delantero Monroe',     'SUSP', '45.00', '89.00', '6',  '2',  'Monroe',       'D4-01'),
            ('REP-014', 'Amortiguador trasero Bilstein',     'SUSP', '52.00', '105.00','6',  '2',  'Bilstein',     'D4-02'),
            ('REP-015', 'Rótula dirección Meyle',            'SUSP', '18.00', '36.00', '8',  '2',  'Meyle',        'D4-03'),
            ('REP-016', 'Batería 60Ah Varta',                'ELEC', '55.00', '110.00','4',  '2',  'Varta',        'E5-01'),
            ('REP-017', 'Batería 74Ah Bosch',                'ELEC', '68.00', '135.00','3',  '2',  'Bosch',        'E5-02'),
            ('REP-018', 'Bombilla H4 Osram',                 'ELEC', '6.50',  '12.90', '30', '6',  'Osram',        'E5-03'),
            ('REP-019', 'Alternador Valeo',                  'ELEC', '95.00', '190.00','2',  '1',  'Valeo',        'E5-04'),
            ('REP-020', 'Aceite Castrol 5W30 5L',            'ACEI', '22.00', '42.00', '20', '5',  'Castrol',      'G7-01'),
            ('REP-021', 'Aceite Mobil 1 5W40 5L',            'ACEI', '25.00', '49.00', '18', '5',  'Mobil',        'G7-02'),
            ('REP-022', 'Aceite caja cambios Fuchs 75W90',   'ACEI', '12.00', '24.00', '10', '3',  'Fuchs',        'G7-03'),
            ('REP-023', 'Embrague Kit LUK 3 piezas',         'TRAN', '120.00','240.00','3',  '1',  'LUK',          'I9-01'),
            ('REP-024', 'Termostato Wahler',                 'REFR', '14.00', '28.00', '8',  '2',  'Wahler',       'J10-01'),
            ('REP-025', 'Anticongelante Prestone 5L',        'REFR', '9.00',  '18.00', '15', '4',  'Prestone',     'J10-02'),
        ]

        repuestos = {}
        for codigo, nombre, cat_code, pc, pv, stock, smin, marca, ubic in datos:
            obj, creado = Repuesto.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'categoria': categorias[cat_code],
                    'precio_compra': Decimal(pc),
                    'precio_venta': Decimal(pv),
                    'stock_actual': Decimal(stock),
                    'stock_minimo': Decimal(smin),
                    'marca': marca,
                    'ubicacion_almacen': ubic,
                    'activo': True,
                },
            )
            if creado:
                self.stdout.write(f'    + {obj.nombre}')
            repuestos[codigo] = obj

        return repuestos

    # ------------------------------------------------------------------
    # COMPRAS – Proveedores
    # ------------------------------------------------------------------
    def _crear_proveedores(self):
        from apps.compras.models import Proveedor

        self.stdout.write('  Creando proveedores...')

        datos = [
            {
                'nombre': 'Distribuciones AutoParts SL',
                'cif': 'B12345678',
                'email': 'ventas@autoparts.es',
                'telefono': '912345678',
                'direccion': 'Calle Industrial, 45',
                'ciudad': 'Madrid',
                'codigo_postal': '28001',
                'contacto_principal': 'Roberto Sanz',
            },
            {
                'nombre': 'Recambios El Norte SA',
                'cif': 'A87654321',
                'email': 'pedidos@elnorte.es',
                'telefono': '943111222',
                'direccion': 'Polígono Las Eras, 12',
                'ciudad': 'San Sebastián',
                'codigo_postal': '20001',
                'contacto_principal': 'Amaia Zubeldia',
            },
            {
                'nombre': 'TecniRecambios SL',
                'cif': 'B55544433',
                'email': 'info@tecnirecambios.com',
                'telefono': '934567890',
                'direccion': 'Avda. de la Industria, 78',
                'ciudad': 'Barcelona',
                'codigo_postal': '08001',
                'contacto_principal': 'Jordi Puig',
            },
            {
                'nombre': 'Lubricantes del Sur SL',
                'cif': 'B99988877',
                'email': 'comercial@lubsur.es',
                'telefono': '954321098',
                'direccion': 'Calle Acerinox, 3',
                'ciudad': 'Sevilla',
                'codigo_postal': '41001',
                'contacto_principal': 'Manuel Jiménez',
            },
        ]

        proveedores = {}
        for d in datos:
            obj, creado = Proveedor.objects.get_or_create(
                cif=d['cif'],
                defaults={**d, 'activo': True},
            )
            if creado:
                self.stdout.write(f'    + {obj.nombre}')
            proveedores[d['cif']] = obj

        return proveedores

    # ------------------------------------------------------------------
    # CLIENTES
    # ------------------------------------------------------------------
    def _crear_clientes(self):
        from apps.clientes.models import Cliente

        self.stdout.write('  Creando clientes...')

        datos = [
            {
                'nombre': 'Antonio', 'apellidos': 'García Martínez',
                'dni': '12345678A', 'email': 'antonio.garcia@email.com',
                'telefono': '611100001', 'ciudad': 'Madrid', 'codigo_postal': '28001',
                'direccion': 'Calle Mayor, 10',
            },
            {
                'nombre': 'María', 'apellidos': 'López Fernández',
                'dni': '23456789B', 'email': 'maria.lopez@email.com',
                'telefono': '611100002', 'ciudad': 'Getafe', 'codigo_postal': '28901',
                'direccion': 'Calle Cervantes, 5',
            },
            {
                'nombre': 'Carlos', 'apellidos': 'Rodríguez Sánchez',
                'dni': '34567890C', 'email': 'carlos.rodriguez@email.com',
                'telefono': '611100003', 'ciudad': 'Alcorcón', 'codigo_postal': '28921',
                'direccion': 'Avda. de las Rosas, 22',
            },
            {
                'nombre': 'Laura', 'apellidos': 'Martínez Torres',
                'dni': '45678901D', 'email': 'laura.martinez@email.com',
                'telefono': '611100004', 'ciudad': 'Leganés', 'codigo_postal': '28911',
                'direccion': 'Calle del Olmo, 8',
            },
            {
                'nombre': 'Pedro', 'apellidos': 'Sánchez Gómez',
                'dni': '56789012E', 'email': 'pedro.sanchez@email.com',
                'telefono': '611100005', 'ciudad': 'Fuenlabrada', 'codigo_postal': '28942',
                'direccion': 'Plaza de España, 3',
            },
            {
                'nombre': 'Isabel', 'apellidos': 'Fernández Castro',
                'dni': '67890123F', 'email': 'isabel.fernandez@email.com',
                'telefono': '611100006', 'ciudad': 'Madrid', 'codigo_postal': '28002',
                'direccion': 'Calle Atocha, 45',
            },
            {
                'nombre': 'Fernando', 'apellidos': 'Torres Navarro',
                'dni': '78901234G', 'email': 'fernando.torres@email.com',
                'telefono': '611100007', 'ciudad': 'Móstoles', 'codigo_postal': '28931',
                'direccion': 'Calle Real, 17',
            },
            {
                'nombre': 'Pilar', 'apellidos': 'Gómez Ruiz',
                'dni': '89012345H', 'email': 'pilar.gomez@email.com',
                'telefono': '611100008', 'ciudad': 'Parla', 'codigo_postal': '28981',
                'direccion': 'Calle Pinos, 2',
            },
        ]

        clientes = []
        for d in datos:
            obj, creado = Cliente.objects.get_or_create(
                dni=d['dni'],
                defaults={**d, 'activo': True},
            )
            if creado:
                self.stdout.write(f'    + {obj.nombre} {obj.apellidos}')
            clientes.append(obj)

        return clientes

    # ------------------------------------------------------------------
    # VEHÍCULOS
    # ------------------------------------------------------------------
    def _crear_vehiculos(self, clientes):
        from apps.vehiculos.models import Vehiculo

        self.stdout.write('  Creando vehículos...')

        datos = [
            # cliente_idx, marca, modelo, anio, matricula, bastidor, color, combustible, km
            (0, 'Toyota',     'Corolla',    2019, '1234ABC', 'JT2BF22K1W0021234', 'Blanco',  'GASOLINA', 45000),
            (0, 'Toyota',     'Yaris',      2021, '5678DEF', 'JTDKW923400021235', 'Rojo',    'HIBRIDO',  18000),
            (1, 'Volkswagen', 'Golf',       2018, '9ABC012', 'WVWZZZ1KZAW012345', 'Gris',    'DIESEL',   72000),
            (2, 'Ford',       'Focus',      2020, '3GHI456', '1FAHP3FN7AW001234', 'Azul',    'GASOLINA', 35000),
            (2, 'Ford',       'Transit',    2017, '7JKL890', 'WF0XXXTTGXCA12345', 'Blanco',  'DIESEL',   120000),
            (3, 'Seat',       'León',       2022, '1MNO234', 'VSSZZZ5FZDH012345', 'Negro',   'GASOLINA', 12000),
            (4, 'Renault',    'Clio',       2016, '5PQR678', 'VF1BB1J0H25012345', 'Plata',   'DIESEL',   95000),
            (5, 'BMW',        'Serie 3',    2021, '9STU012', 'WBA3A5C51DJ012345', 'Negro',   'GASOLINA', 22000),
            (6, 'Honda',      'Civic',      2019, '2VWX345', '2HGFB2F52AH012345', 'Azul',   'GASOLINA', 48000),
            (7, 'Peugeot',    '308',        2020, '6YZA789', 'VF3LBHZMZJS012345', 'Blanco',  'DIESEL',   31000),
        ]

        vehiculos = []
        for cli_idx, marca, modelo, anio, matricula, bastidor, color, comb, km in datos:
            obj, creado = Vehiculo.objects.get_or_create(
                matricula=matricula,
                defaults={
                    'cliente': clientes[cli_idx],
                    'marca': marca,
                    'modelo': modelo,
                    'anio': anio,
                    'bastidor': bastidor,
                    'color': color,
                    'tipo_combustible': comb,
                    'kilometraje': km,
                },
            )
            if creado:
                self.stdout.write(f'    + {obj.marca} {obj.modelo} ({obj.matricula})')
            vehiculos.append(obj)

        return vehiculos

    # ------------------------------------------------------------------
    # CITAS
    # ------------------------------------------------------------------
    def _crear_citas(self, clientes, vehiculos, usuarios):
        from apps.citas.models import Cita

        self.stdout.write('  Creando citas...')

        mecanico1 = usuarios.get('mecanico1')
        mecanico2 = usuarios.get('mecanico2')
        recepcion = usuarios.get('recepcion')

        hoy = timezone.now()

        datos = [
            # cliente_idx, vehiculo_idx, tipo, estado, dias_offset, duracion, desc, mecanico
            (0, 0, 'ACEI', 'COMP', -15, 60,  'Cambio de aceite y filtros', mecanico1),
            (1, 2, 'FREN', 'COMP', -10, 90,  'Revisión y cambio pastillas de freno delanteras', mecanico1),
            (2, 3, 'MANT', 'COMP', -8,  120, 'Revisión general 30.000 km', mecanico2),
            (3, 5, 'REVI', 'CONF', -3,  60,  'Revisión pre-ITV', mecanico1),
            (4, 6, 'SUSP', 'CONF', -1,  150, 'Ruido en la suspensión delantera', mecanico2),
            (5, 7, 'ACEI', 'PEND', 2,   60,  'Cambio de aceite 5W30', mecanico1),
            (6, 8, 'DIAG', 'PEND', 3,   90,  'Testigo motor encendido, diagnóstico OBD', mecanico2),
            (7, 9, 'ITV',  'PEND', 5,   30,  'Puesta a punto previa a ITV', mecanico1),
            (0, 1, 'NEUM', 'PEND', 7,   60,  'Cambio neumáticos temporada', mecanico2),
            (2, 4, 'REPA', 'CANC', -20, 180, 'Reparación transmisión (cancelada por cliente)', None),
        ]

        nuevas = []
        for cli_idx, veh_idx, tipo, estado, dias, dur, desc, mec in datos:
            fecha = hoy + timezone.timedelta(days=dias)
            fecha = fecha.replace(hour=9 + (len(nuevas) % 8), minute=0, second=0, microsecond=0)

            if Cita.objects.filter(
                cliente=clientes[cli_idx],
                vehiculo=vehiculos[veh_idx],
                descripcion=desc,
            ).exists():
                continue

            nuevas.append(Cita(
                cliente=clientes[cli_idx],
                vehiculo=vehiculos[veh_idx],
                fecha_hora=fecha,
                tipo_servicio=tipo,
                estado=estado,
                duracion_estimada=dur,
                descripcion=desc,
                mecanico_asignado=mec,
                usuario_creacion=recepcion,
            ))

        # bulk_create omite el save() del modelo (elude full_clean)
        creadas = Cita.objects.bulk_create(nuevas, ignore_conflicts=True)
        for c in creadas:
            self.stdout.write(f'    + Cita {c.pk}: {c.get_tipo_servicio_display()} – {c.get_estado_display()}')

        return list(Cita.objects.order_by('pk')[:len(datos)])

    # ------------------------------------------------------------------
    # ÓRDENES DE TRABAJO
    # ------------------------------------------------------------------
    def _crear_ordenes_trabajo(self, clientes, vehiculos, citas, usuarios):
        from apps.ordenes.models import OrdenTrabajo, LineaRepuesto, LineaTrabajo

        self.stdout.write('  Creando órdenes de trabajo...')

        mecanico1 = usuarios.get('mecanico1')
        mecanico2 = usuarios.get('mecanico2')

        datos_orden = [
            # cli_idx, veh_idx, cita_idx, estado,  prioridad, km,    desc_problema,         diagnostico,             tiempo_est, tiempo_real
            (0, 0, 0, 'COMP', 'NORM', 45500, 'Cambio de aceite rutinario', 'Motor correcto, aceite deteriorado', Decimal('1.0'), Decimal('0.8')),
            (1, 2, 1, 'COMP', 'NORM', 72100, 'Frenos chirrían al frenar',  'Pastillas delantera gastadas',       Decimal('1.5'), Decimal('1.2')),
            (2, 3, 2, 'COMP', 'ALTA', 35200, 'Revisión 30.000 km completa','Distribución OK, filtros cambiados', Decimal('2.0'), Decimal('2.5')),
            (3, 5, 3, 'PROC', 'NORM', 12100, 'Revisión pre-ITV solicitada','Luces correctas, leve holgura rótula', Decimal('1.0'), None),
            (4, 6, 4, 'ABIE', 'ALTA', 95200, 'Ruido metálico al girar',    '',                                   Decimal('2.0'), None),
        ]

        ordenes = []
        for cli_idx, veh_idx, cita_idx, estado, prioridad, km, desc, diag, t_est, t_real in datos_orden:
            cita = citas[cita_idx] if estado in ('COMP', 'PROC') else None

            # Usamos create porque numero_orden se genera automáticamente
            if OrdenTrabajo.objects.filter(
                cliente=clientes[cli_idx],
                vehiculo=vehiculos[veh_idx],
                descripcion_problema=desc,
            ).exists():
                orden = OrdenTrabajo.objects.get(
                    cliente=clientes[cli_idx],
                    vehiculo=vehiculos[veh_idx],
                    descripcion_problema=desc,
                )
            else:
                orden = OrdenTrabajo.objects.create(
                    cita=cita,
                    cliente=clientes[cli_idx],
                    vehiculo=vehiculos[veh_idx],
                    mecanico_asignado=mecanico1 if cli_idx % 2 == 0 else mecanico2,
                    estado=estado,
                    prioridad=prioridad,
                    kilometros_ingreso=km,
                    descripcion_problema=desc,
                    diagnostico=diag,
                    tiempo_estimado=t_est,
                    tiempo_real=t_real,
                )
                self.stdout.write(f'    + {orden.numero_orden} – {orden.get_estado_display()}')

            ordenes.append(orden)

        # Líneas de repuestos en las órdenes
        self.stdout.write('  Creando líneas de repuestos y trabajo...')
        lineas_repuesto = [
            # orden_idx, descripcion, cantidad, precio_unitario, descuento
            (0, 'Filtro de aceite Mann W713/75',         Decimal('1'), Decimal('9.90'),  Decimal('0')),
            (0, 'Aceite Castrol 5W30 5L',                Decimal('1'), Decimal('42.00'), Decimal('0')),
            (1, 'Pastillas freno delanteras Brembo x2',  Decimal('2'), Decimal('36.00'), Decimal('5')),
            (1, 'Líquido frenos DOT4 1L',                Decimal('1'), Decimal('8.90'),  Decimal('0')),
            (2, 'Filtro de aceite',                      Decimal('1'), Decimal('9.90'),  Decimal('0')),
            (2, 'Filtro de aire Bosch S0080',            Decimal('1'), Decimal('14.50'), Decimal('0')),
            (2, 'Filtro habitáculo Purflux',             Decimal('1'), Decimal('11.90'), Decimal('0')),
            (2, 'Aceite Mobil 1 5W40 5L',               Decimal('1'), Decimal('49.00'), Decimal('10')),
            (3, 'Rótula dirección Meyle',                Decimal('1'), Decimal('36.00'), Decimal('0')),
        ]

        for orden_idx, desc, cantidad, precio, descuento in lineas_repuesto:
            if not LineaRepuesto.objects.filter(
                orden=ordenes[orden_idx], descripcion=desc
            ).exists():
                LineaRepuesto.objects.create(
                    orden=ordenes[orden_idx],
                    descripcion=desc,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    descuento=descuento,
                )

        lineas_trabajo = [
            # orden_idx, descripcion, horas, precio_hora
            (0, 'Cambio aceite y filtros',            Decimal('0.5'), Decimal('45.00')),
            (1, 'Cambio pastillas freno delantera',   Decimal('1.0'), Decimal('45.00')),
            (1, 'Sangrado frenos y relleno líquido',  Decimal('0.5'), Decimal('45.00')),
            (2, 'Revisión 30.000 km completa',        Decimal('2.0'), Decimal('45.00')),
            (3, 'Diagnóstico y revisión pre-ITV',     Decimal('0.5'), Decimal('45.00')),
            (4, 'Diagnóstico suspensión delantera',   Decimal('1.0'), Decimal('45.00')),
        ]

        for orden_idx, desc, horas, precio_hora in lineas_trabajo:
            if not LineaTrabajo.objects.filter(
                orden=ordenes[orden_idx], descripcion=desc
            ).exists():
                LineaTrabajo.objects.create(
                    orden=ordenes[orden_idx],
                    descripcion=desc,
                    horas=horas,
                    precio_hora=precio_hora,
                )

        return ordenes

    # ------------------------------------------------------------------
    # FACTURACIÓN
    # ------------------------------------------------------------------
    def _crear_facturas(self, clientes, ordenes, usuarios):
        from apps.facturacion.models import Factura, LineaFactura

        self.stdout.write('  Creando facturas...')

        creador = usuarios.get('recepcion') or usuarios.get('admin')
        hoy = timezone.now().date()

        datos = [
            # cli_idx, orden_idx, estado, metodo_pago, dias_venc, dias_pago_offset
            (0, 0, 'PAGA', 'EFEC', 30, -14),
            (1, 1, 'PAGA', 'TARJ', 30, -9),
            (2, 2, 'PAGA', 'TRAN', 30, -7),
            (3, 3, 'PEND', '',     30, None),
            (4, 4, 'PEND', '',     30, None),
            # Factura sin orden asociada
            (5, None, 'PAGA', 'BIZU', 30, -5),
            (6, None, 'PARC', 'EFEC', 30, None),
            (7, None, 'VENC', '',     -5, None),
        ]

        facturas = []
        for d in datos:
            cli_idx, ord_idx, estado, metodo, dias_venc, dias_pago = d
            orden = ordenes[ord_idx] if ord_idx is not None else None
            fecha_emision = hoy - timezone.timedelta(days=20)
            fecha_vencimiento = fecha_emision + timezone.timedelta(days=dias_venc)
            fecha_pago = (hoy + timezone.timedelta(days=dias_pago)) if dias_pago else None

            if Factura.objects.filter(cliente=clientes[cli_idx], orden_trabajo=orden).exists():
                factura = Factura.objects.filter(cliente=clientes[cli_idx], orden_trabajo=orden).first()
            else:
                factura = Factura.objects.create(
                    cliente=clientes[cli_idx],
                    orden_trabajo=orden,
                    fecha_emision=fecha_emision,
                    fecha_vencimiento=fecha_vencimiento,
                    estado=estado,
                    metodo_pago=metodo,
                    fecha_pago=fecha_pago,
                    usuario_creador=creador,
                )
                # Líneas de factura
                self._crear_lineas_factura(factura, cli_idx)
                factura.calcular_totales()
                if estado == 'PAGA':
                    factura.monto_pagado = factura.total
                elif estado == 'PARC':
                    factura.monto_pagado = factura.total / 2
                factura.save()
                self.stdout.write(f'    + {factura.numero_factura} – {factura.get_estado_display()} ({factura.total}€)')

            facturas.append(factura)

        return facturas

    def _crear_lineas_factura(self, factura, cli_idx):
        from apps.facturacion.models import LineaFactura

        plantillas = [
            [
                ('Cambio de aceite 5W30 5L + filtro', Decimal('1'), Decimal('52.50'), Decimal('0'), Decimal('21')),
                ('Mano de obra cambio de aceite', Decimal('1'), Decimal('25.00'), Decimal('0'), Decimal('21')),
            ],
            [
                ('Kit pastillas freno delanteras', Decimal('2'), Decimal('36.00'), Decimal('5'), Decimal('21')),
                ('Líquido frenos DOT4', Decimal('1'), Decimal('8.90'), Decimal('0'), Decimal('21')),
                ('Mano de obra frenos', Decimal('1'), Decimal('40.00'), Decimal('0'), Decimal('21')),
            ],
            [
                ('Revisión 30.000 km – filtros y aceite', Decimal('1'), Decimal('85.00'), Decimal('10'), Decimal('21')),
                ('Bujías NGK Iridium x4', Decimal('4'), Decimal('15.00'), Decimal('0'), Decimal('21')),
                ('Mano de obra revisión completa', Decimal('1'), Decimal('60.00'), Decimal('0'), Decimal('21')),
            ],
            [
                ('Revisión pre-ITV', Decimal('1'), Decimal('35.00'), Decimal('0'), Decimal('21')),
            ],
            [
                ('Diagnóstico suspensión', Decimal('1'), Decimal('45.00'), Decimal('0'), Decimal('21')),
            ],
            [
                ('Servicio de lavado y encerado', Decimal('1'), Decimal('30.00'), Decimal('0'), Decimal('21')),
                ('Revisión niveles y presión neumáticos', Decimal('1'), Decimal('15.00'), Decimal('0'), Decimal('21')),
            ],
            [
                ('Cambio neumáticos x2 + equilibrado', Decimal('2'), Decimal('65.00'), Decimal('5'), Decimal('21')),
            ],
            [
                ('Diagnóstico motor – OBD avanzado', Decimal('1'), Decimal('55.00'), Decimal('0'), Decimal('21')),
            ],
        ]

        idx = cli_idx % len(plantillas)
        for desc, cant, precio, descuento, iva in plantillas[idx]:
            LineaFactura.objects.create(
                factura=factura,
                descripcion=desc,
                cantidad=cant,
                precio_unitario=precio,
                descuento=descuento,
                iva=iva,
            )

    # ------------------------------------------------------------------
    # ÓRDENES DE COMPRA
    # ------------------------------------------------------------------
    def _crear_ordenes_compra(self, proveedores, repuestos, usuarios):
        from apps.compras.models import OrdenCompra, LineaCompra

        self.stdout.write('  Creando órdenes de compra...')

        provs = list(proveedores.values())
        hoy = timezone.now().date()

        datos = [
            # prov_idx, estado, dias_offset, lineas [(rep_codigo, cant, precio, desc)]
            (0, 'RECV', -30, [
                ('REP-001', Decimal('20'), Decimal('4.50'), Decimal('5')),
                ('REP-002', Decimal('15'), Decimal('7.20'), Decimal('5')),
                ('REP-020', Decimal('10'), Decimal('22.00'), Decimal('3')),
            ]),
            (1, 'RECP', -15, [
                ('REP-005', Decimal('10'), Decimal('18.00'), Decimal('0')),
                ('REP-006', Decimal('10'), Decimal('14.50'), Decimal('0')),
                ('REP-007', Decimal('6'),  Decimal('22.00'), Decimal('2')),
            ]),
            (2, 'ENVI', -5, [
                ('REP-009', Decimal('5'),  Decimal('28.00'), Decimal('0')),
                ('REP-010', Decimal('4'),  Decimal('65.00'), Decimal('0')),
                ('REP-011', Decimal('20'), Decimal('7.50'),  Decimal('0')),
            ]),
            (3, 'BORR', 0, [
                ('REP-021', Decimal('8'),  Decimal('25.00'), Decimal('0')),
                ('REP-022', Decimal('6'),  Decimal('12.00'), Decimal('0')),
            ]),
            (0, 'CANC', -45, [
                ('REP-016', Decimal('4'),  Decimal('55.00'), Decimal('0')),
                ('REP-017', Decimal('3'),  Decimal('68.00'), Decimal('0')),
            ]),
        ]

        for prov_idx, estado, dias, lineas_data in datos:
            fecha = hoy + timezone.timedelta(days=dias)

            if OrdenCompra.objects.filter(
                proveedor=provs[prov_idx], fecha_orden=fecha
            ).exists():
                continue

            orden = OrdenCompra.objects.create(
                proveedor=provs[prov_idx],
                estado=estado,
                fecha_orden=fecha,
            )

            for rep_codigo, cant, precio, desc in lineas_data:
                rep = repuestos.get(rep_codigo)
                if rep:
                    LineaCompra.objects.create(
                        orden_compra=orden,
                        repuesto=rep,
                        cantidad_solicitada=cant,
                        precio_unitario=precio,
                        descuento=desc,
                    )

            # Calcular totales si el modelo lo permite
            if hasattr(orden, 'calcular_totales'):
                orden.calcular_totales()

            self.stdout.write(f'    + {orden.numero_orden} – {orden.get_estado_display()} ({orden.proveedor})')
