from django.db import models
from model_utils.managers import InheritanceManager
from django.db import transaction

class Zone(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    refresh = models.IntegerField(default=16384)
    retry = models.IntegerField(default=2048)
    expire = models.IntegerField(default=1048576)
    min = models.IntegerField(default=2560)
    ttl = models.IntegerField(default=300)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return unicode(self.name)

    def toData(self):
        if NSRecord.objects.filter(zone=self).count() == 0:
            return u'#%s\n' % self.name
        data = u"Z%(name)s:%(ns)s:%(email)s:%(serial)s:%(refresh)s:%(retry)s:%(expire)s:%(min)s:%(ttl)s:\n" % {
                'name': self.name,
                'ns':NSRecord.objects.filter(zone=self)[0].destination,
                'email':self.email.replace('@','.'),
                'serial':Record.objects.filter(zone=self).aggregate(models.Max('modified'))['modified__max'].strftime('%Y%m%d%H'),
                'refresh': self.refresh,
                'retry': self.retry,
                'expire':self.expire,
                'min': self.min,
                'ttl':self.ttl
            }
        
        for record in Record.objects.filter(zone=self).select_subclasses():
            data+=record.toData()+"\n"

        return data
         
    
class Record(models.Model):
    zone = models.ForeignKey('Zone')
    ttl = models.IntegerField(default=300)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    objects = InheritanceManager()

    
class ARecord(Record):
    subdomain = models.CharField(max_length=255, blank=True,null=True)
    ip = models.IPAddressField()
    
    def toData(self):
        return u"+%(subdomain)s%(zone)s:%(ip)s:%(ttl)s:" % {
            'subdomain': '' if self.subdomain == '' else self.subdomain+'.',
            'zone':self.zone.name,
            'ip': self.ip,
            'ttl': self.ttl
        }

class CNAMERecord(Record):
    subdomain = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    
    def toData(self):
        return u"C%(subdomain)s%(zone)s:%(destination)s:%(ttl)s:" % {
            'subdomain': '' if self.subdomain == '' else self.subdomain+'.',
            'zone':self.zone.name,
            'destination': self.destination,
            'ttl': self.ttl
        }

class MXRecord(Record):
    destination = models.CharField(max_length=255)
    weight = models.IntegerField(default=0)
    
    def toData(self):
        return u"@%(zone)s:%(ip)s:%(destination)s:%(distance)s:%(ttl)s:" % {
            'zone':self.zone.name,
            'ip': '',
            'destination': self.destination,
            'distance': self.weight,
            'ttl': self.ttl
        }

class NSRecord(Record):
    destination = models.CharField(max_length=255)
    def toData(self):
        return u"&%(zone)s:%(ip)s:%(destination)s:%(ttl)s:" % {
            'zone':self.zone.name,
            'ip': '',
            'destination': self.destination,
            'ttl': self.ttl
        }
    
class SPFRecord(Record):
    #'fqdn:s:ttl:
    data = models.CharField(max_length=255)
    def toData(self):
        return u"'%(zone)s:%(data)s:%(ttl)s:" % {
            'zone':self.zone.name,
            'data': self.data.replace(':',r'\072'),
            'ttl': self.ttl
        }

class DKIMRecord(Record):
    #'fqdn:s:ttl:
    pass


def toOctalString(value):
    return "\%s\%s" % (
        "{0:0>3o}".format(int(value/256.0)),
        "{0:0>3o}".format(int(value%256))
        )

def toLabelString(value):
    labels = value.split ( "." ) ;
    result = ""
    for value in labels:
        result += "\\" + "{0:0>3o}".format(len(value)) + value
    return result + r'\000'  ;

class XMPPRecord(Record):
    #'fqdn:s:ttl:
    #:_jabber._tcp.example.com:33:\000\000\000\000\024\225\006sdqdqs\000
    subdomain = models.CharField(max_length=255, blank=True,null=True)
    priority = models.IntegerField(default=0)
    weight = models.IntegerField(default=0)
    c2s_port = models.IntegerField(default=5222)    
    s2s_port = models.IntegerField(default=5269)    
    destination = models.CharField(max_length=255)
    
    def toData(self):
        result = [
                u":_jabber._tcp.%(subdomain)s%(zone)s:33:%(priority)s%(weight)s%(port)s%(destination)s:%(ttl)s:" % {
                    'subdomain': '' if self.subdomain == '' else self.subdomain+'.',
                    'zone':self.zone.name,
                    'priority': toOctalString(self.priority),
                    'weight': toOctalString(self.weight),
                    'port' : toOctalString(self.s2s_port),
                    'destination' : toLabelString(self.destination),
                    'ttl': self.ttl
                },
                u":_xmpp-server._tcp.%(subdomain)s%(zone)s:33:%(priority)s%(weight)s%(port)s%(destination)s:%(ttl)s:" % {
                    'subdomain': '' if self.subdomain == '' else self.subdomain+'.',
                    'zone':self.zone.name,
                    'priority': toOctalString(self.priority),
                    'weight': toOctalString(self.weight),
                    'port' : toOctalString(self.s2s_port),
                    'destination' : toLabelString(self.destination),
                    'ttl': self.ttl
                },
                u":_xmpp-client._tcp.%(subdomain)s%(zone)s:33:%(priority)s%(weight)s%(port)s%(destination)s:%(ttl)s:" % {
                    'subdomain': '' if self.subdomain == '' else self.subdomain+'.',
                    'zone':self.zone.name,
                    'priority': toOctalString(self.priority),
                    'weight': toOctalString(self.weight),
                    'port' : toOctalString(self.c2s_port),
                    'destination' : toLabelString(self.destination),
                    'ttl': self.ttl
                }
            ]
        return '\n'.join(result)


class TXTRecord(Record):
    #'fqdn:s:ttl:
    subdomain = models.CharField(max_length=255, blank=True,null=True)
    data = models.CharField(max_length=255)
    def toData(self):
        return u"'%(subdomain)s%(zone)s:%(data)s:%(ttl)s:" % {
	    'subdomain': '' if self.subdomain == '' else self.subdomain+'.',
            'zone':self.zone.name,
            'data': self.data.replace(':',r'\072'),
            'ttl': self.ttl
        }
    
    
