from django.core.management.base import BaseCommand
from cafe.models import Category, Product

class Command(BaseCommand):
    help = 'Seed initial menu data'

    def handle(self, *args, **kwargs):
        # Categories
        food_cat, _ = Category.objects.get_or_create(name='Food', slug='food', defaults={'icon': '🍕'})
        drinks_cat, _ = Category.objects.get_or_create(name='Drinks', slug='drinks', defaults={'icon': '🧋'})
        hot_cat, _ = Category.objects.get_or_create(name='Hot Drinks', slug='hot-drinks', defaults={'icon': '☕'})

        food_items = [
            ('Pizza', 'Classic crispy pizza with premium toppings', 350, True),
            ('Keema Noodles', 'Spicy minced meat noodles, Nepali style', 220, True),
            ('Momo', 'Traditional steamed dumplings with sauce', 180, True),
            ('Jhol Momo', 'Momo in spicy soupy broth', 200, True),
            ('Cheese French Fries', 'Crispy fries loaded with melted cheese', 180, False),
            ('Peri Peri Fries', 'Spicy peri peri seasoned fries', 160, True),
            ('Normal Fries', 'Classic golden crispy fries', 120, False),
            ('Sandwich', 'Freshly made club sandwich', 180, False),
            ('Sausage', 'Grilled chicken sausage with sauce', 200, False),
            ('Potato Twister', 'Spiral twisted potato on a stick', 150, True),
        ]

        drinks_items = [
            ('Bubble Tea', 'Creamy milk tea with tapioca pearls', 220, True),
            ('Mojito', 'Refreshing mint lime mojito', 180, True),
            ('Peach Iced Tea', 'Sweet chilled peach flavored tea', 160, False),
            ('Monster Energy', 'Monster energy drink can', 250, False),
            ('Diet Coke', 'Chilled diet coca-cola', 120, False),
            ('Red Bull', 'Red Bull energy drink', 250, False),
            ('Oreo Milkshake', 'Thick creamy Oreo cookie milkshake', 280, True),
            ('Chocolate Milkshake', 'Rich thick chocolate milkshake', 260, True),
            ('Strawberry Milkshake', 'Fresh strawberry milkshake', 260, False),
        ]

        hot_items = [
            ('Americano', 'Strong black espresso with hot water', 150, True),
            ('Hot Chocolate', 'Creamy rich hot chocolate drink', 180, True),
            ('Masala Tea', 'Spiced chai with cardamom & ginger', 80, False),
            ('Matka Tea', 'Traditional clay pot brewed tea', 100, False),
        ]

        for name, desc, price, featured in food_items:
            Product.objects.get_or_create(name=name, defaults={
                'description': desc, 'price': price,
                'category': food_cat, 'is_featured': featured
            })

        for name, desc, price, featured in drinks_items:
            Product.objects.get_or_create(name=name, defaults={
                'description': desc, 'price': price,
                'category': drinks_cat, 'is_featured': featured
            })

        for name, desc, price, featured in hot_items:
            Product.objects.get_or_create(name=name, defaults={
                'description': desc, 'price': price,
                'category': hot_cat, 'is_featured': featured
            })

        self.stdout.write(self.style.SUCCESS('Menu data seeded successfully!'))
