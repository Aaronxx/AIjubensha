# AI推理叙事游戏 - Figma Make 页面生成提示词（Design Taste 重构版）

## 设计规范（基于 design-taste-frontend 技能）

### 设计读取
**Reading this as:** 移动端游戏应用界面，面向年轻推理爱好者群体，采用暗黑科技美学 + 霓虹金主色调 + 不对称布局语言。

### 三轴设定
- `DESIGN_VARIANCE: 7` - 适度不对称，打破完美对称布局
- `MOTION_INTENSITY: 4` - 静态为主，hover微动效
- `VISUAL_DENSITY: 5` - 标准应用间距，信息清晰分层

### 色彩系统（遵循 LILA 规则 + 色彩一致性锁定）
| 类型 | 色值 | 用途 |
|------|------|------|
| **背景主色** | #0A0E17 | 页面主背景（off-black，非纯黑） |
| **背景深色** | #06080D | 卡片/模块背景 |
| **背景浅色** | #111827 | 次级背景 |
| **霓虹金** | #C9A96E | **唯一强调色**（按钮/激活状态/标签） |
| **霓虹蓝** | #4A7DFF | 科技元素/链接/图标（低饱和度） |
| **霓虹粉** | #E0556A | 警告/危险/热点标记 |
| **霓虹紫** | #9B7ED8 | 次要强调/渐变 |
| **霓虹绿** | #4CAF93 | 成功/完成状态 |
| **文字主色** | #E8ECF1 | 主要文字 |
| **文字副色** | #8B95A5 | 次要文字/标签 |
| **文字禁用** | #5A6475 | 禁用/占位文字 |
| **边框色** | #1A2744 | 分割线/卡片边框 |

**色彩一致性锁定：** 全站仅使用霓虹金(#C9A96E)作为主强调色，其他颜色仅用于特定状态标记，不在不同section间混用。

### 字体系统（遵循 Typography 规则，禁用 Inter 作为默认）
| 类型 | 字体 | 大小 | 字重 | 用途 |
|------|------|------|------|------|
| **Display** | Cabinet Grotesk / SF Pro | 24px | 700 | 页面标题（tracking-tighter） |
| **副标题** | Cabinet Grotesk / SF Pro | 18px | 600 | 区块标题 |
| **正文** | Satoshi / PingFang SC | 14px | 400 | 正文内容 |
| **小字** | Satoshi / PingFang SC | 12px | 400 | 标签/辅助文字 |
| **微字** | JetBrains Mono / SF Mono | 10px | 400 | 时间/计数/数字 |
| **按钮** | Cabinet Grotesk / SF Pro | 14px | 600 | 按钮文字 |

**字体配对：** Cabinet Grotesk (display) + JetBrains Mono (numbers/data)

### 组件风格（遵循 Shape Consistency Lock）
**圆角系统：all-soft (12px)**
- 卡片：12px
- 按钮：8px
- 输入框：8px
- 标签：6px
- 头像：50%（圆形）

**卡片风格：**
- 背景：#111827
- 边框：1px solid #1A2744
- hover状态：边框变为 rgba(201,169,110,0.4)，添加微弱内发光
- **禁用纯黑阴影**，使用带背景色调的阴影
- 不使用通用卡片容器，用 border-t/divide-y 分组

**按钮风格：**
- 主按钮：背景 #C9A96E，文字 #0A0E17，hover时轻微放大
- 次按钮：背景透明，边框 1px solid #C9A96E，文字 #C9A96E
- 禁用状态：背景 #1A2744，文字 #5A6475
- active状态：scale-[0.98] 模拟物理按压

**输入框风格：**
- 背景：#0A0E17
- 边框：1px solid #1A2744
- focus状态：边框变为 #C9A96E
- placeholder：#5A6475
- label 在输入框上方，helper text 在下方

### 特效规范（遵循 NO neon/outer glows 规则）
- **内发光**：使用 inset box-shadow 代替外发光
- **文字强调**：使用颜色变化，非 text-shadow
- **hover效果**：border-color 变化 + 轻微 transform
- **禁用**：纯黑(#000000)、外发光、过度渐变、AI紫色

### 布局规则（遵循 Anti-Center Bias）
- Hero区域：左对齐内容，右侧资产
- 列表：不对称间距，非完美等分
- Grid：使用 fractional units (2fr 1fr)
- 移动端：所有不对称布局在 <768px 折叠为单列

---

## 页面提示词

### 1. 首页

**页面名称：** AI推理叙事游戏 - 首页
**用途：** 应用主入口

**提示词：**
```
Create a mobile app home screen for an AI mystery narrative game, dark tech aesthetic with gold accent.

Design Read: Dark mode mobile game app, cyberpunk-inspired but restrained, gold (#C9A96E) as single accent color, asymmetric layouts, no neon glows.

Layout structure (top to bottom):

1. Banner carousel - Full-width card with:
   - Dark gradient background (#1A0F2E to #0A0E17)
   - "限时活动 · 山庄晚宴" headline (left-aligned, gold text, 20px)
   - Subtitle (13px, gray text, max 20 words)
   - CTA button "立即参与" (gold fill, dark text, 8px radius)
   - Countdown badge (11px, mono font, gold border)
   - Carousel dots at bottom center

2. Three entry cards - Horizontal row, asymmetric sizing:
   - Card 1 (剧本): 1.2fr width, book icon, gold accent
   - Card 2 (排行榜): 1fr width, trophy icon, blue accent  
   - Card 3 (任务): 1fr width, target icon, green accent, red badge "3"
   Each card: dark background, 12px radius, icon + label, left-aligned content

3. Beginner guide card - Horizontal card:
   - Left: gradient background (purple tint)
   - Right: title + progress bar + arrow
   - Asymmetric content placement

4. Server messages - Compact card:
   - Header: "全服喊话" (12px, gold)
   - 3 message rows with colored user badges
   - "发表" button (small, gold outline)

5. Hot feed header - "热门动态" (18px, left-aligned) + "查看全部" link (right)

6. Feed cards (2 visible) - Weibo-style:
   - User avatar (circular, 42px)
   - Name + colored tag
   - Content text
   - Image placeholders (1-2)
   - Action bar: like/comment/share + timestamp

7. Bottom tab bar - 5 items:
   - 首页 (active, gold icon/label, 2px gold line above)
   - 剧本 (inactive, gray)
   - 快速组局 (center, floating button, orange-gold gradient, larger)
   - 社交 (inactive, gray)
   - 我的 (inactive, gray)

Technical specs:
- Screen: 390x844px
- Background: #0A0E17
- Cards: #111827 with 1px #1A2744 border
- Accent: #C9A96E ONLY for active/CTA elements
- All corners: 12px cards, 8px buttons, 6px tags
- Left-aligned content, no centered hero
- Spacing: 12-16px between sections
- No status bar
- NO neon glows, NO purple gradients, NO centered content
```

---

### 2. 剧本列表页

**提示词：**
```
Create a mobile app script selection screen, dark tech style, gold accent.

Layout:

1. Search header - Full-width search bar:
   - Rounded input (8px radius, dark background)
   - Placeholder: "搜索剧本..."
   - Filter icon button (right)
   - No hardcoded search suggestions

2. Popular banner - Horizontal card:
   - "Popular" tag (orange, small badge)
   - "热门剧本" (14px, gold)
   - Arrow icon (right)
   - Subtle gradient background

3. Category cards - Horizontal scroll, 3 cards:
   - "Trending" + "42 个剧本"
   - "New" + "18 个剧本"
   - "For You" + "25 个剧本"
   Each: dark card, 12px radius, icon + label + count, varying widths

4. Section header - "推荐剧本" (16px, left) + "更多" (12px, right, gray)

5. Script cards (4 stacked):
   Each card:
   - Left cover: 64x64px square, emoji, dark background
   - Right content: name (15px), tags (6px radius, colored), rating (gold star + score), player count (11px, mono)
   - Tags: blue/ purple/ green/ orange backgrounds with matching text
   - Cards stacked with 10px gap, 12px internal padding

6. Bottom tab bar - Same as home

Specs:
- 430x932px
- Background: #0A0E17
- Cards: #1A1F2E, 1px border
- Gold accent for active elements only
- Left-aligned content
- Asymmetric card widths in category row
- NO centered content, NO neon effects
```

---

### 3. 剧本详情页

**提示词：**
```
Create a mobile app script detail screen, dark tech style.

Layout:

1. Hero area - Large rectangular section:
   - Gradient overlay (dark purple to transparent)
   - Title "山庄晚宴" (24px, white, left-aligned)
   - Subtitle (13px, gray, max 20 words)
   - No centered hero - content left-aligned

2. Info card - Dark card with:
   - Type badge (本格推理, blue, 6px radius)
   - Grid layout: difficulty (3 gold stars), duration (75分钟, mono), players (4-6人)
   - Clean data presentation, no card boxes for metrics

3. Synopsis card - "剧情简介" header + expandable text + "展开" link

4. Character list - "角色列表" header:
   - Horizontal scroll of character cards
   - Each: circular avatar + name + role
   - 6 cards visible, varying widths

5. Reviews section - "玩家评价" header:
   - Score summary (9.2/10, large gold number)
   - 2 review cards with user info, rating, text

6. Sticky action bar (bottom):
   - Left: star/favorite icon, share icon
   - Right: "开始游戏" button (gold fill, dark text, full-width remaining)

Specs:
- 390x844px
- Hero: 30% of screen, left-aligned content
- Gold for CTA and active states only
- Character avatars: circular, colored borders
- Action bar: fixed at bottom
- NO centered hero, NO three-equal-feature cards
```

---

### 4. 游戏房间（准备大厅）

**提示词：**
```
Create a mobile app game lobby screen, dark tech style.

Layout:

1. Room header - Top bar:
   - Room number "#12345" (mono, copyable)
   - Script name (14px, gold)
   - Settings icon (right)

2. Player grid - Asymmetric 2x3 grid:
   - Each card: circular avatar, nickname, status badge
   - Host card: crown icon (gold)
   - Empty slots: "+" placeholder, "等待加入"
   - Status badges: green (ready), gray (not ready)
   - Varying card heights if needed

3. Chat area - Compact section:
   - "房间聊天" header
   - 3-4 message bubbles (alternating alignment)
   - Input field + send button

4. Room settings - Expandable card:
   - Toggle switches for speech mode, AI fill
   - Min player selector

5. Action buttons (bottom):
   - "准备" (gold, full-width for non-host)
   - OR "开始游戏" (for host)
   - "邀请好友" (secondary, outline)
   - "退出房间" (text, gray)

Specs:
- 390x844px
- Player cards: 12px radius, dark background
- Chat bubbles: 12px radius, alternating colors
- Gold primary button
- Left-aligned content
- NO perfect symmetry in player grid
```

---

### 5. 游戏进行页 - 聊天界面

**提示词：**
```
Create a mobile app game chat screen, dark tech style.

Layout:

1. Game header - Top bar:
   - Back arrow (left)
   - "第二幕 · 暗流涌动" (gold, 15px)
   - "剩余 18:42" (blue, mono, 12px)
   - Menu icon (right)

2. Chat messages - Scrollable area:
   - NPC messages: avatar left + name (colored) + bubble (dark bg)
   - Player messages: avatar right + name + bubble (blue bg, white text)
   - System messages: centered, small, italic
   - Timestamps between groups (10px, gray, centered)
   - 6-8 messages from different characters

3. Typing indicator - "苏晚晴 正在输入..." (12px, gray)

4. Input area (fixed bottom):
   - Text input (8px radius, dark bg)
   - Send button (circular, gold)
   - Private chat icon (small, left)

Specs:
- 390x844px
- Message bubbles: 12px radius
- NPC bubble: #1A1F2E
- Player bubble: #4A7DFF, white text
- Avatars: 40px circles
- Input bar: distinct from chat
- NO neon effects, NO centered hero
```

---

### 6. 游戏进行页 - 搜证界面

**提示词：**
```
Create a mobile app evidence investigation screen, dark tech style.

Layout:

1. Header - Top bar:
   - Back arrow
   - "第一轮搜证" (15px, white)
   - AP counter: "剩余 AP: 7 / 15" (gold, mono, large)

2. Location cards (2 visible):
   Location 1 - "死者房间":
   - Icon + name (14px)
   - Subtitle (11px, gray)
   - Investigation targets:
     * "尸体周围区域" - progress 100%, green check
     * "个人物品" - progress 50%, "调查" button (gold outline)
     * "隐藏空间" - progress 0%, button disabled
   - Progress bars: 4px height, rounded

   Location 2 - "客厅公共区域":
   - Similar structure, all uninvestigated

3. Hint card - Highlighted:
   - "💡" icon
   - Tip text (gold border, warm tint)
   - Arrow pointer

4. Bottom actions:
   - "结束搜证" (secondary, outline)
   - "确认完成" (primary, gold)

Specs:
- 390x844px
- Progress bars: 4px, colored fills
- Hint card: gold border, subtle bg tint
- Investigation buttons: gold outline
- NO card boxes for every element
- Left-aligned content
```

---

### 7. 游戏进行页 - 个人资料

**提示词：**
```
Create a mobile app profile stats screen, dark tech style.

Layout:

1. Profile header - Centered:
   - Large avatar (80px circle, colored bg)
   - Nickname (18px)
   - Membership badge (gold, small)
   - Signature (12px, gray, italic)

2. Stats row - 3 columns, equal width:
   - "侦探投票率" 78% (blue, mono, large)
   - "凶手逃脱率" 33% (pink, mono, large)
   - "总场次" 156 (gold, mono, large)
   - Labels below (11px, gray)

3. Achievements - "成就徽章 · 4枚" header:
   - Horizontal scroll of badges
   - Each: icon + name (神探/影帝/铁证/博览)
   - Gold colored, 12px radius

4. Recent games - "最近战绩" header:
   - 3 game result cards:
     * "✅ 山庄晚宴 · 侦探 · 投对"
     * "❌ 午夜列车 · 凶手 · 被投出"
     * "✅ 密室疑云 · 普通 · 投对"
   - Green/red indicators, 11px text

Specs:
- 390x844px
- Stats: large mono numbers, colored
- Badges: compact, gold theme
- Game results: alternating indicators
- NO three-equal-card layout for stats
```

---

### 8. 游戏进行页 - 商城界面

**提示词：**
```
Create a mobile app shop screen, dark tech style.

Layout:

1. Balance bar - Top:
   - "⭐ 1280" (gold, large, mono)
   - "充值" button (pill shape, gold fill)

2. Category tabs - Horizontal scroll:
   - 推荐 (active, gold underline)
   - 皮肤/头像框/礼物/限定
   - Active: gold text + 2px underline

3. Product grid - 2 columns:
   Each card:
   - Preview area (gradient bg, product icon)
   - Badge if applicable (HOT/NEW/限定)
   - Product name (14px)
   - Price (gold, mono)
   - 6 products in 3 rows

Specs:
- 390x844px
- Product cards: 12px radius
- Preview: colored gradients (NOT purple)
- Grid: equal spacing, 2 columns
- Tabs: compact, underline active
- NO generic AI gradients
```

---

### 9. 排行榜

**提示词：**
```
Create a mobile app leaderboard screen, dark tech style.

Layout:

1. Header - "排行榜" (18px, gold, left)

2. Category tabs - 3 tabs:
   - 推理榜 (active, gold)
   - 社交榜
   - 贡献榜
   - Active: gold underline

3. Top 3 showcase - Asymmetric display:
   - Center: #1 player (largest, gold frame, crown)
   - Left: #2 player (silver frame, smaller)
   - Right: #3 player (bronze frame, smaller)
   - Each: avatar, name, score (mono, gold)

4. Ranking list (4-10) - Vertical:
   - Rank number (gray, mono)
   - Avatar
   - Nickname
   - Score (right-aligned, gold)
   - Subtle divider lines

5. My rank - Fixed bottom card:
   - "我的排名: #42" (14px)
   - Progress to next rank

Specs:
- 390x844px
- Top 3: prominent, medal colors
- List rows: dark bg, dividers
- Score: mono, gold text
- My rank: pinned at bottom
- NO centered hero
- Asymmetric top 3 display
```

---

### 10. 任务系统

**提示词：**
```
Create a mobile app task system screen, dark tech style.

Layout:

1. Header - "任务中心" (18px, left) + check-in icon (right)

2. Check-in card - Horizontal:
   - 7-day grid (current highlighted gold)
   - Completed checked (green)
   - "立即签到" button (gold)

3. Task categories - Tabs:
   - 每日任务 (active)
   - 成就任务
   - 新手任务

4. Task list - Vertical:
   Each task:
   - Icon (left)
   - Name + description
   - Progress bar (X/Y)
   - Reward badge (gold stars)
   - "领取" button (if complete, gold)
   - OR progress indicator
   - 5-6 tasks visible

5. Summary - Bottom:
   - "今日可获得: 80⭐" (14px, gold)

Specs:
- 390x844px
- Task cards: 12px radius, 1px border
- Progress bars: 4px, colored
- Complete: green accent
- Reward badges: gold
- Check-in: 7-box grid
- NO perfect symmetry
```

---

### 11. 成就系统

**提示词：**
```
Create a mobile app achievement system screen, dark tech style.

Layout:

1. Header - "成就徽章" + "已获得: 32/56"

2. Recent achievement - Featured card:
   - "最近获得: [神探] 2026-05-20"
   - Large icon
   - Rarity badge (史诗, purple)

3. In progress - "进度中" header:
   - Progress cards:
     * "[博览群书] 17/20 85%"
     * "[影帝] 2/3 67%"
   - Horizontal progress bars

4. Achievement grid - Categorized:
   Category headers: 推理类, 演技类, 社交类, etc.
   Each: badge grid
   - Unlocked: gold icon, full opacity
   - Locked: gray icon, 50% opacity
   - Name + rarity indicator

5. Hidden achievements - Bottom:
   - "隐藏成就: 已解锁 3/8 枚"

Specs:
- 390x844px
- Badges: shield-shaped, 12px radius
- Rarity colors: 普通=gray, 稀有=blue, 史诗=purple, 传说=gold
- Progress bars: horizontal
- Grid: 3-4 columns
- NO three-equal-feature layout
```

---

### 12. 社交广场

**提示词：**
```
Create a mobile app social feed screen, dark tech style.

Layout:

1. Header - "社交广场" + search icon + "发布" (+) button

2. Category tabs - 3 tabs:
   - 动态 (active, gold underline)
   - 好友
   - 关注

3. Create post card - Compact:
   - User avatar
   - Placeholder text
   - Image/video icons
   - "发布" button

4. Feed cards - 3 posts:
   Each:
   - Avatar + name + tag
   - Content text
   - Optional images
   - Action bar: like/comment/share + timestamp
   - Comments count badge

5. Online friends - Side section:
   - "在线好友" header
   - Friend list with green dots

Specs:
- 390x844px
- Weibo-style feed layout
- Circular avatars, colored borders
- Tags: colored badges
- Action bar: icon + count
- NO centered hero
- Left-aligned content
```

---

### 13. 个人中心

**提示词：**
```
Create a mobile app user profile/settings screen, dark tech style.

Layout:

1. Profile header - Large section:
   - Avatar (large, circular)
   - Nickname (18px)
   - Membership badge (gold)
   - Signature (12px, italic, gray)
   - Edit button (right)

2. Stats summary - 4 columns:
   - 总场次 156
   - 胜率 78%
   - 成就 32
   - 星星 1280
   - Large mono numbers, labels below

3. Function list - Vertical:
   Each row: icon + label + arrow
   - 战绩详情
   - 剧本记录
   - 收藏夹
   - 商城
   - 钱包
   - 设置
   - 邀请好友
   - 帮助中心
   - Subtle divider lines

4. Logout - Bottom:
   - "退出登录" (red text, centered)

Specs:
- 390x844px
- Profile: gradient background
- Stats: equal columns, large numbers
- Menu rows: icon + text + chevron
- Logout: subtle, visible
- NO card boxes for menu items
```

---

### 14. 钱包/充值

**提示词：**
```
Create a mobile app wallet/top-up screen, dark tech style.

Layout:

1. Balance card - Top:
   - "星星余额" label
   - "1,280" with star icon (gold, large, mono)
   - Gradient background

2. Quick actions - Row:
   - 充值记录
   - 消费记录
   - 赠送记录
   - Icon + label each

3. Top-up packages - 2x3 grid:
   - 60⭐ ¥6
   - 300⭐ ¥30
   - 680⭐ ¥68 (推荐, gold border)
   - 1280⭐ ¥128
   - 3280⭐ ¥328
   - 6480⭐ ¥648 (额外赠送标记)
   - Each: stars, price, bonus if any

4. Payment methods - List:
   - 微信支付
   - 支付宝
   - Apple Pay
   - Radio buttons

5. Confirm button - Bottom:
   - "确认充值" (gold, full-width)

Specs:
- 390x844px
- Balance: prominent, gradient
- Packages: dark bg, price prominent
- Recommended: gold border, badge
- Confirm: gold, full-width
- NO centered hero
```

---

### 15. 语音房间

**提示词：**
```
Create a mobile app voice chat room screen, dark tech style.

Layout:

1. Room header - Top bar:
   - Room name (editable)
   - Room number + copy icon
   - Close button

2. User grid - 3x3 grid:
   Each card:
   - Avatar (circular, 48px)
   - Nickname below
   - Mic status icon
   - Speaking indicator (green glow)
   - Host crown (gold)

3. Voice visualization - Waveform:
   - Animated bars showing voice activity
   - Neon blue/green color

4. Chat panel - Collapsible:
   - Voice-to-text messages
   - Quick emoji buttons

5. Bottom controls - Fixed:
   - 🎤 麦克风 (toggle, green when active)
   - 🔊 扬声器 (toggle)
   - 💬 聊天 (expand/collapse)
   - 🚪 离开房间 (red text)

Specs:
- 390x844px
- User cards: compact, rounded
- Speaking: green glow around avatar
- Muted: red slash icon
- Waveform: animated-style bars
- Controls: large touch targets
- NO neon glows on non-speaking users
```

---

### 16. 回放系统

**提示词：**
```
Create a mobile app game replay playback screen, dark tech style.

Layout:

1. Header - Top bar:
   - Back button
   - Script name: "山庄晚宴"
   - Date: "2026-05-24"
   - Share button

2. Video player - Large area:
   - Game screen reproduction
   - Play/pause overlay
   - Timestamp overlay

3. Playback controls - Below:
   - Timeline with event markers
   - ⏮️ ⏯️ ⏭️ buttons
   - Current / Total time (mono)
   - Speed selector: 0.5x/1x/1.5x/2x

4. Chapter markers - Horizontal:
   - 第一幕
   - 第一轮搜证
   - 第二幕
   - 第二轮搜证
   - 最终投票
   - Pill-shaped buttons

5. Player list - Side panel:
   - Avatars
   - Character names
   - Role reveal
   - Current speaker highlighted

6. Info tabs - Bottom:
   - 对话记录
   - 线索时间线
   - 投票详情

Specs:
- 390x844px
- Video: 16:9 ratio
- Timeline: thin line, colored markers
- Player list: compact avatars
- Controls: media player style
- NO centered hero
- Left-aligned content
```

---

### 17. 推理笔记增强版

**提示词：**
```
Create a mobile app investigation notes/canvas screen, dark tech style.

Layout:

1. Toolbar - Top bar:
   - Back to game
   - Note title (editable)
   - Auto-save indicator
   - Export/share

2. Tool palette - Floating:
   - ✋ 拖拽
   - ➕ 添加卡片
   - 🔗 连线
   - 🎨 颜色
   - 📝 便利贴
   - Compact icon buttons

3. Infinite canvas - Main area:
   - Clue cards (4-5 visible):
     * Title, description, source
     * Colored borders by type
   - Character cards (2-3):
     * Avatar + name + notes
   - Connection lines:
     * Solid = confirmed
     * Dashed = suspected
   - Sticky notes with text

4. Sidebar - Collapsible:
   - 线索库
   - 角色信息
   - 时间线

5. Bottom bar - Zoom:
   - Percentage
   - +/- buttons
   - Reset view

Specs:
- 390x844px
- Canvas: light grid bg (subtle)
- Cards: dark bg, colored borders
- Types: evidence=purple, person=blue, timeline=green
- Connection lines: thin, colored
- Sidebar: slide-in panel
- Mind-map feel
- NO generic card containers
```

---

### 18. 邀请好友

**提示词：**
```
Create a mobile app invite friends screen, dark tech style.

Layout:

1. Hero banner - Top:
   - "邀请好友 赢取奖励" title
   - "最高可得 500⭐" (gold, large)
   - Decorative element

2. Invite code - Prominent card:
   - "我的邀请码" label
   - Large code: "A1B2C3" (mono, gold)
   - Copy button
   - QR code preview
   - Share link + copy icon

3. Quick share buttons - Row:
   - 微信好友
   - 微信朋友圈
   - QQ
   - 复制链接
   - Platform icons

4. Invite stats - Summary card:
   - 已邀请: 12人
   - 已注册: 8人
   - 首通: 5人
   - 累计奖励: 350⭐

5. Reward details - List:
   - 好友注册 → +10⭐
   - 好友首通 → +50⭐
   - 好友充值 → 返利10%
   - Status indicators

6. Invite history - Recent:
   - Avatar/name
   - Register date
   - Reward status
   - Claim button if available

Specs:
- 390x844px
- Hero: gradient bg, promotional
- Code: large, mono, gold
- QR: square, scannable
- Share: platform-colored icons
- Stats: grid layout
- History: compact rows
- NO centered hero
```

---

### 19. 新手指引

**提示词：**
```
Create a mobile app beginner tutorial screen, dark tech style.

Layout:

1. Welcome area - Top:
   - Welcome graphic
   - "欢迎来到AI推理叙事游戏" title
   - Brief description
   - "开始引导" button (gold)

2. Tutorial steps - Vertical stepper:
   Step 1: 基础概念 (active, gold)
   - Icon + title
   - Description
   - Demo placeholder
   - "下一步" button

   Steps 2-6: Inactive (gray)
   - Similar structure

3. Progress indicator - Top dots:
   - 6 dots, current highlighted
   - Completed checked

4. Quick reference - Collapsible:
   - 术语词典 link
   - 操作指南 link
   - 视频教程 link

5. Skip option - Bottom:
   - "跳过引导" (text, gray)

Specs:
- 390x844px
- Stepper: vertical, connected lines
- Active: gold highlight
- Completed: green checks
- Inactive: gray text
- Progress: horizontal dots
- Educational feel
- NO three-equal cards
```

---

### 20. FAQ帮助中心

**提示词：**
```
Create a mobile app FAQ/help center screen, dark tech style.

Layout:

1. Search area - Top:
   - Large search bar
   - Hot searches: "如何充值", "AP是什么", etc.

2. Category navigation - Grid:
   - 新手入门
   - 账号相关
   - 游戏玩法
   - 充值消费
   - 社交功能
   - 技术问题
   - Icon + label each

3. Featured questions - List:
   Expandable items:
   - "如何开始一局游戏？" + feedback
   - "AP是什么？如何使用？"
   - "如何邀请好友一起玩？"
   - "充值后星星没到账怎么办？"
   - View count, useful/unused buttons

4. Expanded answer - When tapped:
   - Question title
   - Detailed text
   - Related images
   - Related questions
   - "联系客服" link

5. Quick actions - Bottom:
   - 在线客服 button
   - 意见反馈 button
   - 视频教程 button

Specs:
- 390x844px
- Search: prominent, rounded
- Categories: consistent icons
- Questions: accordion-style
- Feedback: thumbs up/down
- Quick actions: full-width, stacked
- Help-center feel
- NO centered hero
```

---

### 21. 客服系统

**提示词：**
```
Create a mobile app customer service chat screen, dark tech style.

Layout:

1. Header - "客服中心":
   - Back button
   - Queue status: "排队中: 第3位"

2. Service type selector - 3 options:
   - 🤖 智能客服 (active)
   - 👤 人工客服
   - 📝 提交工单
   - Tab-style

3. Chat area - Messages:
   - Bot welcome
   - Quick action buttons:
     * "如何充值"
     * "账号问题"
     * "游戏问题"
     * "其他"
   - User messages (right, blue)
   - Bot responses (left, dark)
   - Suggested follow-ups

4. Input area - Fixed bottom:
   - Text input
   - Image upload
   - Send button
   - "转人工" button (small)

5. Ticket list - If 工单 selected:
   - 进行中
   - 已解决
   - 新建 button

Specs:
- 390x844px
- Chat: messaging style
- Bot: dark bg bubbles
- User: blue bg, white text
- Quick buttons: pill-shaped
- Queue: prominent if waiting
- Clean chat interface
- NO centered content
```

---

### 22. 隐私协议

**提示词：**
```
Create a mobile app privacy policy screen, dark tech style.

Layout:

1. Header - "隐私协议":
   - Back button
   - Table of contents button

2. Document tabs - Horizontal:
   - 隐私政策 (active)
   - 用户协议
   - 数据收集说明
   - Cookie政策
   - Underline active

3. Document info - Metadata:
   - 生效日期: 2026-01-01
   - 更新日期: 2026-05-24
   - 版本号: v1.0
   - Mono font for dates

4. Document content - Scrollable:
   - Section headers (numbered, bold)
   - Body paragraphs
   - Bullet lists
   - Highlighted boxes (important)
   - Proper hierarchy

5. TOC sidebar - Overlay:
   - All sections listed
   - Clickable navigation

6. Bottom action bar - First-time:
   - Checkbox: "已阅读并同意"
   - "同意并继续" button (gold, full-width)
   - "不同意" text button

Specs:
- 390x844px
- Document: readable, proper spacing
- Headers: bold, larger
- Highlighted: subtle bg tint
- Tabs: compact, underline
- TOC: slide-out panel
- Legal document feel
- On-brand (dark theme)
- NO decorative elements
```

---

## 生成顺序

1. 首页 - 奠定视觉风格
2. 剧本列表页 - 列表模式
3. 剧本详情页 - 详情模式
4. 游戏房间 - 社交准备模式
5. 聊天界面 - 核心游戏模式
6. 搜证界面 - 游戏功能模式
7. 个人资料 - 数据展示模式
8. 商城界面 - 商业化模式
9. 个人中心 - 用户信息模式
10. 钱包/充值 - 支付模式
11. 排行榜 - 竞争展示模式
12. 任务系统 - 任务模式
13. 成就系统 - 收集模式
14. 社交广场 - 社区模式
15. 语音房间 - 实时通讯模式
16. 回放系统 - 媒体播放模式
17. 推理笔记 - 画布模式
18. 邀请好友 - 增长模式
19. 新手指引 - 教学模式
20. FAQ帮助中心 - 帮助模式
21. 客服系统 - 服务模式
22. 隐私协议 - 法律文档模式

---

## 前置检查清单（Pre-Flight Check）

生成每个页面后，检查以下项目：

- [ ] 全站使用单一强调色（霓虹金 #C9A96E）
- [ ] 无纯黑 (#000000) 背景
- [ ] 圆角一致（卡片12px, 按钮8px, 标签6px）
- [ ] 无居中 Hero 内容（左对齐为主）
- [ ] 无三卡片等分布局
- [ ] 无霓虹外发光效果
- [ ] 字体使用 Cabinet Grotesk / Satoshi / JetBrains Mono
- [ ] 按钮文字与背景对比度达标
- [ ] 无 AI 紫色渐变
- [ ] 移动端折叠规则明确
- [ ] 内容密度合理（无数据堆砌）
- [ ] 无装饰性文字条（"BRAND · MOTION · SPATIAL" 类）
- [ ] 无滚动提示文字（"Scroll to explore" 类）
- [ ] 无版本号页脚
- [ ] 无装饰性状态点
- [ ] 无破折号（—）作为设计元素
- [ ] 页面主题锁定（不中途切换明暗）
- [ ] 暗色模式一致性（所有section同色系）
