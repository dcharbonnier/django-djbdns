from django.core.management.base import NoArgsCommand
from records.models import *
  
class Command(NoArgsCommand):
    help = "Dump djbdns file"
    
    def handle_noargs(self, **options):
        data = ""
        for zone in Zone.objects.all():
            data+=zone.toData();
        print data