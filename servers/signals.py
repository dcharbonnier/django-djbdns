from django.db.models import signals
from records.models import *
from servers.models import Host
import os
import tempfile
from fabric.api import env, cd
from fabric.operations import run, put
    
def push(sender, instance, signal, *args, **kwargs):
    
    temp = tempfile.NamedTemporaryFile(mode='w+t')
    for zone in Zone.objects.all():
        temp.write(zone.toData())

    temp.flush()
    for host in Host.objects.all():
        env.host_string = host.hostname
        env.user = host.user
        env.key_filename = host.key 
        put(temp.name, "%s/data" % host.path)  
        with cd(host.path):
            run('make')
        
    temp.close()
    
   
models.signals.post_save.connect(push, sender=ARecord)
models.signals.post_save.connect(push, sender=CNAMERecord)
models.signals.post_save.connect(push, sender=MXRecord)
models.signals.post_save.connect(push, sender=NSRecord)
models.signals.post_save.connect(push, sender=SPFRecord)
models.signals.post_save.connect(push, sender=DKIMRecord)
models.signals.post_save.connect(push, sender=TXTRecord) 
models.signals.post_save.connect(push, sender=Zone)