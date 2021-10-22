from django.contrib import admin
from . models import Category, Payment, Product, Shopcart, Carousel

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'image')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','category','name','price','image','min','max','description','featured','latest','available')

class ShopcartAdmin(admin.ModelAdmin):
    list_display = ('id','user','product','basket_no','quantity','paid_order')

class CarouselAdmin(admin.ModelAdmin):
    list_display = ('image','comment')

class PaymentAdmin(admin.ModelAdmin):
    list_display=('id','user','amount','basket_no','pay_code','paid_order','first_name','last_name','phone','address','city','state')




admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Shopcart,ShopcartAdmin)
admin.site.register(Carousel,CarouselAdmin)
admin.site.register(Payment,PaymentAdmin)