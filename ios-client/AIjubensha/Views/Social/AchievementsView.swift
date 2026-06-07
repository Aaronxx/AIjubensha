//
//  AchievementsView.swift
//  AI推理叙事游戏 - 成就页面
//

import SwiftUI

struct AchievementsView: View {
    @State private var achievements: [AchievementItem] = []
    @State private var selectedFilter: String = "全部"
    @State private var isLoading = true

    let filters = ["全部", "推理", "演技", "社交", "收藏", "挑战", "隐藏"]

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            ScrollView {
                VStack(spacing: 0) {
                    // Progress summary
                    CardContainer {
                        HStack {
                            VStack(alignment: .leading, spacing: Spacing.xs) {
                                Text("已获得")
                                    .font(Typography.caption)
                                    .foregroundStyle(Theme.textTertiary)
                                Text("\(achievements.filter { $0.isUnlocked }.count) / \(achievements.count)")
                                    .font(Typography.statNumber)
                                    .foregroundStyle(Theme.accentGold)
                            }
                            Spacer()
                            VStack(alignment: .trailing, spacing: Spacing.xs) {
                                Text("总奖励")
                                    .font(Typography.caption)
                                    .foregroundStyle(Theme.textTertiary)
                                Text("\(achievements.filter { $0.isUnlocked }.reduce(0) { $0 + $1.rewardStars }) 星")
                                    .font(Typography.statNumber)
                                    .foregroundStyle(Theme.accentGold)
                            }
                        }
                        .padding(Spacing.lg)
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.bottom, Spacing.lg)

                    // Filter tabs
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: Spacing.md) {
                            ForEach(filters, id: \.self) { filter in
                                Text(filter)
                                    .font(Typography.tag)
                                    .padding(.horizontal, Spacing.lg)
                                    .padding(.vertical, Spacing.sm)
                                    .background(selectedFilter == filter ? Theme.accentPrimary : Theme.bgSearchBar)
                                    .foregroundStyle(selectedFilter == filter ? Theme.textOnAccent : Theme.textTertiary)
                                    .cornerRadius(Radius.sm)
                                    .onTapGesture { selectedFilter = filter }
                            }
                        }
                        .padding(.horizontal, Spacing.containerPadding)
                    }
                    .padding(.bottom, Spacing.lg)

                    // Achievement list
                    LazyVStack(spacing: Spacing.md) {
                        ForEach(filteredAchievements) { achievement in
                            AchievementCard(achievement: achievement)
                        }
                    }
                    .padding(.horizontal, Spacing.containerPadding)

                    if isLoading {
                        ProgressView()
                            .frame(maxWidth: .infinity, minHeight: 200)
                    }
                }
                .padding(.bottom, 100)
            }
        }
        .navigationTitle("成就")
        .task { await loadAchievements() }
    }

    private var filteredAchievements: [AchievementItem] {
        if selectedFilter == "全部" { return achievements }
        return achievements.filter { $0.category == selectedFilter }
    }

    private func loadAchievements() async {
        isLoading = true
        try? await Task.sleep(nanoseconds: 500_000_000)
        withAnimation {
            achievements = sampleAchievements
        }
        isLoading = false
    }
}

// MARK: - Model
struct AchievementItem: Identifiable {
    let id: String
    let name: String
    let description: String
    let category: String
    let rarity: String  // common, rare, epic, legendary, hidden
    let icon: String
    let rewardStars: Int
    let isUnlocked: Bool
    let unlockedDate: String?
    let progress: Double?  // 0-1, nil if binary
    let progressLabel: String?
}

let sampleAchievements: [AchievementItem] = [
    AchievementItem(id: "a1", name: "初出茅庐", description: "首次投对真凶", category: "推理", rarity: "common", icon: "sparkles", rewardStars: 10, isUnlocked: true, unlockedDate: "2026-05-20", progress: nil, progressLabel: nil),
    AchievementItem(id: "a2", name: "火眼金睛", description: "单局投对且发现全部关键证据", category: "推理", rarity: "rare", icon: "eye.fill", rewardStars: 20, isUnlocked: false, unlockedDate: nil, progress: 0.7, progressLabel: "5/7 关键证据"),
    AchievementItem(id: "a3", name: "神探", description: "连续5局投对真凶", category: "推理", rarity: "epic", icon: "brain.head.profile", rewardStars: 50, isUnlocked: false, unlockedDate: nil, progress: 0.6, progressLabel: "3/5 连续"),
    AchievementItem(id: "a4", name: "初次逃脱", description: "首次作为凶手未被投出", category: "演技", rarity: "common", icon: "figure.run", rewardStars: 10, isUnlocked: true, unlockedDate: "2026-05-18", progress: nil, progressLabel: nil),
    AchievementItem(id: "a5", name: "影帝", description: "凶手身份连续3局逃脱", category: "演技", rarity: "epic", icon: "theatermasks.fill", rewardStars: 50, isUnlocked: false, unlockedDate: nil, progress: 0.67, progressLabel: "2/3 逃脱"),
    AchievementItem(id: "a6", name: "广结良缘", description: "添加10位好友", category: "社交", rarity: "common", icon: "person.2.fill", rewardStars: 10, isUnlocked: true, unlockedDate: "2026-05-10", progress: nil, progressLabel: nil),
    AchievementItem(id: "a7", name: "速通达人", description: "60分钟内通关标准难度", category: "挑战", rarity: "rare", icon: "stopwatch.fill", rewardStars: 30, isUnlocked: false, unlockedDate: nil, progress: nil, progressLabel: nil),
    AchievementItem(id: "a8", name: "???", description: "???", category: "隐藏", rarity: "hidden", icon: "questionmark.app", rewardStars: 30, isUnlocked: false, unlockedDate: nil, progress: nil, progressLabel: "条件未知"),
]

// MARK: - Achievement Card
struct AchievementCard: View {
    let achievement: AchievementItem

    var rarityColor: Color {
        switch achievement.rarity {
        case "common": return Theme.textTertiary
        case "rare": return Theme.accentBlue
        case "epic": return Theme.accentPurple
        case "legendary": return Theme.accentGold
        case "hidden": return Theme.accentError
        default: return Theme.textTertiary
        }
    }

    var body: some View {
        CardContainer {
            HStack(spacing: Spacing.md) {
                ZStack {
                    Image(systemName: achievement.icon)
                        .font(.system(size: 28))
                        .foregroundStyle(achievement.isUnlocked ? rarityColor : Theme.textTertiary.opacity(0.3))
                        .frame(width: 48, height: 48)
                        .background(achievement.isUnlocked ? rarityColor.opacity(0.1) : Theme.bgSearchBar)
                        .cornerRadius(Radius.sm)

                    if !achievement.isUnlocked && achievement.rarity == "hidden" {
                        Image(systemName: "lock.fill")
                            .font(.system(size: 14))
                            .foregroundStyle(Theme.textTertiary)
                            .offset(x: 14, y: 14)
                    }
                }

                VStack(alignment: .leading, spacing: Spacing.xs) {
                    HStack {
                        Text(achievement.name)
                            .font(Typography.headingSM)
                            .foregroundStyle(achievement.isUnlocked ? Theme.textPrimary : Theme.textTertiary)

                        Tag(text: rarityLabel(for: achievement.rarity), color: rarityColor)
                    }

                    Text(achievement.isUnlocked ? achievement.description : (achievement.rarity == "hidden" ? "???" : achievement.description))
                        .font(Typography.caption)
                        .foregroundStyle(Theme.textTertiary)

                    if let progress = achievement.progress, let label = achievement.progressLabel {
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            ProgressView(value: progress)
                                .tint(rarityColor)
                            Text(label)
                                .font(Typography.captionTiny)
                                .foregroundStyle(Theme.textTertiary)
                        }
                        .padding(.top, Spacing.xs)
                    }
                }

                Spacer()

                if achievement.isUnlocked {
                    VStack(alignment: .trailing, spacing: Spacing.xs) {
                        Image(systemName: "checkmark.seal.fill")
                            .foregroundStyle(Theme.accentGreen)
                        Text("+\(achievement.rewardStars)")
                            .font(Typography.caption)
                            .foregroundStyle(Theme.accentGold)
                    }
                } else {
                    Text("\(achievement.rewardStars)星")
                        .font(Typography.caption)
                        .foregroundStyle(Theme.textTertiary)
                }
            }
            .padding(Spacing.md)
        }
        .opacity(achievement.isUnlocked ? 1 : 0.6)
    }

    func rarityLabel(_ rarity: String) -> String {
        switch rarity {
        case "common": return "普通"
        case "rare": return "稀有"
        case "epic": return "史诗"
        case "legendary": return "传说"
        case "hidden": return "隐藏"
        default: return rarity
        }
    }
}
