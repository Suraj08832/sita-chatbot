import threading
from datetime import datetime, timedelta
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from sitaBot.modules.sql import BASE, SESSION


class UserEconomy(BASE):
    __tablename__ = "user_economy"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    balance = Column(BigInteger, default=0)
    kills = Column(Integer, default=0)
    is_dead = Column(Boolean, default=False)
    death_time = Column(DateTime, nullable=True)
    killed_by = Column(BigInteger, nullable=True)
    protection_until = Column(DateTime, nullable=True)
    last_daily = Column(DateTime, nullable=True)
    
    def __init__(self, user_id, chat_id):
        self.user_id = user_id
        self.chat_id = chat_id
        self.balance = 0
        self.kills = 0
        self.is_dead = False

    def __repr__(self):
        return f"<UserEconomy {self.user_id} in {self.chat_id}>"


class UserInventory(BASE):
    __tablename__ = "user_inventory"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    
    def __init__(self, user_id, item_name, quantity=1):
        self.user_id = user_id
        self.item_name = item_name
        self.quantity = quantity


class Lottery(BASE):
    __tablename__ = "lottery"
    
    lottery_id = Column(Integer, primary_key=True, autoincrement=True)
    total_pool = Column(BigInteger, default=0)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    def __init__(self):
        self.total_pool = 0
        self.start_time = datetime.utcnow()
        self.end_time = datetime.utcnow() + timedelta(days=2)
        self.is_active = True


class LotteryParticipant(BASE):
    __tablename__ = "lottery_participants"
    
    id = Column(Integer, primary_key=True)
    lottery_id = Column(Integer, ForeignKey("lottery.lottery_id"))
    user_id = Column(BigInteger, nullable=False)
    amount = Column(BigInteger, nullable=False)
    
    def __init__(self, lottery_id, user_id, amount):
        self.lottery_id = lottery_id
        self.user_id = user_id
        self.amount = amount


UserEconomy.__table__.create(checkfirst=True)
UserInventory.__table__.create(checkfirst=True)
Lottery.__table__.create(checkfirst=True)
LotteryParticipant.__table__.create(checkfirst=True)

ECONOMY_LOCK = threading.RLock()


def get_or_create_user(user_id, chat_id):
    with ECONOMY_LOCK:
        user = SESSION.query(UserEconomy).filter(
            UserEconomy.user_id == user_id,
            UserEconomy.chat_id == chat_id
        ).first()
        
        if not user:
            user = UserEconomy(user_id, chat_id)
            SESSION.add(user)
            SESSION.commit()
        
        return user


def get_balance(user_id, chat_id):
    user = get_or_create_user(user_id, chat_id)
    return user.balance


def update_balance(user_id, chat_id, amount):
    with ECONOMY_LOCK:
        user = get_or_create_user(user_id, chat_id)
        user.balance += amount
        SESSION.commit()


def get_top_rich(limit=10):
    with ECONOMY_LOCK:
        return SESSION.query(UserEconomy).order_by(
            UserEconomy.balance.desc()
        ).limit(limit).all()


def get_top_killers(limit=10):
    with ECONOMY_LOCK:
        return SESSION.query(UserEconomy).order_by(
            UserEconomy.kills.desc()
        ).limit(limit).all()


def get_user_rank(user_id, chat_id):
    with ECONOMY_LOCK:
        user = get_or_create_user(user_id, chat_id)
        rank = SESSION.query(UserEconomy).filter(
            UserEconomy.balance > user.balance
        ).count()
        return rank + 1 if rank is not None else None


def is_dead(user_id, chat_id):
    user = get_or_create_user(user_id, chat_id)
    
    if user.is_dead:
        if user.death_time and (datetime.utcnow() - user.death_time).total_seconds() > 18000:
            revive_user(user_id, chat_id)
            return False
        return True
    return False


def is_protected(user_id, chat_id):
    user = get_or_create_user(user_id, chat_id)
    
    if user.protection_until:
        if datetime.utcnow() < user.protection_until:
            return True
        else:
            with ECONOMY_LOCK:
                user.protection_until = None
                SESSION.commit()
    return False


def kill_user(user_id, chat_id, killer_id):
    with ECONOMY_LOCK:
        user = get_or_create_user(user_id, chat_id)
        user.is_dead = True
        user.death_time = datetime.utcnow()
        user.killed_by = killer_id
        
        killer = get_or_create_user(killer_id, chat_id)
        killer.kills += 1
        
        SESSION.commit()


def revive_user(user_id, chat_id):
    with ECONOMY_LOCK:
        user = get_or_create_user(user_id, chat_id)
        user.is_dead = False
        user.death_time = None
        user.killed_by = None
        SESSION.commit()


def protect_user(user_id, chat_id, days):
    with ECONOMY_LOCK:
        user = get_or_create_user(user_id, chat_id)
        user.protection_until = datetime.utcnow() + timedelta(days=days)
        SESSION.commit()


def get_inventory(user_id):
    with ECONOMY_LOCK:
        return SESSION.query(UserInventory).filter(
            UserInventory.user_id == user_id
        ).all()


def add_item(user_id, item_name, quantity=1):
    with ECONOMY_LOCK:
        item = SESSION.query(UserInventory).filter(
            UserInventory.user_id == user_id,
            UserInventory.item_name == item_name
        ).first()
        
        if item:
            item.quantity += quantity
        else:
            item = UserInventory(user_id, item_name, quantity)
            SESSION.add(item)
        
        SESSION.commit()


def create_lottery():
    with ECONOMY_LOCK:
        lottery = Lottery()
        SESSION.add(lottery)
        SESSION.commit()
        return lottery.lottery_id


def get_active_lottery():
    with ECONOMY_LOCK:
        lottery = SESSION.query(Lottery).filter(
            Lottery.is_active == True
        ).first()
        
        if lottery and datetime.utcnow() > lottery.end_time:
            lottery.is_active = False
            SESSION.commit()
            return None
        
        return lottery


def join_lottery(lottery_id, user_id, amount):
    with ECONOMY_LOCK:
        existing = SESSION.query(LotteryParticipant).filter(
            LotteryParticipant.lottery_id == lottery_id,
            LotteryParticipant.user_id == user_id
        ).first()
        
        if existing:
            return False
        
        participant = LotteryParticipant(lottery_id, user_id, amount)
        SESSION.add(participant)
        
        lottery = SESSION.query(Lottery).filter(
            Lottery.lottery_id == lottery_id
        ).first()
        lottery.total_pool += amount
        
        SESSION.commit()
        return True


def get_lottery_participants(lottery_id):
    with ECONOMY_LOCK:
        return SESSION.query(LotteryParticipant).filter(
            LotteryParticipant.lottery_id == lottery_id
        ).all()


def can_claim_daily(user_id):
    with ECONOMY_LOCK:
        user = SESSION.query(UserEconomy).filter(
            UserEconomy.user_id == user_id
        ).first()
        
        if not user or not user.last_daily:
            return True
        
        time_since = datetime.utcnow() - user.last_daily
        return time_since.total_seconds() >= 43200


def update_daily(user_id):
    with ECONOMY_LOCK:
        users = SESSION.query(UserEconomy).filter(
            UserEconomy.user_id == user_id
        ).all()
        
        for user in users:
            user.last_daily = datetime.utcnow()
        
        SESSION.commit()
