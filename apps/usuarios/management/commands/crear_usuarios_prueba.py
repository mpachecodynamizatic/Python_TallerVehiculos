from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from apps.usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Crea usuarios de prueba con diferentes roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina usuarios de prueba existentes antes de crearlos',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Creando usuarios de prueba...'))

        # Si se especifica --reset, eliminar usuarios de prueba existentes
        if options['reset']:
            usuarios_prueba = ['admin', 'mecanico1', 'mecanico2', 'recepcion']
            Usuario.objects.filter(username__in=usuarios_prueba).delete()
            self.stdout.write(self.style.WARNING('Usuarios de prueba eliminados'))

        # ====================
        # USUARIO ADMINISTRADOR
        # ====================
        admin, created = Usuario.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@taller.com',
                'first_name': 'Administrador',
                'last_name': 'Principal',
                'rol': Usuario.Rol.ADMIN,
                'telefono': '+34600000001',
                'is_staff': True,
                'is_superuser': True,
                'activo': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('✓ Usuario "admin" creado'))
            self.stdout.write(self.style.WARNING('  Usuario: admin / Contraseña: admin123'))
        else:
            self.stdout.write(self.style.WARNING('  Usuario "admin" ya existe'))

        # Asignar al grupo Administradores
        try:
            admin_group = Group.objects.get(name='Administradores')
            admin.groups.add(admin_group)
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR('  ⚠ Grupo "Administradores" no existe. Ejecuta: python manage.py crear_grupos'))

        # ====================
        # USUARIO MECÁNICO 1
        # ====================
        mecanico1, created = Usuario.objects.get_or_create(
            username='mecanico1',
            defaults={
                'email': 'mecanico1@taller.com',
                'first_name': 'Juan',
                'last_name': 'Martínez',
                'rol': Usuario.Rol.MECANICO,
                'telefono': '+34600000002',
                'activo': True,
            }
        )
        if created:
            mecanico1.set_password('mecanico123')
            mecanico1.save()
            self.stdout.write(self.style.SUCCESS('✓ Usuario "mecanico1" creado'))
            self.stdout.write(self.style.WARNING('  Usuario: mecanico1 / Contraseña: mecanico123'))
        else:
            self.stdout.write(self.style.WARNING('  Usuario "mecanico1" ya existe'))

        # Asignar al grupo Mecánicos
        try:
            mecanico_group = Group.objects.get(name='Mecánicos')
            mecanico1.groups.add(mecanico_group)
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR('  ⚠ Grupo "Mecánicos" no existe. Ejecuta: python manage.py crear_grupos'))

        # ====================
        # USUARIO MECÁNICO 2
        # ====================
        mecanico2, created = Usuario.objects.get_or_create(
            username='mecanico2',
            defaults={
                'email': 'mecanico2@taller.com',
                'first_name': 'Carlos',
                'last_name': 'López',
                'rol': Usuario.Rol.MECANICO,
                'telefono': '+34600000003',
                'activo': True,
            }
        )
        if created:
            mecanico2.set_password('mecanico123')
            mecanico2.save()
            self.stdout.write(self.style.SUCCESS('✓ Usuario "mecanico2" creado'))
            self.stdout.write(self.style.WARNING('  Usuario: mecanico2 / Contraseña: mecanico123'))
        else:
            self.stdout.write(self.style.WARNING('  Usuario "mecanico2" ya existe'))

        # Asignar al grupo Mecánicos
        try:
            mecanico_group = Group.objects.get(name='Mecánicos')
            mecanico2.groups.add(mecanico_group)
        except Group.DoesNotExist:
            pass

        # ====================
        # USUARIO RECEPCIONISTA
        # ====================
        recepcion, created = Usuario.objects.get_or_create(
            username='recepcion',
            defaults={
                'email': 'recepcion@taller.com',
                'first_name': 'María',
                'last_name': 'García',
                'rol': Usuario.Rol.RECEPCIONISTA,
                'telefono': '+34600000004',
                'activo': True,
            }
        )
        if created:
            recepcion.set_password('recepcion123')
            recepcion.save()
            self.stdout.write(self.style.SUCCESS('✓ Usuario "recepcion" creado'))
            self.stdout.write(self.style.WARNING('  Usuario: recepcion / Contraseña: recepcion123'))
        else:
            self.stdout.write(self.style.WARNING('  Usuario "recepcion" ya existe'))

        # Asignar al grupo Recepcionistas
        try:
            recepcionista_group = Group.objects.get(name='Recepcionistas')
            recepcion.groups.add(recepcionista_group)
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR('  ⚠ Grupo "Recepcionistas" no existe. Ejecuta: python manage.py crear_grupos'))

        # ====================
        # RESUMEN
        # ====================
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Usuarios de prueba creados correctamente'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.WARNING('\nCredenciales de acceso:'))
        self.stdout.write(self.style.WARNING('  Admin:         admin / admin123'))
        self.stdout.write(self.style.WARNING('  Mecánico 1:    mecanico1 / mecanico123'))
        self.stdout.write(self.style.WARNING('  Mecánico 2:    mecanico2 / mecanico123'))
        self.stdout.write(self.style.WARNING('  Recepcionista: recepcion / recepcion123'))
        self.stdout.write(self.style.SUCCESS('\nAccede al sistema en: http://localhost:8000/accounts/login/\n'))
