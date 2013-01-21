from django.db import models

class Host(models.Model):
    hostname = models.CharField(max_length=255)
    path = models.CharField(max_length=255, default="/etc/service/tinydns/root")
    key = models.CharField(max_length=255)
    user = models.CharField(max_length=255,default="dnsupdater")
    
    def __unicode__(self):
        return unicode(self.hostname)
    
    
    
    
