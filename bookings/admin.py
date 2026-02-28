from django.contrib import admin
from django.utils.html import format_html
from .models import Booking, BookingPayment, BookingHistory


class BookingPaymentInline(admin.TabularInline):
    model = BookingPayment
    extra = 0
    fields = ['amount', 'payment_method', 'transaction_id', 'paid_at']
    readonly_fields = ['paid_at']


class BookingHistoryInline(admin.TabularInline):
    model = BookingHistory
    extra = 0
    fields = ['status_from', 'status_to', 'changed_by', 'changed_at']
    readonly_fields = ['changed_at']
    can_delete = False


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'guest_name', 'room_link', 'check_in_date',
                    'check_out_date', 'total_amount', 'status_badge', 'payment_badge']
    list_filter = ['status', 'payment_status',
                   'check_in_date', 'check_out_date']
    search_fields = ['booking_reference', 'guest_name', 'guest_email']
    readonly_fields = ['booking_reference', 'created_at', 'updated_at']
    inlines = [BookingPaymentInline, BookingHistoryInline]

    def room_link(self, obj):
        url = f"/admin/rooms/room/{obj.room.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.room.name)
    room_link.short_description = 'Room'

    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'blue',
            'checked_in': 'green',
            'checked_out': 'gray',
            'cancelled': 'red',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 10px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def payment_badge(self, obj):
        colors = {
            'pending': 'orange',
            'partial': 'blue',
            'paid': 'green',
            'refunded': 'gray',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 10px;">{}</span>',
            colors.get(obj.payment_status, 'gray'),
            obj.get_payment_status_display()
        )
    payment_badge.short_description = 'Payment'


@admin.register(BookingPayment)
class BookingPaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'amount', 'payment_method', 'paid_at']
    list_filter = ['payment_method', 'paid_at']


@admin.register(BookingHistory)
class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ['booking', 'status_from',
                    'status_to', 'changed_by', 'changed_at']
    list_filter = ['changed_at']
    readonly_fields = ['changed_at']
