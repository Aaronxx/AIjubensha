"""TDD unit tests: arc transitions, fact matching, parser robustness."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.models import (
    ArcState, ArcTransition, GamePhase, InfoLevel, KnowledgeEntry,
    NPCDefinition, NPCState, PersonalityMatrix, Relationship,
    RelationType, SelfAwareness, SilenceStrategy,
)
from src.prompt import EMOTION_CALM
from src.state_manager import StateManager
from src.prompt import OutputParser, OutputParseError, OutputValidationError, EMOTIONAL_TAGS


# ═══════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════

def build_test_npc(**overrides) -> NPCDefinition:
    arc_states = [
        ArcState("distant", "疏离", "礼貌克制", 0.0,
                 [InfoLevel.L1], [SilenceStrategy.POLITE_REFUSAL], "平静"),
        ArcState("interested", "有兴趣", "多说话有温度", 0.3,
                 [InfoLevel.L1, InfoLevel.L2], [SilenceStrategy.DEFLECT], "平静"),
        ArcState("defensive", "防御", "紧张谨慎", -0.3,
                 [InfoLevel.L1, InfoLevel.L2], [SilenceStrategy.CHANGE_SUBJECT], "紧张-低"),
        ArcState("breakdown", "崩溃", "坦诚脆弱", 0.5,
                 [InfoLevel.L1, InfoLevel.L2, InfoLevel.L3, InfoLevel.L4], [], "悲伤-中"),
    ]
    arc_transitions = [
        ArcTransition("distant", "interested", "attitude>=0.15"),
        ArcTransition("interested", "defensive", "attitude<=-0.2"),
        # interested→breakdown: needs trust AND sadness, or very high trust
        ArcTransition("interested", "breakdown", "attitude>=0.5 AND emotion_contains=悲伤"),
        ArcTransition("interested", "breakdown", "attitude>=0.7"),
        ArcTransition("interested", "breakdown", "attitude>=0.5 AND emotion_contains=懊悔"),
        ArcTransition("distant", "defensive", "attitude<=-0.3"),
        ArcTransition("distant", "defensive", "emotion_contains=紧张"),
        ArcTransition("defensive", "breakdown", "attitude>=0.4"),
        ArcTransition("defensive", "breakdown", "emotion_contains=悲伤-中"),
        ArcTransition("defensive", "breakdown", "emotion_contains=悲伤-高"),
        ArcTransition("defensive", "breakdown", "emotion_contains=哀恸"),
        ArcTransition("defensive", "breakdown", "attitude>=0.3 AND emotion_contains=悲伤-中"),
        # Reverse (recovery) — harder thresholds, stronger first
        ArcTransition("defensive", "distant", "attitude>=0.5"),
        ArcTransition("defensive", "interested", "attitude>=0.3"),
        ArcTransition("breakdown", "interested", "attitude>=0.3"),
    ]
    knowledge = [
        KnowledgeEntry("f1", InfoLevel.L1, "我是画廊老板苏晚晴", "asked_directly"),
        KnowledgeEntry("f2", InfoLevel.L2, "死者最后一次来画廊时情绪异常激动", "asked_about_last_visit"),
        KnowledgeEntry("f3", InfoLevel.L2, "案发当晚我也在山庄，约了死者谈画展", "asked_about_night"),
        KnowledgeEntry("f4", InfoLevel.L3, "我和死者在三年前曾有过一段感情", "trust>=0.3"),
        KnowledgeEntry("f5", InfoLevel.L3, "死者的现任妻子曾经威胁过我", "trust>=0.5"),
        KnowledgeEntry("f6", InfoLevel.L4, "我曾打算在画展后永远离开这座城市", "trust>=0.7"),
    ]
    defaults = dict(
        npc_id="char_01", name="苏晚晴", age=30, occupation="画廊老板",
        character_anchor="温和克制，用词文雅。紧张时反而更安静。",
        personality=PersonalityMatrix(0.3, 0.1, 0.8, 0.7, "文雅克制"),
        self_awareness=SelfAwareness.NEVER_KNOWS, is_killer=False,
        knowledge=knowledge, relationships=[
            Relationship("char_03", RelationType.COMRADE, will_cover_for=True),
        ],
        default_silence_strategy=SilenceStrategy.POLITE_REFUSAL,
        silence_triggers=["涉及char_03"], arc_states=arc_states,
        arc_transitions=arc_transitions, initial_arc_state="distant",
    )
    defaults.update(overrides)
    return NPCDefinition(**defaults)


# ═══════════════════════════════════════════
# StateManager — Arc Transitions
# ═══════════════════════════════════════════

class TestArcTransitions:
    def test_attitude_accumulation_triggers_transition(self):
        """多个小幅度态度变化累积后应触发角色弧转移"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)
        assert state.current_arc_state == "distant"

        # Accumulate: 3 rounds of +0.05 → reaches 0.15 threshold
        for _ in range(3):
            sm.update_after_reply(npc_def, state, "user_001", {
                "emotional_tag": "平静",
                "info_revealed": [],
                "attitude_shift": "+0.05",
            })
        assert state.attitude_to_player == pytest.approx(0.15)
        assert state.current_arc_state == "interested"

    def test_very_high_trust_unlocks_breakdown(self):
        """极高信任(+0.7)无条件触发崩溃坦白"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "平静", "info_revealed": [], "attitude_shift": "+0.7",
        })
        assert state.current_arc_state == "breakdown"

    def test_trust_with_sadness_triggers_breakdown(self):
        """信任+悲伤触发崩溃"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "悲伤-中", "info_revealed": [], "attitude_shift": "+0.5",
        })
        assert state.current_arc_state == "breakdown"  # attitude>=0.5 AND 悲伤

    def test_negative_attitude_triggers_defensive(self):
        """负面态度累积触发防御状态"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)
        # First move to interested
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "平静", "info_revealed": [], "attitude_shift": "+0.2",
        })
        assert state.current_arc_state == "interested"

        # Then negative hits
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "紧张-低", "info_revealed": [], "attitude_shift": "-0.5",
        })
        assert state.attitude_to_player == pytest.approx(-0.3)
        assert state.current_arc_state == "defensive"

    def test_recursive_chain_transition(self):
        """递归链式转移：一次更新可触发多个连续的状态转移"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)

        # From distant, +0.5 triggers interested (>=0.15), then breakdown (>=0.5) in one chain
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "悲伤-中", "info_revealed": [], "attitude_shift": "+0.5",
        })
        assert state.attitude_to_player == pytest.approx(0.5)
        assert state.current_arc_state == "breakdown"

    def test_attitude_clamped_to_bounds(self):
        """态度值被限制在 -1.0 到 1.0 之间"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)

        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "平静", "info_revealed": [], "attitude_shift": "+2.0",
        })
        assert state.attitude_to_player == 1.0

        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "愤怒-高", "info_revealed": [], "attitude_shift": "-5.0",
        })
        assert state.attitude_to_player == -1.0

    def test_attitude_shift_with_chinese_description(self):
        """解析中文附带的态度变化描述"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)

        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "平静",
            "info_revealed": [],
            "attitude_shift": "+0.2，玩家展现了对我的信任",
        })
        assert state.attitude_to_player == pytest.approx(0.2)

    def test_no_transition_below_threshold(self):
        """未达到阈值时不触发转移"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)

        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "平静", "info_revealed": [], "attitude_shift": "+0.10",
        })
        assert state.attitude_to_player == pytest.approx(0.10)
        assert state.current_arc_state == "distant"  # No transition

    def test_emotion_trigger_transition(self):
        """情绪触发弧转移：紧张情绪→防御状态"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)

        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "紧张-低",
            "info_revealed": [],
            "attitude_shift": None,
        })
        assert state.current_arc_state == "defensive"  # emotion_contains=紧张

    def test_emotion_downturn_triggers_breakdown(self):
        """情绪低落触发崩溃坦白状态"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "紧张-低", "info_revealed": [], "attitude_shift": None,
        })
        assert state.current_arc_state == "defensive"
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "悲伤-中", "info_revealed": [], "attitude_shift": None,
        })
        assert state.current_arc_state == "breakdown"  # emotion_contains=悲伤-中

    def test_and_combined_trigger(self):
        """AND组合触发器：两个条件同时满足才触发"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)
        # Go to defensive first
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "紧张-低", "info_revealed": [], "attitude_shift": None,
        })
        assert state.current_arc_state == "defensive"
        # Only emotion, no attitude → should NOT trigger combined AND
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "悲伤-中", "info_revealed": [], "attitude_shift": None,
        })
        # Already breakdown from the standalone emotion_contains trigger
        assert state.current_arc_state == "breakdown"

    def test_recovery_from_defensive(self):
        """从防御恢复需要更高阈值，且可以逆转"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)
        # Go defensive via emotion
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "紧张-低", "info_revealed": [], "attitude_shift": None,
        })
        assert state.current_arc_state == "defensive"
        # +0.2 not enough (needs 0.3 for partial recovery to interested)
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "平静", "info_revealed": [], "attitude_shift": "+0.2",
        })
        assert state.current_arc_state == "defensive"  # Still stuck
        # +0.35 triggers defensive→interested (>=0.3), partial recovery
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "平静", "info_revealed": [], "attitude_shift": "+0.15",
        })
        assert state.current_arc_state == "interested"  # Partial recovery

    def test_full_recovery_to_polite(self):
        """完整恢复：态度>=0.5 从防御直接回到疏离"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "紧张-低", "info_revealed": [], "attitude_shift": None,
        })
        assert state.current_arc_state == "defensive"
        # Direct full recovery with 0.5 attitude
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "平静", "info_revealed": [], "attitude_shift": "+0.5",
        })
        # defensive→distant fires first, then may chain forward
        assert state.current_arc_state in ("distant", "interested", "breakdown")
        assert state.attitude_to_player == 0.5


# ============================================================
# StateManager — Fact Matching
# ═══════════════════════════════════════════

class TestFactMatching:
    def test_exact_content_match(self):
        """精确匹配：LLM返回的内容和知识条目完全一致"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)

        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "平静",
            "info_revealed": [{"level": "L1", "content": "我是画廊老板苏晚晴"}],
            "attitude_shift": None,
        })
        assert state.knowledge_map["f1"].released is True
        assert "user_001" in state.knowledge_map["f1"].released_to
        assert len(state.fact_ledger) == 1

    def test_substring_match(self):
        """子串匹配：LLM用自己的话表达了同一事实"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)

        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "平静",
            "info_revealed": [{"level": "L2", "content": "他最后一次来画廊时看起来情绪异常激动"}],
            "attitude_shift": None,
        })
        assert state.knowledge_map["f2"].released is True

    def test_keyword_overlap_match(self):
        """关键词重叠匹配：LLM重新组织语言但语义相同"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)

        # NPC says it in their own words
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "平静",
            "info_revealed": [{"level": "L2", "content": "那天晚上我也在山庄里面，约好了要谈画展的事"}],
            "attitude_shift": None,
        })
        assert state.knowledge_map["f3"].released is True

    def test_no_match_unrelated_content(self):
        """无关内容不应匹配到任何事实"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)

        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "平静",
            "info_revealed": [{"level": "L1", "content": "今天天气不错"}],
            "attitude_shift": None,
        })
        assert len(state.fact_ledger) == 0  # Nothing matched

    def test_multiple_reveals_in_one_reply(self):
        """一次回复透露多条信息"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)

        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "悲伤-中",
            "info_revealed": [
                {"level": "L1", "content": "我是画廊老板苏晚晴"},
                {"level": "L2", "content": "他最后一次来画廊情绪异常激动"},
            ],
            "attitude_shift": None,
        })
        assert state.knowledge_map["f1"].released is True
        assert state.knowledge_map["f2"].released is True
        assert len(state.fact_ledger) == 2

    def test_already_released_not_duplicated(self):
        """已公开的事实不会被重复记录"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)
        # First release
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "平静",
            "info_revealed": [{"level": "L1", "content": "我是画廊老板苏晚晴"}],
            "attitude_shift": None,
        })
        assert len(state.fact_ledger) == 1
        # Same info again
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "平静",
            "info_revealed": [{"level": "L1", "content": "我是画廊老板苏晚晴"}],
            "attitude_shift": None,
        })
        assert len(state.fact_ledger) == 1  # Not duplicated


# ═══════════════════════════════════════════
# OutputParser — Robustness
# ═══════════════════════════════════════════

class TestParserRobustness:
    def test_valid_output_parsed_correctly(self):
        """正常JSON输出解析正确"""
        parser = OutputParser()
        raw = '{"emotional_tag": "紧张-低", "info_revealed": [{"level": "L2", "content": "我在山庄"}], "attitude_shift": null}'
        data = parser.parse(raw)
        assert data["emotional_tag"] == "紧张-低"
        assert len(data["info_revealed"]) == 1
        assert data["info_revealed"][0]["content"] == "我在山庄"
        assert data["attitude_shift"] is None

    def test_markdown_json_still_works(self):
        """Markdown包裹的JSON仍可解析"""
        parser = OutputParser()
        raw = '好的。\n```json\n{"emotional_tag": "平静", "info_revealed": [], "attitude_shift": null}\n```'
        data = parser.parse(raw)
        assert data["emotional_tag"] == "平静"

    def test_missing_json_fallback_to_defaults(self):
        """缺少JSON时优雅降级"""
        parser = OutputParser()
        raw = "我不太清楚你在说什么。"
        data = parser.parse(raw, fallback_emotional_tag="紧张-中")
        assert data["emotional_tag"] == "紧张-中"
        assert data["info_revealed"] == []
        assert data["attitude_shift"] is None

    def test_malformed_json_fallback_to_defaults(self):
        """畸形JSON时优雅降级"""
        parser = OutputParser()
        raw = '{broken json!!!'
        data = parser.parse(raw, fallback_emotional_tag="平静")
        assert data["emotional_tag"] == "平静"

    def test_invalid_emotional_tag_auto_fixed(self):
        """无效情绪标签自动修正为平静"""
        parser = OutputParser()
        raw = '{"emotional_tag": "超级开心", "info_revealed": [], "attitude_shift": null}'
        data = parser.parse(raw)
        assert data["emotional_tag"] == "平静"  # Auto-fixed

    def test_invalid_info_level_auto_fixed(self):
        """无效信息层级自动修正为 L1"""
        parser = OutputParser()
        raw = '{"emotional_tag": "平静", "info_revealed": [{"level": "L5", "content": "test"}], "attitude_shift": null}'
        data = parser.parse(raw)
        assert data["info_revealed"][0]["level"] == "L1"

    def test_missing_fields_auto_filled(self):
        """缺少字段自动填充默认值"""
        parser = OutputParser()
        raw = '{"emotional_tag": "平静"}'
        data = parser.parse(raw)
        assert data["info_revealed"] == []
        assert data["attitude_shift"] is None

    def test_info_revealed_not_list_auto_fixed(self):
        """info_revealed 不是数组时自动修正"""
        parser = OutputParser()
        raw = '{"emotional_tag": "平静", "info_revealed": "some string", "attitude_shift": null}'
        data = parser.parse(raw)
        assert data["info_revealed"] == []  # Auto-fixed

    def test_string_info_auto_converted_to_dict(self):
        """字符串类型的info自动转换为dict"""
        parser = OutputParser()
        raw = '{"emotional_tag": "平静", "info_revealed": ["一段话"], "attitude_shift": null}'
        data = parser.parse(raw)
        assert isinstance(data["info_revealed"][0], dict)
        assert data["info_revealed"][0]["content"] == "一段话"


# ═══════════════════════════════════════════
# Fabrication Guard
# ═══════════════════════════════════════════

# ============================================================
# Deterministic Attitude Triggers
# ============================================================

# ============================================================
# Phase-gated confession
# ============================================================

class TestPhaseGating:
    def test_confession_blocked_in_act1(self):
        from src.engine import NPCsEngine
        assert not NPCsEngine._phase_allows_confession(GamePhase.ACT_1)

    def test_confession_blocked_in_act2(self):
        from src.engine import NPCsEngine
        assert not NPCsEngine._phase_allows_confession(GamePhase.ACT_2_DISCUSS)

    def test_confession_blocked_in_act3(self):
        from src.engine import NPCsEngine
        assert not NPCsEngine._phase_allows_confession(GamePhase.ACT_3_DISCUSS)

    def test_confession_allowed_in_act4(self):
        from src.engine import NPCsEngine
        assert NPCsEngine._phase_allows_confession(GamePhase.ACT_4_VOTE)

    def test_confession_allowed_in_finished(self):
        from src.engine import NPCsEngine
        assert NPCsEngine._phase_allows_confession(GamePhase.FINISHED)


class TestAttitudeTriggers:
    def test_accusation_triggers_negative(self):
        """直接指控触发负态度"""
        from src.engine import NPCsEngine
        engine = NPCsEngine()
        result = engine._detect_attitude_trigger("我觉得你就是凶手", build_test_npc())
        assert result is not None
        assert "-" in result

    def test_trust_triggers_positive(self):
        """信任表达触发正态度"""
        from src.engine import NPCsEngine
        engine = NPCsEngine()
        result = engine._detect_attitude_trigger("我相信你不是那种人", build_test_npc())
        assert result is not None
        assert "+" in result

    def test_neutral_message_no_trigger(self):
        """中性消息不触发"""
        from src.engine import NPCsEngine
        engine = NPCsEngine()
        result = engine._detect_attitude_trigger("你喜欢什么颜色", build_test_npc())
        assert result is None

    def test_insult_triggers_negative(self):
        """辱骂触发负态度（值取决于NPC性格）"""
        from src.engine import NPCsEngine
        engine = NPCsEngine()
        result = engine._detect_attitude_trigger("你滚开", build_test_npc())
        assert result is not None
        assert "-" in result
        assert "辱骂" in result

    def test_first_match_wins(self):
        """匹配第一个关键词即返回"""
        from src.engine import NPCsEngine
        engine = NPCsEngine()
        result = engine._detect_attitude_trigger("你这个凶手，一直在撒谎", build_test_npc())
        assert result is not None

    def test_compliment_triggers_positive(self):
        """赞美触发正态度"""
        from src.engine import NPCsEngine
        engine = NPCsEngine()
        result = engine._detect_attitude_trigger("你真是个艺术家", build_test_npc())
        assert result is not None
        assert "+" in result

    def test_fiery_npc_reacts_stronger(self):
        """暴躁NPC对辱骂反应更激烈"""
        from src.engine import NPCsEngine
        engine = NPCsEngine()
        gentle = build_test_npc()  # aggression=0.1
        fiery = build_test_npc()
        fiery.personality.aggression = 0.9
        fiery.personality.rationality = 0.2

        r1 = engine._detect_attitude_trigger("你滚开", gentle)
        r2 = engine._detect_attitude_trigger("你滚开", fiery)

        d1 = float(r1.split("，")[0])
        d2 = float(r2.split("，")[0])
        assert abs(d2) > abs(d1), f"暴躁NPC应反应更激烈: {d2} vs {d1}"


class TestFabricationGuard:
    def test_no_inferred_no_correction(self):
        """没有 inferred 内容时不触发矫正"""
        from src.engine import NPCsEngine
        engine = NPCsEngine()
        parsed = {"info_revealed": [{"content": "真实信息", "level": "L1"}]}
        corrected, orig = engine._guard_fabrication(
            parsed, "我是画廊老板。", build_test_npc(), None
        )
        assert corrected == ""
        assert orig == ""
        assert len(parsed["info_revealed"]) == 1

    def test_inferred_triggers_correction(self):
        """检测到 inferred 内容时触发矫正，剔除编造项"""
        from src.engine import NPCsEngine
        engine = NPCsEngine()
        parsed = {
            "info_revealed": [
                {"content": "真实信息", "level": "L1"},
                {"content": "编造的内容", "level": "L1", "inferred": True},
                {"content": "也是编造的", "level": "L1", "inferred": True},
            ]
        }
        corrected, orig = engine._guard_fabrication(
            parsed, "我昨天去了那里，还看到了...", build_test_npc(), None
        )
        assert corrected != ""  # Should return evasion text
        assert orig != ""      # Should return original reply
        assert len(parsed["info_revealed"]) == 1  # Inferred items stripped
        assert parsed["info_revealed"][0]["content"] == "真实信息"

    def test_killer_skips_guard(self):
        """凶手 NPC 跳过编造检测（允许在辐射范围内说谎）"""
        from src.engine import NPCsEngine
        engine = NPCsEngine()
        killer = build_test_npc(is_killer=True, self_awareness=SelfAwareness.KNOWS_IS_KILLER)
        parsed = {
            "info_revealed": [
                {"content": "谎言", "level": "L1", "inferred": True},
            ]
        }
        corrected, orig = engine._guard_fabrication(parsed, "谎言回复", killer, None)
        assert corrected == ""  # Killer bypasses guard
        assert orig == ""

    def test_evasion_replacement_non_empty(self):
        """替换话术不能为空（HARD_SILENCE除外）"""
        from src.engine import NPCsEngine, EVASION_TEMPLATES
        engine = NPCsEngine()
        parsed = {"info_revealed": [{"content": "x", "inferred": True}]}
        npc = build_test_npc()
        npc.default_silence_strategy = SilenceStrategy.POLITE_REFUSAL

        corrected, _ = engine._guard_fabrication(parsed, "test reply", npc, None)
        assert len(corrected) > 0  # Must not be empty

    def test_fidelity_low_triggers_correction(self):
        """核心事实被改写（fidelity_low）也触发矫正"""
        from src.engine import NPCsEngine
        engine = NPCsEngine()
        parsed = {
            "info_revealed": [
                {"content": "死者最后一次来时情绪异常激动", "fidelity_low": True},
                {"content": "死者生前常来画廊", "fidelity_low": False},
            ]
        }
        corrected, orig = engine._guard_fabrication(parsed, "test", build_test_npc(), None)
        assert corrected != ""  # Triggered by fidelity_low
        # Good item kept, bad item stripped
        assert len(parsed["info_revealed"]) == 1
        assert parsed["info_revealed"][0]["content"] == "死者生前常来画廊"

    def test_fidelity_low_and_inferred_both_stripped(self):
        """fidelity_low 和 inferred 同时存在时都被剔除"""
        from src.engine import NPCsEngine
        engine = NPCsEngine()
        parsed = {
            "info_revealed": [
                {"content": "a", "fidelity_low": True},
                {"content": "b", "inferred": True},
                {"content": "c"},
            ]
        }
        corrected, orig = engine._guard_fabrication(parsed, "test", build_test_npc(), None)
        assert corrected != ""
        assert len(parsed["info_revealed"]) == 1
        assert parsed["info_revealed"][0]["content"] == "c"


# ═══════════════════════════════════════════
# Topic Hit Detection
# ═══════════════════════════════════════════

class TestTopicHit:
    def test_hit_on_blocked_fact_keywords(self):
        """玩家问题包含封锁事实的关键词时触发碰撞"""
        from src.prompt import ContextAssembler
        assembler = ContextAssembler()
        # Player asks about "last night" + "banquet" → hits L2 "案发当晚我也在山庄"
        result = assembler._topic_hit("您去了昨晚的晚宴吗", "案发当晚我也在山庄")
        assert result is True

    def test_hit_on_location_question(self):
        """玩家问"在山庄"相关时触发碰撞"""
        from src.prompt import ContextAssembler
        assembler = ContextAssembler()
        result = assembler._topic_hit("昨晚你在这座山庄里吗", "案发当晚我也在山庄")
        assert result is True

    def test_no_hit_on_unrelated_question(self):
        """无关问题不触发碰撞"""
        from src.prompt import ContextAssembler
        assembler = ContextAssembler()
        result = assembler._topic_hit("你喜欢什么颜色", "案发当晚我也在山庄")
        assert result is False

    def test_no_hit_on_too_short_match(self):
        """偶然重叠一两个字不触发（如'我''的'等已被过滤的常见字）"""
        from src.prompt import ContextAssembler
        assembler = ContextAssembler()
        result = assembler._topic_hit("我也喜欢", "案发当晚我也在山庄")
        # "我也" 只有两个字，命中率不够30%阈值
        assert result is False

    def test_hit_on_threat_topic(self):
        """问威胁相关时触发碰撞"""
        from src.prompt import ContextAssembler
        assembler = ContextAssembler()
        result = assembler._topic_hit("死者的妻子是不是威胁过你", "死者的现任妻子曾经威胁过我")
        assert result is True


# ═══════════════════════════════════════════
# StateManager — init_npc_state
# ═══════════════════════════════════════════

class TestNPCStateInit:
    def test_init_sets_correct_arc_state(self):
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)
        assert state.current_arc_state == "distant"
        assert state.emotional_tag == "平静"
        assert state.attitude_to_player == 0.0
        assert len(state.knowledge_map) == 6

    def test_init_copies_knowledge_without_mutation(self):
        """初始化状态是定义的副本，不会互相影响"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)
        state.knowledge_map["f1"].released = True
        # Original definition should be unaffected
        original = next(k for k in npc_def.knowledge if k.fact_id == "f1")
        assert original.released is False


# ═══════════════════════════════════════════
# Edge cases
# ═══════════════════════════════════════════

class TestEdgeCases:
    def test_empty_info_revealed_noop(self):
        """空 info_revealed 不会有任何操作"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)
        count_before = len(state.fact_ledger)
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "平静", "info_revealed": [], "attitude_shift": None,
        })
        assert len(state.fact_ledger) == count_before

    def test_none_attitude_shift_noop(self):
        """None 态度变化不会有任何操作"""
        sm = StateManager()
        npc_def = build_test_npc()
        state = sm.init_npc_state(npc_def)
        sm.update_after_reply(npc_def, state, "user_001", {
            "emotional_tag": "紧张-低", "info_revealed": [], "attitude_shift": None,
        })
        assert state.attitude_to_player == 0.0

    def test_killer_npc_honesty_mode(self):
        """凶手NPC的诚实度模式不影响状态管理逻辑"""
        killer = build_test_npc(is_killer=True, self_awareness=SelfAwareness.KNOWS_IS_KILLER)
        sm = StateManager()
        state = sm.init_npc_state(killer)
        # Core state management should work the same
        sm.update_after_reply(killer, state, "user_001", {
            "emotional_tag": "紧张-中",
            "info_revealed": [{"level": "L1", "content": "我是画廊老板苏晚晴"}],
            "attitude_shift": "-0.1",
        })
        assert state.emotional_tag == "紧张-中"
        assert state.attitude_to_player == pytest.approx(-0.1)
