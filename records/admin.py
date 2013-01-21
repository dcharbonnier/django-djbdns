from django.contrib import admin
from models import Zone, ARecord, CNAMERecord, NSRecord, MXRecord, SPFRecord, TXTRecord, XMPPRecord


class ARecordInline(admin.TabularInline):
    model = ARecord

class MXRecordInline(admin.TabularInline):
    model = MXRecord

class CNAMERecordInline(admin.TabularInline):
    model = CNAMERecord

class NSRecordInline(admin.TabularInline):
    model = NSRecord

class SPFRecordInline(admin.TabularInline):
    model = SPFRecord
    
class TXTRecordInline(admin.TabularInline):
    model = TXTRecord

class XMPPRecordInline(admin.TabularInline):
    model = XMPPRecord

class ZoneAdmin(admin.ModelAdmin):   
    save_on_top = True
    save_as = True


    inlines = [
               ARecordInline,
               CNAMERecordInline,
               NSRecordInline,
               MXRecordInline,
               SPFRecordInline,
               TXTRecordInline,
               XMPPRecordInline,
               ]
    
admin.site.register(Zone,ZoneAdmin)
