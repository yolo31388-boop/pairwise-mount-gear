"""坐骑马具与装备系统"""
import random
from dataclasses import dataclass, field

VALID_SLOTS = ("saddle", "rein", "hoof", "armor")
VALID_MOUNT_TYPES = ("land", "flying", "water")
STAT_SOFT_CAP = 50.0
SET_BONUS_THRESHOLD = 2


@dataclass
class MountGear:
    gid: str
    name: str
    slot: str = "saddle"  # saddle/rein/hoof/armor
    level: int = 1
    stats: dict = field(default_factory=dict)
    set_id: str = ""
    durability: float = 100
    max_durability: float = 100


class MountGearSystem:
    def __init__(self, seed: int | None = None):
        self.gear: dict[str, MountGear] = {}
        self.mount_type: dict[str, str] = {}  # gear_id -> 坐骑类型限制
        self.rng = random.Random(seed)

    def can_equip(self, gear_id: str, slot: str) -> bool:
        # fix1: 槽位类型必须匹配
        gear = self.gear.get(gear_id)
        if gear is None or slot not in VALID_SLOTS:
            return False
        return gear.slot == slot

    def roll_stats(self, level: int) -> dict:
        # fix2: 基础值上下浮动(±20%)
        base = 5 + level
        return {"speed": round(base * self.rng.uniform(0.8, 1.2), 2)}

    def check_set_bonus(self, gears: list) -> dict:
        # fix3: 按套装ID分组检查
        counts: dict[str, int] = {}
        for g in gears:
            if g.set_id:
                counts[g.set_id] = counts.get(g.set_id, 0) + 1
        for set_id, count in counts.items():
            if count >= SET_BONUS_THRESHOLD:
                return {"bonus": True, "set_id": set_id, "pieces": count}
        return {}

    def get_upgrade_rate(self, level: int) -> float:
        # fix4: 等级越高成功率越低
        return max(0.05, 1.0 - 0.06 * max(0, level))

    def can_use_on_mount(self, gear_id: str, mount_type: str) -> bool:
        # fix5: 坐骑类型限制
        required = self.mount_type.get(gear_id)
        if required is None:
            return True
        return required == mount_type

    def get_stat_cap(self) -> float:
        # fix6: 软上限
        return STAT_SOFT_CAP

    def apply_soft_cap(self, value: float) -> float:
        # 超过软上限部分收益递减
        cap = self.get_stat_cap()
        if value <= cap:
            return value
        return cap + (value - cap) ** 0.5

    def consume_durability(self, gear_id: str, amount: float):
        # fix7: 使用中消耗耐久
        gear = self.gear.get(gear_id)
        if gear is None:
            return
        gear.durability = max(0.0, gear.durability - abs(amount))

    def repair(self, gear_id: str) -> bool:
        gear = self.gear.get(gear_id)
        if gear is None:
            return False
        gear.durability = gear.max_durability
        return True
