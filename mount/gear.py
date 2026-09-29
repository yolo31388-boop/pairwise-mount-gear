"""坐骑马具与装备系统 - 含7个bug"""
from dataclasses import dataclass, field

@dataclass
class MountGear:
    gid: str
    name: str
    slot: str  # saddle/rein/hoof/armor
    level: int = 1
    stats: dict = field(default_factory=dict)
    set_id: str = ""
    durability: float = 100  # bug7: 不消耗

class MountGearSystem:
    def __init__(self):
        self.gear: dict[str, MountGear] = {}
        self.mount_type: dict[str, str] = {}  # bug5: 不检查类型

    def can_equip(self, gear_id: str, slot: str) -> bool:
        # bug1: 无槽位类型限制
        return True

    def roll_stats(self, level: int) -> dict:
        # bug2: 固定值
        return {"speed": 10}

    def check_set_bonus(self, gears: list) -> dict:
        # bug3: 不看ID只看数量
        if len(gears) >= 2:
            return {"bonus": True}
        return {}

    def get_upgrade_rate(self, level: int) -> float:
        # bug4: 100%成功
        return 1.0

    def can_use_on_mount(self, gear_id: str, mount_type: str) -> bool:
        # bug5: 跨类型
        return True

    def get_stat_cap(self) -> float:
        # bug6: 无上限
        return float("inf")

    def consume_durability(self, gear_id: str, amount: float):
        # bug7: 不消耗
        pass
