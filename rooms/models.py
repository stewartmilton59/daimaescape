from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse


class Room(models.Model):
    ROOM_TYPES = [
        ('one_bedroom', 'One-Bedroom Villa'),  # Changed to match your brand
        ('two_bedroom', 'Two-Bedroom Villa'),  # Changed to match your brand
        ('family', 'Family Villa'),
    ]

    BED_TYPES = [
        ('single', 'Single Bed'),
        ('double', 'Double Bed'),
        ('queen', 'Queen Bed'),
        ('king', 'King Bed'),
        ('twin', 'Twin Beds'),
    ]

    # Basic Information
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    room_type = models.CharField(
        max_length=20, choices=ROOM_TYPES, default='one_bedroom')
    villa_code = models.CharField(
        max_length=10, unique=True, blank=True, null=True)  # Optional

    # Pricing (in TZS as per your menu)
    price_per_night_tzs = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Price in Tanzanian Shillings")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                           help_text="Discount percentage (0-100)")

    # Villa Details - Updated to match your PDF
    description = models.TextField()
    short_description = models.CharField(
        max_length=200, help_text="Brief description for cards")

    # Capacity
    max_guests = models.PositiveIntegerField(
        default=2, validators=[MinValueValidator(1)])
    beds = models.PositiveIntegerField(default=1, help_text="Number of beds")
    bed_type = models.CharField(
        max_length=20, choices=BED_TYPES, default='queen')
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)

    # Amenities - Updated from your PDF (page 7)
    has_wifi = models.BooleanField(
        default=True, help_text="High-Speed Internet")
    has_smart_tv = models.BooleanField(
        default=True, help_text="Smart TV with Netflix, YouTube")
    has_ac = models.BooleanField(default=True)
    has_fireplace = models.BooleanField(
        default=False, help_text="Fireplace for cozy evenings")
    has_fully_equipped_kitchen = models.BooleanField(default=True)
    has_private_bathroom = models.BooleanField(
        default=True, help_text="Private bathroom with hot shower")
    has_outdoor_seating = models.BooleanField(
        default=True, help_text="Patio with garden views")
    has_bbq_grill = models.BooleanField(default=False)
    has_bluetooth_speaker = models.BooleanField(
        default=False, help_text="Wireless speaker")
    has_umbrellas = models.BooleanField(
        default=False, help_text="Umbrellas for rainy days")

    # Images
    main_image = models.ImageField(
        upload_to='rooms/main/', null=True, blank=True)

    # Metadata
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(
        default=False, help_text="Show on homepage")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0,
                                 validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_reviews = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'name']
        indexes = [
            models.Index(fields=['room_type', 'is_available']),
            models.Index(fields=['price_per_night_tzs']),
        ]

    def __str__(self):
        return f"{self.get_room_type_display()} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.get_room_type_display()}")
        if not self.villa_code:
            # Generate a simple villa code
            prefix = '1BR' if self.room_type == 'one_bedroom' else '2BR'
            self.villa_code = f"{prefix}-{self.id or '001'}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('rooms:room_detail', args=[self.slug])

    def get_discounted_price_tzs(self):
        """Calculate price after discount in TZS"""
        if self.discount_percent > 0:
            discount = (self.price_per_night_tzs * self.discount_percent) / 100
            return self.price_per_night_tzs - discount
        return self.price_per_night_tzs

    def get_amenities_list(self):
        """Return list of available amenities matching your PDF"""
        amenities = []
        if self.has_wifi:
            amenities.append({'name': 'High-Speed WiFi', 'icon': 'fa-wifi'})
        if self.has_smart_tv:
            amenities.append(
                {'name': 'Smart TV with Netflix', 'icon': 'fa-tv'})
        if self.has_ac:
            amenities.append({'name': 'Air Conditioning', 'icon': 'fa-wind'})
        if self.has_fireplace:
            amenities.append({'name': 'Fireplace', 'icon': 'fa-fire'})
        if self.has_fully_equipped_kitchen:
            amenities.append(
                {'name': 'Fully Equipped Kitchen', 'icon': 'fa-utensils'})
        if self.has_private_bathroom:
            amenities.append({'name': 'Private Bathroom', 'icon': 'fa-bath'})
        if self.has_outdoor_seating:
            amenities.append({'name': 'Outdoor Patio', 'icon': 'fa-tree'})
        if self.has_bbq_grill:
            amenities.append({'name': 'BBQ Grill', 'icon': 'fa-fire'})
        if self.has_bluetooth_speaker:
            amenities.append({'name': 'Bluetooth Speaker', 'icon': 'fa-music'})
        if self.has_umbrellas:
            amenities.append({'name': 'Umbrellas', 'icon': 'fa-umbrella'})
        return amenities


class RoomImage(models.Model):
    """Additional images for rooms"""
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='rooms/additional/')
    caption = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.room.name}"


class RoomFeature(models.Model):
    """Features like '3 Bed', '2 Bath', etc."""
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='features')
    icon = models.CharField(
        max_length=50, help_text="Font Awesome icon class (e.g., 'fa-bed')")
    text = models.CharField(
        max_length=100, help_text="Display text (e.g., '3 Bed')")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.text} for {self.room.name}"


# New model for House Rules (from your PDF page 9-10)
class HouseRule(models.Model):
    CATEGORY_CHOICES = [
        ('smoking', 'Smoking & Fire Safety'),
        ('property', 'Rooms & Property Care'),
        ('quiet', 'Peace & Quiet'),
        ('nature', 'Nature & Environment'),
        ('safety', 'Safety & Valuables'),
        ('conduct', 'Guest Conduct'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    rule = models.TextField()
    icon = models.CharField(max_length=50, blank=True,
                            help_text="Font Awesome icon")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['category', 'order']

    def __str__(self):
        return f"{self.get_category_display()}: {self.rule[:50]}"


# New model for Laundry Services (from your PDF page 10)
class LaundryService(models.Model):
    name = models.CharField(max_length=100)
    price_tzs = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Laundry Services"

    def __str__(self):
        return f"{self.name} - TSh {self.price_tzs}"
