from django.core.management.base import BaseCommand, CommandError
from records.models import *

class Command(BaseCommand):
    args = '<file_path file_path ...>'
    help = 'Import zones from djbdns data file'

    def handle(self, *args, **options):
        for file in args:
            f = open(file, 'r')
            for record in f:
                try:
                    if record[0] == "Z":
                        data = record[1:].split(':')
                        z,created = Zone.objects.get_or_create(name=data[0])
                        z.email = data[2].replace('.', '@', 1)
                        z.refresh = data[4]
                        z.retry = data[5]
                        z.expire = data[6]
                        z.min = data[7]
                        z.ttl = data[8]
                        z.save()
                    elif record[0] == "&":
                        data = record[1:].split(':')
                        zone=get_zone(data[0])
                        r = NSRecord()
                        r.zone=zone
                        r.destination=data[2]
                        r.ttl=data[3]
                        r.save()
                    elif record[0] == "+":
                        data = record[1:].split(':')
                        zone=get_zone(data[0])
                        r = ARecord()
                        r.zone=zone
                        r.subdomain=get_subdomain(zone,data[0])
                        r.ip=data[1]
                        r.ttl=data[2]
                        r.save()
                    elif record[0] == "@":
                        data = record[1:].split(':')
                        zone=get_zone(data[0])
                        r = MXRecord()
                        r.zone=zone
                        r.destination=data[2]
                        r.weight=int(data[3])
                        r.ttl=int(data[4])
                        r.save()
                    elif record[0] == "C":
                        data = record[1:].split(':')
                        zone=get_zone(data[0])
                        r = CNAMERecord()
                        r.zone=zone
                        r.subdomain=get_subdomain(zone,data[0])
                        r.destination=data[1]
                        r.ttl=int(data[2])
                        r.save()
                    else:
                        print record
                except Zone.DoesNotExist:
                    print "Zone.DoesNotExist", data
                except Exception, e:
                    print e, record
            self.stdout.write('imported')
            
def get_subdomain(zone,fqdn):
    subdomain=fqdn.replace(zone.name,'')
    if subdomain=='':
        return ''
    if subdomain[-1] == '.':
        subdomain=subdomain[:-1]
    return subdomain

def get_zone(fqdn):
    try:
        return Zone.objects.get(name=fqdn)
    except Zone.DoesNotExist, e:
        fqdn = '.'.join(fqdn.split('.')[1:])
        if fqdn == '':
            raise e
        else:
            return get_zone(fqdn) 
