from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Crea los grupos de usuarios y asigna permisos según el rol'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Creando grupos y asignando permisos...'))

        # ====================
        # GRUPO ADMINISTRADORES
        # ====================
        admin_group, created = Group.objects.get_or_create(name='Administradores')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Administradores" creado'))
        else:
            self.stdout.write(self.style.WARNING('  Grupo "Administradores" ya existe'))

        # Asignar TODOS los permisos a los administradores
        all_permissions = Permission.objects.all()
        admin_group.permissions.set(all_permissions)
        self.stdout.write(self.style.SUCCESS(f'  Asignados {all_permissions.count()} permisos'))

        # ====================
        # GRUPO MECÁNICOS
        # ====================
        mecanico_group, created = Group.objects.get_or_create(name='Mecánicos')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Mecánicos" creado'))
        else:
            self.stdout.write(self.style.WARNING('  Grupo "Mecánicos" ya existe'))

        # Permisos para mecánicos
        permisos_mecanico = [
            # Órdenes de trabajo
            'view_ordentrabajo', 'add_ordentrabajo', 'change_ordentrabajo',
            'view_lineatrabajo', 'add_lineatrabajo', 'change_lineatrabajo', 'delete_lineatrabajo',
            'view_linearepuesto', 'add_linearepuesto', 'change_linearepuesto', 'delete_linearepuesto',

            # Inventario de repuestos
            'view_repuesto', 'change_repuesto',
            'view_categoriarepuesto',
            'view_movimientoinventario', 'add_movimientoinventario',

            # Vehículos (solo lectura)
            'view_vehiculo',

            # Clientes (solo lectura)
            'view_cliente',

            # Citas (solo lectura)
            'view_cita',
        ]

        permisos_mecanico_objs = Permission.objects.filter(codename__in=permisos_mecanico)
        mecanico_group.permissions.set(permisos_mecanico_objs)
        self.stdout.write(self.style.SUCCESS(f'  Asignados {permisos_mecanico_objs.count()} permisos'))

        # ====================
        # GRUPO RECEPCIONISTAS
        # ====================
        recepcionista_group, created = Group.objects.get_or_create(name='Recepcionistas')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grupo "Recepcionistas" creado'))
        else:
            self.stdout.write(self.style.WARNING('  Grupo "Recepcionistas" ya existe'))

        # Permisos para recepcionistas
        permisos_recepcionista = [
            # Clientes (CRUD completo)
            'view_cliente', 'add_cliente', 'change_cliente', 'delete_cliente',

            # Vehículos (CRUD completo)
            'view_vehiculo', 'add_vehiculo', 'change_vehiculo', 'delete_vehiculo',

            # Citas (CRUD completo)
            'view_cita', 'add_cita', 'change_cita', 'delete_cita',

            # Órdenes de trabajo (solo lectura y creación)
            'view_ordentrabajo', 'add_ordentrabajo',

            # Facturas (ver y crear)
            'view_factura', 'add_factura',
            'view_presupuesto', 'add_presupuesto',

            # Pagos
            'view_pago', 'add_pago',

            # Repuestos (solo lectura)
            'view_repuesto',
            'view_categoriarepuesto',
        ]

        permisos_recepcionista_objs = Permission.objects.filter(codename__in=permisos_recepcionista)
        recepcionista_group.permissions.set(permisos_recepcionista_objs)
        self.stdout.write(self.style.SUCCESS(f'  Asignados {permisos_recepcionista_objs.count()} permisos'))

        # ====================
        # RESUMEN
        # ====================
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Grupos y permisos configurados correctamente'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.WARNING('\nPara asignar un usuario a un grupo, usa el admin de Django'))
        self.stdout.write(self.style.WARNING('o ejecuta el comando crear_usuarios_prueba\n'))
