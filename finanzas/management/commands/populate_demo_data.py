import random
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from finanzas.models import Categoria, Transaccion, Presupuesto

class Command(BaseCommand):
    help = 'Populates the database with demo data for a specific user'

    def add_arguments(self, parser):
        parser.add_argument('--user_id', type=int, help='The ID of the user to populate data for')

    def handle(self, *args, **options):
        user_id = options['user_id']
        if not user_id:
            self.stdout.write(self.style.ERROR('User ID is required'))
            return

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with ID {user_id} does not exist'))
            return

        self.stdout.write(f'Generating demo data for user: {user.username}')

        # 1. Create Categories
        categorias_data = [
            ('Salario', 'ingreso'),
            ('Freelance', 'ingreso'),
            ('Inversiones', 'ingreso'),
            ('Alimentación', 'gasto'),
            ('Transporte', 'gasto'),
            ('Vivienda', 'gasto'),
            ('Entretenimiento', 'gasto'),
            ('Salud', 'gasto'),
            ('Educación', 'gasto'),
            ('Servicios', 'gasto'),
        ]

        categorias = {}
        for nombre, tipo in categorias_data:
            cat, created = Categoria.objects.get_or_create(
                usuario=user,
                nombre=nombre,
                defaults={'tipo': tipo}
            )
            categorias[nombre] = cat
            if created:
                self.stdout.write(f'Created category: {nombre}')

        # 2. Create Transactions (Last 3 months)
        today = timezone.now()
        start_date = today - timedelta(days=90)
        
        # Sample descriptions
        descriptions = {
            'Salario': ['Sueldo mensual', 'Bono'],
            'Freelance': ['Proyecto web', 'Consultoría'],
            'Inversiones': ['Dividendos', 'Intereses'],
            'Alimentación': ['Supermercado', 'Restaurante', 'Café'],
            'Transporte': ['Gasolina', 'Uber', 'Bus'],
            'Vivienda': ['Alquiler', 'Reparaciones'],
            'Entretenimiento': ['Cine', 'Netflix', 'Juegos'],
            'Salud': ['Farmacia', 'Consulta médica'],
            'Educación': ['Libros', 'Curso online'],
            'Servicios': ['Luz', 'Agua', 'Internet'],
        }

        # Generate ~50 transactions
        for _ in range(50):
            # Pick a category
            cat_name = random.choice(list(categorias.keys()))
            cat = categorias[cat_name]
            
            # Determine amount based on type
            if cat.tipo == 'ingreso':
                monto = Decimal(random.uniform(1000, 5000)).quantize(Decimal('0.01'))
            else:
                monto = Decimal(random.uniform(10, 200)).quantize(Decimal('0.01'))

            # Random date within range
            days_offset = random.randint(0, 90)
            trans_date = today - timedelta(days=days_offset)
            
            # Random description
            desc = random.choice(descriptions.get(cat_name, ['Transacción']))

            Transaccion.objects.create(
                usuario=user,
                fecha=trans_date,
                monto=monto,
                tipo=cat.tipo,
                categoria=cat,
                descripcion=desc
            )
        
        self.stdout.write('Created 50 transactions')

        # 3. Create Budgets for current month
        current_month = today.month
        current_year = today.year

        budget_cats = ['Alimentación', 'Transporte', 'Entretenimiento']
        for cat_name in budget_cats:
            if cat_name in categorias:
                cat = categorias[cat_name]
                amount = Decimal(random.uniform(500, 1500)).quantize(Decimal('0.01'))
                
                Presupuesto.objects.get_or_create(
                    usuario=user,
                    categoria=cat,
                    mes=current_month,
                    año=current_year,
                    defaults={'monto_maximo': amount}
                )
        
        self.stdout.write('Created budgets')
        self.stdout.write(self.style.SUCCESS('Successfully populated demo data'))
