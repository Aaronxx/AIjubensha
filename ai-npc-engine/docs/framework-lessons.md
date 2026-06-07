# 框架经验总结 — 从测试中提取的设计规则

> 来源：苏晚晴（非凶手）和 周明远（凶手）的 100+ 轮对话测试
> 状态：已固化到框架中

---

## 0. 知识层级原则

### 问题
- "投资分歧"被标为 L3，实际上圈内人都知道，应属于 L2
- "争吵"才是需要信任才能说出的敏感信息，应属于 L3

### 分级标准
| 层级 | 定义 | 示例 |
|------|------|------|
| L1 | 公开身份，第一句对话就能说的 | "我是周明远，做艺术品投资的" |
| L2 | 调查中自然会发现的客观事实 | "投资方向有分歧""资金紧张想卖画" |
| L3 | 需要建立信任才愿意说的敏感信息 | "当晚我们激烈争吵""他曾威胁过我" |
| L4 | 只有崩溃/认罪时才说的核心秘密 | "是我杀了他" |

### 判定口诀
> 如果圈内人/目击者/商业伙伴可能知道 → L2
> 如果只有当事人双方知道、且当事人不愿意说 → L3
> 如果只有凶手自己知道 → L4

---

## 1. 事实管理

### 问题
- NPC 将"画廊里情绪激动"嫁接到"晚宴上"（时间/地点混淆）
- NPC 把"情绪异常激动"改写为"心事重重"（核心判断被削弱）
- NPC 随口编造"那幅蓝色油画的作者常来"（自由发挥无约束）

### 框架级方案
| 方案 | 位置 |
|------|------|
| KnowledgeEntry 新增 `time_label` / `location_label` 字段 | `models.py` |
| Prompt 中自动展示"（上周四·画廊）"格式标签 | `prompt.py:ContextAssembler` |
| 提取模型检测 `fidelity_low`——事实被改写时触发矫正 | `prompt.py:ExtractionPromptBuilder` |
| Prompt 红线："不同时间/地点的事实不可混淆" | `prompt.py:DialoguePromptBuilder` |
| ScriptValidator 警告缺少标签的 L2+ 事实 | `script_validator.py` |

---

## 2. 编造防御

### 问题
- NPC 被问封锁话题时编造借口（"我本来要去但临时有事"）
- 提取模型（也是LLM）不可靠——derived 检测有盲区
- Prompt 规则是软约束，无法100%阻止

### 框架级方案
| 方案 | 位置 |
|------|------|
| 关键词碰撞检测——玩家消息触碰封锁事实时插入强制回避指令 | `prompt.py:_topic_hit` |
| 区分分幕封锁（硬回避）vs 角色弧封锁（软提示） | `prompt.py:critical_block` |
| 编造检测兜底——提取模型标记 `inferred`/`fidelity_low`→替换为回避话术 | `engine.py:_guard_fabrication` |
| 沉默策略提示全部加入"绝不编造借口" | `prompt.py:SILENCE_HINTS` |

---

## 3. 情绪系统

### 问题
- 4维度×3等级太粗糙，无法表达复杂情绪
- "低落-低"就能触发崩溃（门槛太低）
- 无法表达"既紧张又悲伤"的复合情绪

### 框架级方案
| 方案 | 位置 |
|------|------|
| GoEmotions风格15类别：焦虑/愤怒/悲伤/积极4簇 | `models.py:EmotionCategory` |
| 3级强度："悲伤-低"/"悲伤-中"/"悲伤-高" | `prompt.py:EMOTIONAL_TAGS` |
| 复合情绪："紧张-中,悲伤-低" | `prompt.py:ExtractionPromptBuilder` |
| 崩溃门槛提高到"悲伤-中"或"哀恸" | `test_engine.py:arc_transitions` |
| ScriptValidator 警告"悲伤"（无等级）触发崩溃 | `script_validator.py` |

---

## 4. 态度系统

### 问题
- 赞美/艺术话题不触发态度变化
- 被指控"凶手"态度纹丝不动
- 辱骂后态度仍为正数
- 不同性格NPC反应一样

### 框架级方案
| 方案 | 位置 |
|------|------|
| 确定性关键词触发器——不依赖LLM，直接检测玩家消息 | `engine.py:STIMULUS_KEYWORDS` |
| 6种刺激类型：指控/辱骂/质疑/信任/赞美/感谢 | `engine.py:_detect_attitude_trigger` |
| 人格驱动反应曲线——aggression×rationality 决定delta | `models.py:PersonalityMatrix.attitude_profile` |
| 连续同向刺激累积放大1.3x | `engine.py:_detect_attitude_trigger` |
| 人格驱动行为倾向自动注入Prompt | `prompt.py:_personality_augment` |

---

## 5. 弧状态管理

### 问题
- 一句"节哀"就崩溃（门槛太低）
- 进入防御后无法恢复
- killer前3幕就认罪

### 框架级方案
| 方案 | 位置 |
|------|------|
| 崩溃需信任+悲伤组合条件（或attitude>=0.7） | `test_engine.py:arc_transitions` |
| 恢复路径——更高阈值，但可逆转 | `state_manager.py:_check_arc_transitions` |
| 分幕认罪封锁——引擎层硬拦截 | `engine.py:_phase_allows_confession` |
| 弧转移链中阻止回退循环 | `state_manager.py:visited` |
| ScriptValidator 检查所有状态可达性 | `script_validator.py` |

---

## 6. NPC人格模板

### 问题
- 每个NPC手工配置200+行代码
- 凶手和温和NPC用同样的arc transition

### 框架级方案
| 模板 | 特征 | 适用 |
|------|------|------|
| `gentle_non_killer` | 温和、理性、慢崩溃 | 大多数非凶手NPC |
| `hardened_killer` | 高理性、善伪装、死不认罪 | 全知型凶手 |
| `timid_bystander` | 胆小、容易吓、快速坦白 | 目击者/知情者 |
| `fiery_suspect` | 暴躁、爆发快恢复也快 | 有嫌疑但非真凶 |

位置：`src/npc_factory.py`
