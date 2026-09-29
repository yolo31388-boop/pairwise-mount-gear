"""坐骑马具与装备系统 - 红态测试"""
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mount.gear import MountGearSystem, MountGear

class TestSlotRestriction:
    def test_saddle_cannot_go_rein_slot(self):
        mgs = MountGearSystem()
        mgs.gear["g1"] = MountGear("g1", "saddle", slot="saddle")
        assert mgs.can_equip("g1", "rein") == False

class TestStatsVariance:
    def test_same_level_gear_has_variance(self):
        mgs = MountGearSystem()
        # 应该有随机浮动
        assert hasattr(mgs, "rng")
        import random
        mgs.rng = random.Random(42)
        stats_list = [mgs.roll_stats(5) for _ in range(10)]
        values = [s["speed"] for s in stats_list]
        assert len(set(values)) > 1

class TestSetBonusById:
    def test_mixed_set_doesnt_trigger(self):
        mgs = MountGearSystem()
        gears = [MountGear("g1", "a", set_id="A"), MountGear("g2", "b", set_id="B")]
        result = mgs.check_set_bonus(gears)
        assert result == {}

class TestUpgradeRate:
    def test_higher_level_lower_rate(self):
        mgs = MountGearSystem()
        r1 = mgs.get_upgrade_rate(1)
        r10 = mgs.get_upgrade_rate(10)
        assert r10 < r1

class TestMountTypeRestriction:
    def test_flying_gear_cannot_use_on_land_mount(self):
        mgs = MountGearSystem()
        mgs.gear["g1"] = MountGear("g1", "wings", slot="armor")
        mgs.mount_type["g1"] = "flying"
        assert mgs.can_use_on_mount("g1", "land") == False

class TestStatCap:
    def test_stats_have_soft_cap(self):
        mgs = MountGearSystem()
        cap = mgs.get_stat_cap()
        assert cap < float("inf")

class TestDurabilityConsumption:
    def test_durability_decreases_with_use(self):
        mgs = MountGearSystem()
        mgs.gear["g1"] = MountGear("g1", "saddle", durability=100)
        mgs.consume_durability("g1", 10)
        assert mgs.gear["g1"].durability < 100
