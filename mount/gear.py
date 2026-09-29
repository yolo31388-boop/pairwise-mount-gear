"""坐骑马具与装备系统"""
import math
import random
from dataclasses import dataclass, field

SLOTS = ("saddle", "rein", "hoof", "armor")
MOUNT_TYPES = ("land", "flying", "water")
MAX_LEVEL = 15
STAT_CAP = 100.0
MAX_DURABILITY = 100.0


@dataclass
class MountGear:
    gid: str
    name: str
    slot: str = ""  # saddle/rein/hoof/armor
    level: int = 1
    stats: dict = field(default_factory=dict)
    set_id: str = ""
    durability: float = MAX_DURABILITY
    mount_type: str = ""  # land/flying/water，空表示不限


class MountGearSystem:
    def __init__(self, rng=None):
        self.gear: dict[str, MountGear] = {}
        self.mount_type: dict[str, str] = {}
        self.rng = rng if rng is not None else random.Random()

    def can_equip(self, gear_id: str, slot: str) -> bool:
        # 修复1: 槽位必须在合法类型内且与马具自身槽位一致
        gear = self.gear.get(gear_id)
        if gear is None or slot not in SLOTS or gear.slot not in SLOTS:
            return False
        if gear.slot != slot:
            return False
        # 修复7: 耐久耗尽的马具不能装备
        if gear.durability <= 0:
            return False
        return True

    def roll_stats(self, level: int) -> dict:
        # 修复2: 属性在基础值上下浮动 (±20%)
        base = 10.0 * max(level, 1)
        value = base * self.rng.uniform(0.8, 1.2)
        return {"speed": self.apply_soft_cap(value)}

    def apply_soft_cap(self, value: float) -> float:
        # 修复6: 超过软上限后边际递减
        if value <= STAT_CAP:
            return round(value, 2)
        excess = value - STAT_CAP
        return round(STAT_CAP + math.log1p(excess) * 10.0, 2)

    def check_set_bonus(self, gears: list) -> dict:
        # 修复3: 按套装ID分组计数，同组达到件数才触发
        groups: dict[str, int] = {}
        for gear in gears:
            sid = getattr(gear, "set_id", "") or ""
            if sid:
                groups[sid] = groups.get(sid, 0) + 1
        if any(count >= 2 for count in groups.values()):
            return {"bonus": True}
        return {}

    def get_upgrade_rate(self, level: int) -> float:
        # 修复4: 成功率随强化等级递减
        level = max(1, min(level, MAX_LEVEL))
        return round(max(0.05, 0.95 - (level - 1) * 0.06), 4)

    def upgrade_gear(self, gear_id: str) -> bool:
        gear = self.gear.get(gear_id)
        if gear is None or gear.level >= MAX_LEVEL:
            return False
        if self.rng.random() > self.get_upgrade_rate(gear.level):
            return False
        gear.level += 1
        return True

    def can_use_on_mount(self, gear_id: str, mount_type: str) -> bool:
        # 修复5: 马具有坐骑类型限制，不匹配不能使用
        gear = self.gear.get(gear_id)
        if gear is None:
            return False
        required = gear.mount_type or self.mount_type.get(gear_id, "")
        if not required:
            return True
        return required == mount_type

    def get_stat_cap(self) -> float:
        return STAT_CAP

    def consume_durability(self, gear_id: str, amount: float):
        # 修复7: 使用中消耗耐久，不低于0
        gear = self.gear.get(gear_id)
        if gear is None:
            return
        gear.durability = max(0.0, gear.durability - amount)

    def repair(self, gear_id: str) -> bool:
        gear = self.gear.get(gear_id)
        if gear is None:
            return False
        gear.durability = MAX_DURABILITY
        return True
