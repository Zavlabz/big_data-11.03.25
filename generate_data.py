import random
from datetime import datetime, timedelta
from faker import Faker
import csv

fake = Faker()

start_date = datetime(2023, 1, 1)
end_date   = datetime(2023, 1, 31)
days       = (end_date - start_date).days + 1
action_types = [
    'first_visit','registration','login','logout',
    'create_topic','view_topic','delete_topic','create_message'
]

users = []
logs  = []
uid   = 1

for d in range(days):
    day = start_date + timedelta(days=d)
    # 5 регистраций
    for _ in range(5):
        users.append({'user_id':uid,'username':fake.user_name(),'created_at':day})
        logs.append({
            'user_id':uid,'action_type':'registration',
            'server_response':'success','timestamp':day,'action_id':None
        })
        uid += 1

    # остальные действия
    for action in action_types:
        count = 5 + (2 if action=='create_topic' else 0)
        for _ in range(count):
            user_id = random.choice(users)['user_id'] if users and action!='registration' else None
            if action=='create_topic':
                # иногда ошибка
                if random.choice([True,False]):
                    user_id = None; resp='error'
                else:
                    resp = 'success' if user_id else 'error'
            else:
                resp = 'success'
            logs.append({
                'user_id':user_id,'action_type':action,
                'action_id':random.randint(1000,9999) if action in ('create_topic','create_message') else None,
                'server_response':resp,'timestamp':day
            })

def fmt(v):
    if v is None: return ''
    if isinstance(v, datetime): return v.strftime('%Y-%m-%d %H:%M:%S')
    return v

with open('users.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['user_id','username','created_at'])
    w.writeheader()
    for u in users: w.writerow({'user_id':u['user_id'],'username':u['username'],'created_at':fmt(u['created_at'])})

with open('logs.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f)
    w.writerow(['user_id','action_type','action_id','server_response','timestamp'])
    for L in logs:
        w.writerow([
            L['user_id'] or '',
            L['action_type'],
            L['action_id'] or '',
            L['server_response'],
            L['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        ])
