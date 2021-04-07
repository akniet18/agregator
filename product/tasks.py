
from datetime import datetime, timedelta
from .models import *
from huey import crontab
from utils.push import send_push
from huey.contrib.djhuey import db_periodic_task, db_task

# @periodic_task(run_every=timedelta(seconds=10))
@db_periodic_task(crontab(minute="*/1"))
def send_notifiction():    
    p = CountProduct.objects.filter(count__lte=10)
    for i in p:
        send_push(i.pharmacy.owner, f"У вас заканчивается запас «{i.product.name}». В текущий момент оставшееся количество : «{i.count}»")
        print(i.product.name, i.count)
    return "ok"
    

    
        
