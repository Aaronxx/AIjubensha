# AI推理叙事游戏 - 游戏流程页面 Figma Make 提示词

> 基于 PRD v1.6 游戏流程设计
> 设计风格：暗黑科技 + 霓虹金主色 + 不对称布局

---

## 设计规范（复用统一设计语言）

### 色彩系统
| 类型 | 色值 | 用途 |
|------|------|------|
| 背景主色 | #0A0E17 | 页面主背景 |
| 背景深色 | #06080D | 卡片/模块背景 |
| 背景浅色 | #111827 | 次级背景 |
| 霓虹金 | #C9A96E | **唯一强调色** |
| 霓虹蓝 | #4A7DFF | 科技元素/链接 |
| 霓虹粉 | #E0556A | 警告/危险 |
| 霓虹绿 | #4CAF93 | 成功/完成状态 |
| 文字主色 | #E8ECF1 | 主要文字 |
| 文字副色 | #8B95A5 | 次要文字 |
| 边框色 | #1A2744 | 分割线/卡片边框 |

### 字体系统
- **Display**: Cabinet Grotesk / SF Pro 24px 700
- **正文**: Satoshi / PingFang SC 14px 400
- **小字**: Satoshi / PingFang SC 12px 400
- **数字**: JetBrains Mono 10px 400

### 组件风格
- 卡片圆角: 12px
- 按钮圆角: 8px
- 标签圆角: 6px
- 头像: 50% 圆形

---

## 游戏流程页面总览

根据 PRD 定义的 8 个环节，共需设计 **15 个页面**：

| 序号 | 页面名称 | 对应环节 | 页面类型 |
|------|---------|---------|---------|
| 1 | 个人准备页 | 前置环节 | 视频播放+身份确认 |
| 2 | 个人身份卡 | 前置环节 | 弹出式身份面板 |
| 3 | 第一幕-轮流发言 | 第一环节 阶段A/B | 群聊+发言控制 |
| 4 | 第一幕-自由交流 | 第一环节 阶段C | 群聊+次数限制 |
| 5 | 第一轮搜证 | 第二环节 | AP分配+线索发现 |
| 6 | 第二幕-集中讨论 | 第三环节 | 群聊+证据展示+私聊 |
| 7 | 侦探投票 | 第四环节 | 单独投票面板 |
| 8 | 第二轮搜证 | 第五环节 | AP分配+深层线索 |
| 9 | 第三幕-最终讨论 | 第六环节 | 群聊+焦点收窄 |
| 10 | 全员最终投票 | 第七环节 | 投票选择面板 |
| 11 | 投票结果公示-A | 第八环节 阶段A | 安全公布动画 |
| 12 | 投票结果公示-B | 第八环节 阶段B/C | 悬念揭晓面板 |
| 13 | 结局短剧播放 | 第八环节 阶段D | 视频播放器 |
| 14 | 蝴蝶效应复盘 | 第八环节 阶段E | 因果图可视化 |
| 15 | 单局战绩详情 | 游戏结束 | 数据总结面板 |

---

## 页面提示词

### 1. 个人准备页

**页面名称：** 游戏个人准备 - 开场短剧播放
**对应环节：** 前置环节（限时5分钟）
**用途：** 播放角色专属开场短剧，确认身份后进入第一幕

**提示词：**
```
Create a mobile app game preparation screen with video playback, dark tech style, gold accent.

Design Read: Dark mode mobile game app, cinematic feel with gold (#C9A96E) accent, immersive atmosphere for mystery narrative.

Layout structure (top to bottom):

1. Top status bar - Compact overlay:
   - "个人准备阶段" (12px, gold)
   - Countdown timer: "04:32" (mono, white, prominent)
   - "全员等待中..." (11px, gray, with 3 dots animation)

2. Video player area - Large central area (60% of screen):
   - 16:9 video placeholder
   - Dark gradient overlay (bottom)
   - Play/pause controls (minimal)
   - Progress bar (thin, gold fill)
   - "角色专属 · 苏晚晴" badge (top-left, semi-transparent bg)
   - Skip forward/backward buttons (10s)

3. Character info overlay - Bottom of video area:
   - Character name: "苏晚晴" (18px, gold, Cabinet Grotesk)
   - Role tag: "画廊老板 · 30岁" (11px, gray)
   - Short description: "那晚我确实在画廊..." (13px, white, max 2 lines)

4. Action buttons - Fixed bottom:
   - "我的身份" button (secondary, outline, opens identity card)
   - "已确认" button (primary, gold fill, large)
   - Auto-confirm warning: "超时将自动进入下一环节" (11px, gray)

5. Ready status - Top-right overlay:
   - Player avatars row (4-6 circles)
   - Green checkmark for confirmed players
   - Spinning loader for unconfirmed
   - "3/6 已确认" (mono, 11px)

Technical specs:
- Screen: 390x844px
- Background: #0A0E17
- Video area: dark gradient overlay
- Gold accent for CTA and timer
- Cinematic atmosphere, no neon effects
- Left-aligned text, no centered hero
- Countdown timer prominent (urgency feel)
- Player status overlay compact
```

---

### 2. 个人身份卡

**页面名称：** 个人身份信息面板
**对应环节：** 前置环节（点击"我的身份"弹出）
**用途：** 查看自己的身份背景、秘密、目标，防止忘记

**提示词：**
```
Create a mobile app identity card popup screen, dark tech style, gold accent.

Layout:

1. Header - Top bar of popup:
   - "我的身份" title (16px, gold)
   - Close button (X, right)
   - Subtle divider line

2. Character profile - Upper section:
   - Large circular avatar (64px, colored border)
   - Character name: "苏晚晴" (20px, white, Cabinet Grotesk)
   - Role: "画廊老板 · 30岁" (13px, gray)
   - "你的秘密" badge (pink, small, top-right of avatar)

3. Background story - Expandable card:
   - "背景故事" header (14px, gold)
   - Paragraph text (13px, white, 2-3 lines)
   - "展开" link (gold, right)

4. Initial relationships - List:
   - "初始关系" header (14px, gold)
   - 4 relationship rows:
     * Avatar + name + relationship tag (同事/情人/陌生人)
     * Colored tag per relationship type
   - Scrollable if more than 4

5. Personal objectives - Card:
   - "个人目标" header (14px, gold)
   - Primary objective: "找到杀害老板的真凶" (13px, white)
   - Secondary objective: "隐瞒与死者的债务纠纷" (13px, gray)
   - Red line: "绝不承认挪用公款" (13px, pink)

6. Secret section - Highlighted card:
   - "个人秘密" header (14px, pink accent)
   - Warning icon
   - Secret text (13px, white)
   - "此信息仅你可见，不可向其他玩家透露" (11px, gray, italic)

7. Bottom action - Compact:
   - "关闭" button (secondary, full-width)
   - "返回游戏" button (primary, gold, full-width)

Specs:
- 390x844px (full screen modal)
- Card sections: 12px radius, #111827 bg
- Gold for headers, pink for secrets
- Left-aligned content
- Scrollable main content
- No centered hero
```

---

### 3. 第一幕-轮流发言

**页面名称：** 第一幕轮流发言 - 侦探开场+轮流自述
**对应环节：** 第一环节 阶段A/B
**用途：** 侦探开场后，按顺序轮流发言，不可插话

**提示词：**
```
Create a mobile app group chat screen with turn-based speaking control, dark tech style.

Layout:

1. Game header - Top bar:
   - Back to menu icon (left)
   - "第一幕 · 暗流涌动" (15px, gold)
   - Phase timer: "剩余 22:15" (mono, 12px, blue)
   - Menu icon (right, settings)

2. Phase indicator - Compact banner below header:
   - "阶段B: 轮流发言" (13px, gold)
   - "当前: 陈警官发言" (12px, white)
   - "限时 02:45" (mono, 11px, countdown)
   - "不可插话" warning tag (pink, small)

3. Chat messages - Scrollable area (main):
   - System message: "侦探开场已结束" (centered, gray, italic)
   - NPC messages (left-aligned):
     * Avatar (40px circle) + colored name + message bubble
     * #1A1F2E bubble bg, white text
   - Player messages (right-aligned):
     * Avatar + name + #4A7DFF bubble, white text
   - Turn marker: "--- 陈警官 发言中 ---" (centered, gold, 11px)
   - 5-6 messages visible

4. Speaking queue - Bottom overlay (above input):
   - Horizontal scroll of player avatars (6 circles, 32px)
   - Current speaker: gold ring around avatar
   - Completed: green checkmark overlay
   - Upcoming: gray overlay
   - "3/6 已发言" (mono, 11px, right side)

5. Input area - Fixed bottom:
   - Text input (8px radius, dark bg)
   - Send button (circular, disabled - waiting for turn)
   - "等待你的发言顺序..." placeholder (gray)
   - Private chat icon (small, left)

6. Skip vote (detective only) - If detective:
   - "跳过本阶段" button (small, outline, gold)
   - Voting status: "0/5 同意" (11px, gray)

Specs:
- 390x844px
- Message bubbles: 12px radius
- Speaking queue: horizontal scroll, overlay
- Current turn: gold highlight
- Input disabled when not your turn
- Phase indicator prominent
- Left-aligned chat messages
- NO neon effects
```

---

### 4. 第一幕-自由交流

**页面名称：** 第一幕自由交流 - 限时讨论
**对应环节：** 第一环节 阶段C
**用途：** 自由发言，每人15次机会，对单人最多3次追问

**提示词：**
```
Create a mobile app group chat screen with free discussion limits, dark tech style.

Layout:

1. Game header - Same as page 3:
   - "第一幕 · 暗流涌动" (gold)
   - "剩余 06:32" (blue, mono)

2. Phase indicator:
   - "阶段C: 自由交流" (13px, gold)
   - "自由发言模式" tag (green, small)

3. Limit status bar - Below phase:
   - Left: "你的发言次数: 8/15" (mono, 12px)
   - Right: "追问限制: 对单人最多3次" (11px, gray)
   - Progress bar (thin, gold fill for used)

4. Chat messages - Scrollable (main):
   - Mixed NPC and player messages
   - System messages for limit warnings:
     * "⚠️ 你对此玩家的追问已达2/3" (centered, pink, 11px)
   - 6-8 messages visible
   - Typing indicator: "苏晚晴 正在输入..." (12px, gray)

5. Quick actions - Floating above input:
   - "发起私聊" button (small, outline, blue)
   - "发起跳过投票" button (small, outline, gold) - detective only
   - Auto-hide after 3 seconds

6. Input area - Fixed bottom:
   - Text input (8px radius)
   - Send button (circular, gold, active)
   - Remaining count: "剩余 7 次" (11px, mono, above input)
   - Private chat icon (left)
   - Evidence attach icon (paperclip)

Specs:
- 390x844px
- Limit status prominent
- Warning messages for approaching limits
- Active input (gold send button)
- Quick actions floating, auto-hide
- NO centered content
```

---

### 5. 第一轮搜证

**页面名称：** 第一轮搜证 - AP分配调查
**对应环节：** 第二环节（限时10分钟）
**用途：** 分配15 AP到调查目标，发现L1-L2线索

**提示词：**
```
Create a mobile app evidence investigation screen with AP allocation, dark tech style, gold accent.

Design Read: Investigation/inquiry UI, tactical feel with gold accent, clear data presentation for action points and investigation targets.

Layout structure:

1. Header - Top bar:
   - Back to game arrow (left)
   - "第一轮搜证" (15px, white, Cabinet Grotesk)
   - Timer: "08:42" (blue, mono, 12px)
   - AP counter badge: "AP 7/15" (gold bg, dark text, prominent)

2. AP allocation zone - Upper section:
   - "分配你的调查行动点" header (14px, gold)
   - AP pool visualization: 15 slots (7 filled gold, 8 empty)
   - "点击目标投入AP" helper text (12px, gray)

3. Location cards - Scrollable vertical:

   Location 1: "死者房间" (expanded):
   - Location icon + name (14px, white)
   - "已搜查 2/3 目标" (11px, gray)
   - Investigation targets list:
     a) "尸体周围区域"
        - AP cost: 2 | Invested: 2 ✅
        - Progress bar: 100% filled (green)
        - Clues discovered: "致命伤口", "血迹方向"
        - Status: "已完成" (green check)
     b) "个人物品"
        - AP cost: 2 | Invested: 1
        - Progress bar: 50% (gold partial fill)
        - "调查" button (gold outline, small)
        - Status: "调查中..."
     c) "隐藏空间"
        - AP cost: 3 | Invested: 0
        - Progress bar: 0% (empty)
        - Button: "🔒 需要线索解锁" (disabled, gray)
        - Lock condition: "需要先发现『可疑的暗门』线索"

   Location 2: "客厅公共区域" (collapsed):
   - Icon + name + "未搜查" tag
   - Tap to expand
   - Preview: "3个调查目标" (11px, gray)

4. Hint card - Highlighted between locations:
   - Light gold bg tint
   - "💡" icon (20px)
   - "NPC 赵医生提到: 『死者的日记本最近不见了』" (13px)
   - "→ 可以在 NPC B 房间里寻找" (12px, gold)
   - Arrow pointer icon

5. Bottom actions - Fixed:
   - "结束搜证" button (secondary, outline, 40% width)
   - "确认完成" button (primary, gold, 60% width)

Specs:
- 390x844px
- AP counter prominent in header
- Progress bars: 4px height, rounded
- Location cards: 12px radius, #111827 bg
- Gold for active/invested elements
- Green for completed
- Locked items: gray, disabled
- Hint card: gold border, warm tint bg
- Left-aligned content
- NO neon outer glows
```

---

### 6. 第二幕-集中讨论

**页面名称：** 第二幕集中讨论 - 证据展示+私聊
**对应环节：** 第三环节（限时30分钟）
**用途：** 自由发言+证据展示，诚实度规则启用，可发起私聊

**提示词：**
```
Create a mobile app group chat screen with evidence sharing and private chat features, dark tech style.

Layout:

1. Game header:
   - "第二幕 · 暗流涌动" (15px, gold)
   - "剩余 24:18" (blue, mono)

2. Phase indicator:
   - "集中讨论" (13px, gold)
   - "诚实度规则已启用" tag (green, small)
   - "可公开线索" badge (blue, small)

3. Evidence tray - Horizontal scroll above chat:
   - "你的线索" header (12px, gray)
   - 4-5 clue chips (horizontal scroll):
     * Each: icon + short name (11px)
     * Gold border for unshared
     * Green bg for already shared
     * Tap to share to chat
   - "点击分享线索到群聊" helper (11px, gray)

4. Chat messages - Scrollable (main):
   - Mixed messages with evidence tags:
     * "陈警官分享了线索: [致命伤口]" (system, centered)
     * NPC response with clue reference
     * Player message with question
   - NPC messages showing tension:
     * "苏晚晴" (name in colored text)
     * "那个...我确实看到过那个日记本，不过没在意" (13px)
     * [诚实度: 回避策略触发] tag (pink, small, 10px)
   - 6-8 messages visible

5. Private chat quick access - Floating:
   - "私聊" button (compact, blue)
   - Expands to show NPC avatars (6 circles, 28px)
   - Tap to start 1-on-1 private conversation

6. Input area - Fixed bottom:
   - Text input
   - Send button (gold, active)
   - Evidence attach (paperclip, opens clue selector)
   - Private chat toggle (left)

Specs:
- 390x844px
- Evidence tray: horizontal scroll, chips
- Shared evidence: green indicator
- Unshared evidence: gold border
- Honesty tags: pink, small
- Private chat: compact avatar row
- Left-aligned chat
- Tension atmosphere (no playful elements)
```

---

### 7. 侦探投票

**页面名称：** 侦探单独中期投票
**对应环节：** 第四环节（限时3分钟）
**用途：** 仅侦探投票，结果不公开，作为中期判断记录

**提示词：**
```
Create a mobile app detective voting screen (solo vote, mid-game), dark tech style, tense atmosphere.

Layout:

1. Header:
   - "侦探中期投票" (15px, gold)
   - "仅限侦探" tag (gold, small)
   - Timer: "02:45" (blue, mono)

2. Privacy notice - Banner:
   - "🔒 你的投票结果仅自己可见" (13px, white)
   - "此投票不影响最终结果，仅作为中期判断" (12px, gray)
   - Dark card bg, subtle border

3. Suspect cards - Vertical list:

   Each suspect card (6 cards):
   - Avatar (48px circle)
   - Name (14px, white)
   - Role tag (画廊老板/投资人/警察) (11px, gray)
   - Evidence summary: "被提及3次 · 回避2次" (11px, blue)
   - Suspicion meter: "可疑度 █████░░ 70%" (mono, colored bar)
   - Select button (circle, empty when unselected)

   Selected state:
   - Gold ring around avatar
   - Button filled gold with checkmark
   - Card border: gold

4. Vote reasoning - Text area (optional):
   - "投票理由（选填）" header (12px, gray)
   - Text input (compact, 2 lines max)
   - Placeholder: "记录你的判断依据..."

5. Bottom actions:
   - "确认投票" button (primary, gold, full-width)
   - Disabled until a suspect is selected

Specs:
- 390x844px
- Suspect cards: 12px radius, #111827 bg
- Suspicion bars: 4px height
- Selected: gold highlight
- Privacy notice prominent
- Solo vote feel (no other player indicators)
- Tense, serious atmosphere
- Left-aligned content
```

---

### 8. 第二轮搜证

**页面名称：** 第二轮搜证 - 深层线索探索
**对应环节：** 第五环节（限时10分钟）
**用途：** 分配20 AP，发现L3深层线索，对话解锁的新目标出现

**提示词：**
```
Create a mobile app second round evidence investigation screen, deeper investigation, dark tech style.

Layout:

1. Header:
   - "第二轮搜证" (15px, white)
   - Timer: "07:23" (blue, mono)
   - AP badge: "AP 12/20" (gold, prominent)

2. Round comparison - Compact banner:
   - "本轮AP: 20（第一轮15）" (12px, gray)
   - "新解锁调查目标: 3个" (12px, gold)
   - Arrow icon

3. New targets section - Highlighted:
   - "新解锁目标" header (14px, gold, with sparkle icon)
   - New target card:
     * "🔓 NPC B 的私人房间"
     * "通过对话解锁" tag (blue, small)
     * "NPC A 的供词提到了B的异常行为"
     * AP cost: 3
     * "调查" button (gold, active)

4. Location cards (expanded depth):

   Location: "死者房间" (re-investigate):
   - Previously completed targets: green checkmarks
   - New unlocked target:
     * "隐藏的暗格"
     * AP cost: 4 (high cost indicator)
     * "需要: 『可疑的暗门』+ 『日记本缺页』"
     * Conditions met: ✅
     * "深入调查" button (gold, prominent)
   - L3 tag on deep targets (purple-ish, small)

   Location: "书房":
   - All targets uninvestigated
   - Preview visible: "书桌", "书架", "保险箱"
   - Insurance locked: need key clue

5. Clue chain visualization - Mini diagram:
   - "线索链" header (12px, gray)
   - Flow: 对话→目标A→线索X→目标B→L3证据
   - Current position highlighted
   - "发现更多线索可解锁新目标" (11px, gray)

6. Bottom actions:
   - "结束搜证" (secondary)
   - "确认完成" (primary, gold)

Specs:
- 390x844px
- New targets: gold border, highlighted
- L3 targets: special tag indicator
- Clue chain: thin lines, connected dots
- Higher AP costs for deep targets
- More locked items than round 1
- Sense of progression (more content unlocked)
- Left-aligned content
```

---

### 9. 第三幕-最终讨论

**页面名称：** 第三幕最终讨论 - 焦点收窄逼问
**对应环节：** 第六环节（限时30分钟）
**用途：** 焦点收窄到2-3嫌疑人，L3条件释放，撒谎NPC可能露馅

**提示词：**
```
Create a mobile app final discussion screen with narrowed focus, tense atmosphere, dark tech style.

Layout:

1. Header:
   - "第三幕 · 终局逼近" (15px, gold)
   - "最终讨论" tag (pink, small)
   - Timer: "18:42" (blue, mono, urgent red when <5min)

2. Focus indicator - Prominent banner:
   - "焦点嫌疑人" header (12px, gold)
   - 2 suspect chips with avatars:
     * "周明远" (avatar + name, gold border)
     * "林太太" (avatar + name, gold border)
   - "3/6 玩家聚焦于此" (11px, gray)

3. L3 clue alerts - Above chat:
   - "新线索解锁" notification:
     * "苏晚晴释放了深层线索" (12px, white)
     * L3 tag (purple)
     * "查看" link (gold)
   - Auto-dismiss after 5 seconds

4. Chat messages - Scrollable:
   - More intense messages:
     * "陈警官": "周明远，你的不在场证明有一个小时的空白" (13px, accusatory)
     * "周明远": "我...那段时间我在..." (hesitation visible)
     * [诚实度: 谎言辐射范围触发] tag (pink, 10px)
     * [情绪: 紧张-高] tag (orange, 10px)
   - System: "苏晚晴 情绪波动检测" (gray, italic)
   - NPC contradictions highlighted:
     * "⚠️ 与之前发言矛盾" (yellow, small)
   - 6-8 messages

5. Pressure indicators - Side overlay:
   - NPC stress levels:
     * 周明远: █████░░ 高压 (red)
     * 林太太: ███░░░░ 中压 (orange)
     * 苏晚晴: ██░░░░░ 低压 (green)
   - Collapsible panel
   - "NPC压力值" header (11px, gray)

6. Evidence showcase - Above input:
   - "已公开线索" (7/12) (12px, gray)
   - Horizontal scroll of shared evidence chips
   - Green bg for shared
   - Gold border for unshared

7. Input area - Fixed bottom:
   - Text input
   - Send button (gold)
   - "逼问" button (pink, outline, small)
   - Evidence attach

Specs:
- 390x844px
- High tension visual cues
- Pressure meters: thin bars, colored
- Contradiction warnings: yellow
- L3 alerts: purple accent
- Focus suspects: gold highlight
- Chat messages show emotional tags
- Urgent timer (turns red under 5min)
- Left-aligned content
- Atmosphere: serious, confrontational
```

---

### 10. 全员最终投票

**页面名称：** 全员最终投票
**对应环节：** 第七环节
**用途：** 所有玩家独立投票，AI也参与推理投票

**提示词：**
```
Create a mobile app final voting screen, all players vote independently, dark tech style, climactic.

Layout:

1. Header:
   - "最终投票" (18px, gold, larger)
   - "所有玩家独立投票" (12px, gray)
   - No timer (voting phase)

2. Voting instructions - Card:
   - "选择你认为的凶手" (14px, white)
   - "投票结果将在公示阶段揭晓" (12px, gray)
   - Subtle divider

3. Suspect cards - Full cards (vertical):

   Each suspect (6 cards, full width):
   - Avatar (56px circle, prominent)
   - Name (16px, white, Cabinet Grotesk)
   - Role + brief summary: "画廊老板 · 声称早离开" (12px, gray)
   - Evidence against:
     * "被3条线索指向" (11px, blue)
     * "回避发言2次" (11px, pink)
   - Select button (large circle, right side)
   - Tap to select: gold ring fills + checkmark

   Selected state:
   - Full gold border on card
   - "已选择" badge (gold)
   - Other cards dimmed (50% opacity)

4. AI voting indicator - Bottom of list:
   - "AI NPC 也在独立投票..." (12px, gray, animated dots)
   - "AI将综合线索和对话做出判断" (11px, gray, italic)

5. Bottom actions:
   - "确认投票" button (primary, gold, full-width)
   - Disabled until selection made
   - "投票后不可更改" warning (11px, gray)

Specs:
- 390x844px
- Suspect cards: prominent, full-width
- Avatar: 56px, large
- Selected: full gold border
- AI indicator adds tension
- Serious, climactic feel
- Left-aligned content
- No neon effects
- Clear selection state (only one)
```

---

### 11. 投票结果公示-A（安全公布）

**页面名称：** 投票结果公示 - 0票安全玩家
**对应环节：** 第八环节 阶段A
**用途：** 公布得0票玩家，全场松一口气

**提示词：**
```
Create a mobile app vote result announcement screen for safe players (0 votes), dark tech style, relief atmosphere.

Layout:

1. Header:
   - "投票结果公示" (16px, white)
   - "阶段一" tag (green, small)

2. Announcement - Large centered card:
   - "安全" header (24px, green, large)
   - Relief icon: 😮‍💨 or shield icon
   - "以下玩家得0票，安全" (14px, gray)

3. Safe players - Horizontal row:
   - 3-4 player avatars (48px circles)
   - Names below each (12px, white)
   - Green checkmark overlay on each
   - "SAFE" badge (green, small)
   - Gold accent border on card

4. Atmosphere text - Below:
   - "所有人松了一口气" (13px, gray, italic)
   - Divider line

5. Next indicator:
   - "下一位: 1-2票玩家..." (12px, gray)
   - "点击继续" button (gold, small)
   - Auto-advance arrow

6. Background:
   - Subtle dark gradient
   - No dramatic effects (relief, not tension)

Specs:
- 390x844px
- Green primary color for safe
- Relief atmosphere, not tense
- Centered safe players card
- Gold accent minimal
- Quick transition to next phase
- Calm visual tone
```

---

### 12. 投票结果公示-B（悬念揭晓）

**页面名称：** 投票结果公示 - 最高得票玩家
**对应环节：** 第八环节 阶段B/C
**用途：** 公布最高得票玩家，悬念揭晓，平票处理

**提示词：**
```
Create a mobile app vote result announcement screen for highest voted player, climactic reveal, dark tech style.

Layout:

1. Header:
   - "投票结果公示" (16px, white)
   - "最终揭晓" tag (gold, pulsing)

2. Vote breakdown - Top section:
   - "投票统计" header (14px, gold)
   - Vote distribution bars:
     * 周明远: ████████░░ 4票 (67%, red bar)
     * 林太太: ██░░░░░░░░ 1票 (17%, orange bar)
     * 赵医生: ░░░░░░░░░░ 0票 (0%, gray bar)
     * 弃权: ██░░░░░░░░ 1票 (17%, gray bar)
   - Bar chart visualization

3. Accused reveal - Large dramatic card:
   - "最高得票" header (12px, pink)
   - Avatar (80px circle, dramatic reveal)
   - Name: "周明远" (24px, gold, large)
   - Vote count: "4票" (20px, red, mono)
   - Role reveal: "投资人 · 35岁" (13px, gray)
   - Evidence summary:
     * "3条L3线索指向"
     * "回避发言2次"
     * "谎言被揭穿1次"
   - Gold border, dramatic card

4. Tie-breaker notice (if applicable):
   - "⚠️ 平票处理" banner (yellow bg)
   - "周明远 与 林太太 并列最高票" (13px)
   - "未投此二人的玩家重新投票" (12px)
   - "重新投票为公开记名" (11px, gray)
   - "进入重新投票..." button (gold)

5. Result status:
   - If no tie: "等待真相揭晓..." (13px, gray, animated dots)
   - Next button: "查看结局" (gold, full-width)

Specs:
- 390x844px
- Dramatic reveal feel
- Vote bars: prominent visualization
- Accused card: largest element
- Red for high votes, gold for reveal
- Tie-breaker: yellow warning
- Tense, climactic atmosphere
- Centered reveal card
- Left-aligned vote bars
```

---

### 13. 结局短剧播放

**页面名称：** 结局短剧播放
**对应环节：** 第八环节 阶段D
**用途：** 播放对应结局的短剧（指认成功/失败/平票不同结局）

**提示词：**
```
Create a mobile app ending video playback screen, cinematic, dark tech style.

Layout:

1. Minimal header:
   - No back button (cannot skip)
   - "结局" badge (gold, small, top-left)
   - Progress indicator (thin line, top)

2. Video player - Full screen area:
   - 16:9 video (maximized, minimal padding)
   - "结局A: 真相大白" title overlay (18px, gold)
   - Subtitle text (bottom of video, 13px, white)
   - No visible controls during first 10 seconds
   - Play/pause appears after tap

3. Ending badge - Overlay:
   - "指认成功" tag (green, top-right)
   - Ending type: "结局 A / 共 5 个" (11px, gray)

4. Post-video overlay - After video ends:
   - "结局已播放完毕" (14px, white)
   - "查看蝴蝶效应复盘" button (gold, full-width)
   - "查看对话记录" button (secondary, outline)

5. Ambient:
   - Full dark background
   - No distractions
   - Cinematic immersion
   - Video takes center stage

Specs:
- 390x844px
- Video maximized
- Minimal UI during playback
- Ending overlay after video
- Cinematic, immersive feel
- Gold accent for ending title
- No neon effects
- Centered video (video content, not UI pattern)
```

---

### 14. 蝴蝶效应复盘

**页面名称：** 蝴蝶效应复盘图
**对应环节：** 第八环节 阶段E
**用途：** 可视化展示每个选择如何影响结局，因果图展示

**提示词：**
```
Create a mobile app butterfly effect review screen with causal graph visualization, dark tech style, gold accent.

Layout:

1. Header:
   - "蝴蝶效应复盘" (16px, gold)
   - "山庄晚宴 · 结局A" (12px, gray)
   - Share button (right)

2. Summary card - Top:
   - "真凶: 周明远" (14px, white)
   - "投票结果: 4票指认成功" (12px, green)
   - "关键转折: 第二轮搜证发现暗格" (12px, gold)

3. Causal graph - Main area (scrollable canvas):

   Timeline nodes (vertical flow):
   Node 1: "个人准备" (green circle)
     - "观看开场短剧" (11px, gray)
     - Connecting line down
   
   Node 2: "第一幕发言" (blue circle)
     - "质问苏晚晴关于当晚行踪" (12px, white)
     - Branch: "→ 苏晚晴释放L2线索" (green)
     - Connecting line down
   
   Node 3: "第一轮搜证" (blue circle)
     - "AP投入: 尸体周围(2) + 个人物品(2)" (11px)
     - "发现: 致命伤口 + 血迹方向" (12px, green)
     - "⚡ 关键选择: 搜查客厅" (gold tag)
     - Connecting line down
   
   Node 4: "第二幕讨论" (blue circle)
     - "公开线索: 致命伤口" (12px, green)
     - "私聊周明远 → 触发异常反应" (12px, pink)
     - Parallel path (faded): "→ 如果选择公开血迹方向..." (gray, dashed)
     - Connecting line down
   
   Node 5: "第二轮搜证" (gold circle, prominent)
     - "🔓 解锁隐藏暗格" (14px, gold, bold)
     - "发现: 凶器 + 遗书" (12px, gold)
     - "💡 决定性证据" tag (gold, large)
     - Connecting line down
   
   Node 6: "最终投票" (green circle)
     - "投票: 周明远 ✅" (12px, green)
     - "AI投票: 4/5 投周明远" (11px, gray)
     - Connecting line down
   
   Node 7: "结局A" (green circle, end)
     - "真相大白" (12px, gold)

   Parallel paths (faded, dashed lines):
     - "如果未搜查客厅 → 暗格未解锁 → 结局D" (gray, translucent)
     - "如果未公开伤口 → 周明远逃脱 → 结局B" (gray, translucent)

4. Legend - Bottom overlay:
   - "图例" header (11px, gray)
   - Gold circle = 关键转折
   - Green line = 你的选择
   - Gray dashed = 未选择的路径
   - Gold border = 决定性证据

5. Bottom actions:
   - "查看对话记录" (secondary)
   - "返回主页" (primary, gold)

Specs:
- 390x844px
- Causal graph: vertical timeline + branches
- Nodes: circles, colored
- Connections: lines (solid = chosen, dashed = alternate)
- Gold for critical turning points
- Gray for parallel unchosen paths
- Scrollable vertical layout
- Informative, analytical feel
- Left-aligned content nodes
- NO neon effects
```

---

### 15. 单局战绩详情

**页面名称：** 单局战绩详情
**对应环节：** 游戏结束
**用途：** 展示本局完整数据、表现统计、复盘入口

**提示词：**
```
Create a mobile app game result stats screen, comprehensive data summary, dark tech style, gold accent.

Layout:

1. Header - Result banner:
   - "剧本: 山庄晚宴" (14px, white)
   - "难度: ⭐⭐⭐" (gold stars)
   - "结局: 凶手被指认" (14px, green)
   - Background: dark card with subtle gold accent

2. Meta info - Compact row:
   - "2026-05-24" (mono, gray)
   - "78分钟" (mono, gray)
   - "明侦模式" (tag, blue)

3. Player results table:
   - "参与角色 (6人)" header (14px, gold)
   - Table header: 角色 | 扮演者 | 身份 | 结果
   - Rows (6):
     * 苏晚晴 | 推理小王 | 普通玩家 | ✅ 投对 (green)
     * 周明远 | [AI] | 凶手 | ❌ 被投 (red)
     * 陈警官 | 探案达人 | 侦探 | ✅ 投对 (green)
     * 林太太 | [AI] | 普通玩家 | ❌ 投错 (orange)
     * 赵医生 | [AI] | 普通玩家 | ✅ 投对 (green)
     * 何记者 | 真相猎手 | 普通玩家 | ✅ 投对 (green)
   - [AI] tag: gray, small
   - Subtle divider between rows

4. Vote result - Summary card:
   - "投票结果" header (14px, gold)
   - "周明远 4票 / 林太太 1票 / 弃权 1" (14px, white, mono)

5. Personal performance - Card:
   - "个人表现" header (14px, gold)
   - Stats grid (2x2):
     * 搜证AP: 5/5 (16px, gold, mono)
     * 发现线索: 7条 (16px, gold, mono)
     * 发言次数: 23次 (16px, blue, mono)
     * 私聊次数: 4次 (16px, blue, mono)
   - Labels below each stat (11px, gray)
   - Additional:
     * "公开线索: 5条" (12px, green)
     * "保留线索: 2条" (12px, gray)
     * "最终投票: 周明远 ✅" (12px, green)

6. Review actions - Bottom:
   - "查看蝴蝶效应复盘" button (primary, gold, full-width)
   - "查看完整对话记录" button (secondary, outline)
   - "返回主页" button (text, gray)

Specs:
- 390x844px
- Result banner: prominent, colored
- Table: clean, compact rows
- Stats: large mono numbers, 2x2 grid
- Gold for key numbers
- Green for correct, red for wrong
- AI players tagged clearly
- Comprehensive data feel
- Left-aligned content
- NO three-equal-card layout
```

---

## 页面生成顺序建议

1. 个人准备页 → 建立游戏流程起点
2. 个人身份卡 → 身份信息展示
3. 第一幕-轮流发言 → 游戏正式开始
4. 第一幕-自由交流 → 讨论模式
5. 第一轮搜证 → 核心搜证机制
6. 第二幕-集中讨论 → 诚实度规则展示
7. 侦探投票 → 单独投票机制
8. 第二轮搜证 → 深层搜证
9. 第三幕-最终讨论 → 紧张逼问氛围
10. 全员最终投票 → 高潮投票
11. 投票结果公示-A → 安全公布
12. 投票结果公示-B → 悬念揭晓
13. 结局短剧播放 → 结局动画
14. 蝴蝶效应复盘 → 因果图可视化
15. 单局战绩详情 → 数据总结

---

## 设计一致性检查

生成所有页面后确认：

- [ ] 统一使用霓虹金 (#C9A96E) 作为唯一强调色
- [ ] 游戏阶段标识清晰（顶部 header 一致）
- [ ] 倒计时/计时器统一使用 JetBrains Mono
- [ ] 消息气泡统一 12px 圆角
- [ ] 玩家头像统一圆形
- [ ] AP/投票等数据使用 mono 字体
- [ ] 搜证页面进度条 4px 高度
- [ ] 无霓虹外发光效果
- [ ] 聊天页面消息左对齐（NPC）/ 右对齐（玩家）
- [ ] 结果公示有明确的氛围区分（安全=绿色/悬念=金红色）
- [ ] 蝴蝶效应复盘图因果关系统一使用线条连接
- [ ] 所有页面背景统一 #0A0E17
