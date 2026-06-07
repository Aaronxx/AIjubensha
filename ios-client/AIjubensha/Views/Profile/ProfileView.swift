//
//  ProfileView.swift
//  AI推理叙事游戏 - 个人中心
//

import SwiftUI

struct ProfileView: View {
    @State private var userStats: PlayerStats?
    @State private var achievements: [Achievement] = []
    @State private var settlements: [SettlementRecord] = []
    @State private var isLoading = true
    @State private var showAchievements = false
    @State private var showLeaderboard = false
    @State private var showSocialSquare = false
    @State private var showMessages = false
    @State private var showHelpCenter = false
    @State private var showPrivacy = false
    @State private var showCustomerService = false
    @EnvironmentObject var authManager: AuthManager

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            ScrollView {
                VStack(spacing: 0) {
                    // Profile header (gradient)
                    VStack(spacing: Spacing.lg) {
                        AvatarView(text: authManager.currentUser?.username.prefix(1).uppercased() ?? "游", size: 64)
                        VStack(spacing: Spacing.xs) {
                            Text(authManager.currentUser?.username ?? "游客")
                                .font(Typography.headingLG)
                                .foregroundStyle(Theme.textPrimary)
                            Text("SVIP")
                                .font(Typography.tag)
                                .foregroundStyle(Theme.accentGold)
                                .padding(.horizontal, Spacing.lg)
                                .padding(.vertical, Spacing.xs)
                                .background(Theme.bgBadge)
                                .cornerRadius(Radius.sm)
                            Text("真相只有一个")
                                .font(Typography.bodySecondary)
                                .foregroundStyle(Theme.textTertiary)
                        }
                    }
                    .padding(.top, Spacing.xxl)
                    .padding(.bottom, Spacing.xl)
                    .frame(maxWidth: .infinity)
                    .background(
                        LinearGradient(
                            colors: [Theme.profileGradientStart, Theme.profileGradientEnd],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )

                    // Stats
                    HStack(spacing: 0) {
                        StatCardView(value: "\(userStats?.total_games ?? 0)", label: "总场次", valueColor: Theme.accentPrimary)
                        ThemeDivider()
                        StatCardView(
                            value: userStats.map { s in
                                s.detective_games > 0 ? String(format: "%.0f%%", Double(s.detective_success) / Double(s.detective_games) * 100) : "0%"
                            } ?? "0%",
                            label: "侦探",
                            valueColor: Theme.accentBlue
                        )
                        ThemeDivider()
                        StatCardView(value: "\(userStats?.stars_earned ?? 0)", label: "星星", valueColor: Theme.accentGold)
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.vertical, Spacing.lg)
                    .background(Theme.bgCard)
                    .padding(.horizontal, Spacing.containerPadding)

                    // Achievements
                    VStack(alignment: .leading, spacing: Spacing.lg) {
                        SectionHeader(title: "成就", showMore: false)
                            .padding(.horizontal, Spacing.containerPadding)

                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: Spacing.md) {
                                ForEach(achievements) { achievement in
                                    AchievementBadgeView(
                                        name: achievement.name,
                                        icon: achievement.icon ?? "star.fill",
                                        rarityColor: rarityColor(for: achievement.rarity)
                                    )
                                }
                            }
                            .padding(.horizontal, Spacing.containerPadding)
                        }
                    }
                    .padding(.top, Spacing.xl)

                    // Recent games
                    VStack(alignment: .leading, spacing: Spacing.lg) {
                        SectionHeader(title: "最近游戏", showMore: false)
                            .padding(.horizontal, Spacing.containerPadding)

                        ForEach(settlements.prefix(5)) { record in
                            SettlementRow(record: record)
                                .padding(.horizontal, Spacing.containerPadding)
                        }

                        if settlements.isEmpty && !isLoading {
                            Text("暂无游戏记录")
                                .font(Typography.bodySecondary)
                                .foregroundStyle(Theme.textTertiary)
                                .frame(maxWidth: .infinity)
                                .padding()
                        }
                    }
                    .padding(.top, Spacing.xl)

                    // Social & Features
                    VStack(spacing: 0) {
                        NavigationLink(destination: AchievementsView()) {
                            SettingsRow(title: "成就", icon: "star.fill")
                        }
                        ThemeDivider()
                        NavigationLink(destination: LeaderboardView()) {
                            SettingsRow(title: "排行榜", icon: "chart.bar.fill")
                        }
                        ThemeDivider()
                        NavigationLink(destination: SocialSquareView()) {
                            SettingsRow(title: "社交广场", icon: "bubble.left.and.bubble.right")
                        }
                        ThemeDivider()
                        Button(action: { showMessages = true }) {
                            SettingsRow(title: "消息", icon: "bell.fill")
                        }
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.top, Spacing.xl)

                    // Settings
                    VStack(spacing: 0) {
                        NavigationLink(destination: HelpCenterView()) {
                            SettingsRow(title: "帮助中心", icon: "questionmark.circle")
                        }
                        ThemeDivider()
                        NavigationLink(destination: CustomerServiceView()) {
                            SettingsRow(title: "客服中心", icon: "headphones")
                        }
                        ThemeDivider()
                        NavigationLink(destination: PrivacyPolicyView()) {
                            SettingsRow(title: "隐私政策", icon: "lock.shield")
                        }
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.top, Spacing.xl)

                    // Logout
                    Button(action: { authManager.logout() }) {
                        HStack {
                            Image(systemName: "rectangle.portrait.and.arrow.right")
                                .foregroundStyle(Theme.accentError)
                            Text("退出登录")
                                .foregroundStyle(Theme.accentError)
                            Spacer()
                        }
                        .padding()
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.top, Spacing.lg)
                }
                .padding(.bottom, 100)
            }
        }
        .navigationTitle("我的")
        .navigationBarTitleDisplayMode(.inline)
        .task { await loadData() }
    }

    private func rarityColor(for rarity: String) -> Color {
        switch rarity {
        case "common": return Theme.textTertiary
        case "rare": return Theme.accentBlue
        case "epic": return Theme.accentPurple
        case "legendary": return Theme.accentGold
        case "hidden": return Theme.accentError
        default: return Theme.textTertiary
        }
    }

    private func loadData() async {
        isLoading = true
        let userId = authManager.currentUser?.user_id ?? "test_user"

        do {
            let (stats, achs, settles) = try await (
                APIService.shared.getPlayerStats(playerId: userId),
                APIService.shared.getAchievements(playerId: userId),
                APIService.shared.getSettlements(playerId: userId)
            )
            withAnimation {
                userStats = PlayerStats(
                    player_id: stats.player_id,
                    total_games: stats.total_games,
                    correct_votes: stats.correct_votes,
                    detective_games: stats.detective_games,
                    detective_success: stats.detective_success,
                    murderer_games: stats.murderer_games,
                    murderer_escapes: stats.murderer_escapes,
                    stars_earned: stats.stars_earned
                )
                achievements = achs.map { Achievement(achievement_id: $0.achievement_id, name: $0.name, description: $0.description, rarity: $0.rarity, icon: $0.icon, unlocked_at: $0.unlocked_at, reward_stars: $0.reward_stars) }
                settlements = settles.map { SettlementRecord(scriptName: $0.script_name, role: $0.role, result: $0.result, date: $0.date) }
            }
        } catch {
            print("Failed to load profile data: \(error)")
        }
        isLoading = false
    }
}

struct SettlementRow: View {
    let record: SettlementRecord

    var body: some View {
        HStack {
            Text(record.scriptName)
                .font(Typography.headingSM)
                .foregroundStyle(Theme.textPrimary)
            Spacer()
            Text(record.result)
                .font(Typography.caption)
                .foregroundStyle(record.result.contains("✅") ? Theme.accentGreen : Theme.accentError)
            Text(record.date)
                .font(Typography.caption)
                .foregroundStyle(Theme.textTertiary)
        }
        .padding()
        .background(Theme.bgCard)
        .cornerRadius(Radius.md)
        .overlay(
            RoundedRectangle(cornerRadius: Radius.md)
                .stroke(Theme.borderCard, lineWidth: 1)
        )
    }
}

struct SettingsRow: View {
    let title: String
    let icon: String

    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundStyle(Theme.textSecondary)
            Text(title)
                .font(Typography.body)
                .foregroundStyle(Theme.textPrimary)
            Spacer()
            Image(systemName: "chevron.right")
                .foregroundStyle(Theme.textTertiary)
                .font(Typography.caption)
        }
        .padding()
    }
}
