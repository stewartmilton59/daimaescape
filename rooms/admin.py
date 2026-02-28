from django.contrib import admin
from django.utils.html import format_html
from .models import Room, RoomImage, RoomFeature


class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1
    fields = ['image', 'caption', 'is_featured', 'order']

    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 5px;" />', obj.image.url)
        return "No Image"
    get_image_preview.short_description = 'Preview'

    readonly_fields = ['get_image_preview']


class RoomFeatureInline(admin.TabularInline):
    model = RoomFeature
    extra = 3
    fields = ['icon', 'text', 'order']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['villa_code', 'name', 'room_type', 'price_per_night_tzs',
                    'get_discounted_price_display', 'is_available', 'is_featured',
                    'rating', 'main_image_preview']
    list_filter = ['room_type', 'is_available', 'is_featured', 'bed_type',
                   'has_wifi', 'has_ac', 'has_fireplace']
    search_fields = ['name', 'villa_code', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'main_image_preview']
    list_editable = ['is_available', 'is_featured']
    list_per_page = 20

    fieldsets = [
        ('Basic Information', {
            'fields': ('name', 'slug', 'room_type', 'villa_code', 'main_image', 'main_image_preview')
        }),
        ('Pricing (Tanzanian Shillings)', {
            'fields': ('price_per_night_tzs', 'discount_percent'),
            'classes': ('wide',)
        }),
        ('Description', {
            'fields': ('short_description', 'description'),
            'classes': ('wide',)
        }),
        ('Room Details', {
            'fields': ('max_guests', ('bedrooms', 'beds'), ('bathrooms', 'bed_type')),
            'classes': ('wide',)
        }),
        ('Amenities', {
            'fields': (
                ('has_wifi', 'has_smart_tv'),
                ('has_ac', 'has_fireplace'),
                ('has_fully_equipped_kitchen', 'has_private_bathroom'),
                ('has_outdoor_seating', 'has_bbq_grill'),
                ('has_bluetooth_speaker', 'has_umbrellas'),
            ),
            'classes': ('wide', 'collapse')
        }),
        ('Metadata', {
            'fields': ('is_available', 'is_featured', 'rating', 'total_reviews'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]

    inlines = [RoomFeatureInline, RoomImageInline]

    def get_discounted_price_display(self, obj):
        original = obj.price_per_night_tzs
        discounted = obj.get_discounted_price_tzs()
        if obj.discount_percent > 0:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">TSh {}</span> '
                '<span style="color: green; font-weight: bold;">TSh {}</span> '
                '<span style="color: red;">(-{}%)</span>',
                original, discounted, obj.discount_percent
            )
        return format_html('<span>TSh {}</span>', original)
    get_discounted_price_display.short_description = 'Price'

    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 5px;" />',
                obj.main_image.url
            )
        return "No Image"
    main_image_preview.short_description = 'Image Preview'

    actions = ['make_available', 'make_unavailable', 'make_featured']

    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} villas marked as available.')
    make_available.short_description = "Mark selected villas as available"

    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} villas marked as unavailable.')
    make_unavailable.short_description = "Mark selected villas as unavailable"

    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} villas marked as featured.')
    make_featured.short_description = "Mark selected villas as featured"
