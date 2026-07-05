from django.utils import timezone
from shop.models import Category, Product, ProductImage, Coupon, Offer, Banner, StoreSetting

def seed():
    # 0. Clean up images/banners to avoid duplication
    print("Clearing old images and banners...")
    ProductImage.objects.all().delete()
    Banner.objects.all().delete()

    # 1. Initialize store settings
    settings_obj = StoreSetting.get_settings()
    settings_obj.announcement_text = "Free Shipping On Luxury Jewelry Orders Above ₹699"
    settings_obj.whatsapp_number = "+917777974101"
    settings_obj.save()
    
    # 2. Create Categories
    print("Seeding Categories...")
    # Parent Categories
    women_col, _ = Category.objects.get_or_create(name="Women Collection")
    men_col, _ = Category.objects.get_or_create(name="Men Collection")
    
    # Women subcategories
    w_rings, _ = Category.objects.get_or_create(name="Women Rings", parent=women_col)
    w_neck, _ = Category.objects.get_or_create(name="Women Necklaces", parent=women_col)
    w_brace, _ = Category.objects.get_or_create(name="Women Bracelets", parent=women_col)
    w_ank, _ = Category.objects.get_or_create(name="Anklets", parent=women_col)
    w_mangal, _ = Category.objects.get_or_create(name="Mangalsutra", parent=women_col)
    w_earring, _ = Category.objects.get_or_create(name="Earrings", parent=women_col)
    w_combo, _ = Category.objects.get_or_create(name="Combo Sets", parent=women_col)
    
    # Men subcategories
    m_chains, _ = Category.objects.get_or_create(name="Men Chains", parent=men_col)
    m_brace, _ = Category.objects.get_or_create(name="Men Bracelets", parent=men_col)
    m_kada, _ = Category.objects.get_or_create(name="Kada", parent=men_col)
    m_rings, _ = Category.objects.get_or_create(name="Men Rings", parent=men_col)
    
    # 3. Create Products
    print("Seeding Products...")
    
    # P1: Women Ring
    p1, _ = Product.objects.get_or_create(
        name="Royal Gold Polished Solitaire Ring",
        defaults={
            'description': "Crafted in gold-plated brass with a shimmering premium AAA+ cubic zirconia solitaire crystal. Designed to shine on every formal dress occasion.",
            'price': 899.00,
            'discount_price': 699.00,
            'category': w_rings,
            'stock': 15,
            'is_featured': True,
            'is_new_arrival': True,
            'is_best_seller': True
        }
    )
    ProductImage.objects.get_or_create(
        product=p1,
        image="products/ring.png",
        is_primary=True
    )

    # P2: Women Necklace
    p2, _ = Product.objects.get_or_create(
        name="Classic Kundan Pearl Choker Set",
        defaults={
            'description': "Traditional heritage kundan choker embellished with multi-layered micro pearls and golden lace adjustable drawstrings. Includes matching earrings.",
            'price': 1899.00,
            'discount_price': 1499.00,
            'category': w_neck,
            'stock': 8,
            'is_featured': True,
            'is_new_arrival': True,
            'is_trending': True
        }
    )
    ProductImage.objects.get_or_create(
        product=p2,
        image="products/necklace.png",
        is_primary=True
    )

    # P3: Women Bracelet
    p3, _ = Product.objects.get_or_create(
        name="Minimalist Diamond-Cut Gold Bangle",
        defaults={
            'description': "Sleek, stackable geometric bangle carved with detailed diamond-cut patterns that catch light from all directions. Gold polish finish.",
            'price': 599.00,
            'category': w_brace,
            'stock': 20,
            'is_new_arrival': True,
            'is_trending': True
        }
    )
    ProductImage.objects.get_or_create(
        product=p3,
        image="products/bracelet.png",
        is_primary=True
    )

    # P4: Men Heavy Chain
    p4, _ = Product.objects.get_or_create(
        name="Men's Heavy Cuban Link Gold Chain",
        defaults={
            'description': "Thick 24-inch Cuban link statement chain for men. Double polished in gold plating for durability and premium metallic shine.",
            'price': 1299.00,
            'discount_price': 999.00,
            'category': m_chains,
            'stock': 12,
            'is_featured': True,
            'is_best_seller': True
        }
    )
    ProductImage.objects.get_or_create(
        product=p4,
        image="products/chain.png",
        is_primary=True
    )

    # P5: Men Kada
    p5, _ = Product.objects.get_or_create(
        name="Royal Carved Gold Kada Bracelet",
        defaults={
            'description': "Traditional heavy brass kada for men with detailed geometric tribal carvings. Features an openable hinge design for comfortable fit.",
            'price': 949.00,
            'discount_price': 799.00,
            'category': m_kada,
            'stock': 5,
            'is_new_arrival': True,
            'is_trending': True
        }
    )
    ProductImage.objects.get_or_create(
        product=p5,
        image="products/kada.png",
        is_primary=True
    )
    
    # P6: Women Earrings (Low stock for warning verification)
    p6, _ = Product.objects.get_or_create(
        name="Emerald Gold Drop Jhumka Earrings",
        defaults={
            'description': "Premium artificial emerald drop jhumka earrings featuring floral designs and tiny dangling pearl beads.",
            'price': 499.00,
            'category': w_earring,
            'stock': 3,
            'is_new_arrival': True
        }
    )
    ProductImage.objects.get_or_create(
        product=p6,
        image="products/earrings.png",
        is_primary=True
    )

    # 4. Create Coupons
    print("Seeding Coupons...")
    Coupon.objects.get_or_create(
        code="RARA15",
        defaults={
            'discount_percentage': 15.00,
            'min_purchase': 499.00,
            'valid_from': timezone.now(),
            'valid_to': timezone.now() + timezone.timedelta(days=90),
            'active': True
        }
    )
    Coupon.objects.get_or_create(
        code="FESTIVE200",
        defaults={
            'discount_amount': 200.00,
            'min_purchase': 999.00,
            'valid_from': timezone.now(),
            'valid_to': timezone.now() + timezone.timedelta(days=90),
            'active': True
        }
    )
    
    # 5. Create Banners
    print("Seeding Hero Banners...")
    Banner.objects.get_or_create(
        title="THE ROYAL WOMEN COLLECTION",
        defaults={
            'subtitle': "Anti-tarnish, gold-plated Kundan, Pearls, and Solitaire collections crafted to perfection.",
            'image': "banners/banner_women.png",
            'order': 1,
            'active': True
        }
    )
    Banner.objects.get_or_create(
        title="BOLD STATEMENT MEN JEWELRY",
        defaults={
            'subtitle': "Explore heavy Cuban link chains, custom gold bracelets, rings, and premium carved Kadas.",
            'image': "banners/banner_men.png",
            'order': 2,
            'active': True
        }
    )

    print("Seeding Complete!")

if __name__ == "__main__":
    seed()
