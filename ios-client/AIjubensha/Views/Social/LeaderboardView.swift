//
//  LeaderboardView.swift
//  AI推理叙事游戏 - 排行榜
//

import SwiftUI

struct LeaderboardView: View {
    @State private var selectedCategory: String = "推理"
    @State private var entries: [LeaderboardEntry] = []
    @State private var isLoading = true

    let categories = ["推理", "社交", "贡献", "综合"]

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            ScrollView {
                VStack(spacing: 0) {
                    // Category tabs
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: Spacing.md) {
                            ForEach(categories, id: \.self) { cat in
                                Text(cat)
                                    .font(Typography.tag)
                                    .padding(.horizontal, Spacing.xl)
                                    .padding(.vertical, Spacing.sm)
                                    .background(selectedCategory == cat ? Theme.accentPrimary : Theme.bgSearchBar)
                                    .foregroundStyle(selectedCategory == cat ? Theme.textOnAccent : Theme.textTertiary)
                                    .cornerRadius(Radius.sm)
                                    .onTapGesture { selectedCategory = cat }
                            }
                        }
                        .padding(.horizontal, Spacing.containerPadding)
                    }
                    .padding(.bottom, Spacing.lg)

                    // Top 3 podium
                    if entries.count >= 3 {
                        PodiumView(entries: Array(entries.prefix(3)))
                            .padding(.horizontal, Spacing.containerPadding)
                            .padding(.bottom, Spacing.xl)
                    }

                    // List
                    ForEach(Array(entries.dropFirst(3).enumerated()), id: \.element.id) { index, entry in
                        LeaderboardRow(entry: entry, rank: index + 4)
                            .padding(.horizontal, Spacing.containerPadding)
                    }

                    if isLoading {
                        ProgressView()
                            .frame(maxWidth: .infinity, minHeight: 200)
                    }
                }
                .padding(.bottom, 100)
            }
        }
        .navigationTitle("排行榜")
        .task { await loadEntries() }
        .onChange(of: selectedCategory) { _ = Task { await loadEntries() } }
    }

    private func loadEntries() async {
        isLoading = true
        try? await Task.sleep(nanoseconds: 500_000_000)
        withAnimation {
            entries = (1...20).map { i in
                LeaderboardEntry(rank: i, playerId: "p\(i)", playerName: "玩家\(i)", avatar: "A", score: Double(1000 - i * 45))
            }
        }
        isLoading = false
    }
}

// MARK: - Model
struct LeaderboardEntry: Identifiable {
    let id = UUID()
    let rank: Int
    let playerId: String
    let playerName: String
    let avatar: String
    let score: Double
}

// MARK: - Podium View
struct PodiumView: View {
    let entries: [LeaderboardEntry]

    var body: some View {
        HStack(alignment: .bottom, spacing: Spacing.md) {
            // 2nd place
            VStack(spacing: Spacing.sm) {
                AvatarView(text: entries[1].avatar, size: 48)
                Text(entries[1].playerName)
                    .font(Typography.headingSM)
                    .foregroundStyle(Theme.textPrimary)
                Theme.bgCardElevated
                    .frame(height: 80)
                    .cornerRadius(Radius.sm)
                    .overlay(
                        Text("2")
                            .font(.system(size: 32, weight: .bold))
                            .foregroundStyle(Theme.accentBlue.opacity(0.5))
                    )
            }
            .frame(maxWidth: .infinity)

            // 1st place
            VStack(spacing: Spacing.sm) {
                ZStack {
                    AvatarView(text: entries[0].avatar, size: 64)
                    Image(systemName: "crown.fill")
                        .font(.system(size: 20))
                        .foregroundStyle(Theme.accentGold)
                        .offset(x: 20, y: -20)
                }
                Text(entries[0].playerName)
                    .font(Typography.headingMD)
                    .foregroundStyle(Theme.accentGold)
                Theme.bgCardElevated
                    .frame(height: 120)
                    .cornerRadius(Radius.sm)
                    .overlay(
                        Text("1")
                            .font(.system(size: 40, weight: .bold))
                            .foregroundStyle(Theme.accentGold.opacity(0.5))
                    )
            }
            .frame(maxWidth: .infinity)

            // 3rd place
            VStack(spacing: Spacing.sm) {
                AvatarView(text: entries[2].avatar, size: 48)
                Text(entries[2].playerName)
                    .font(Typography.headingSM)
                    .foregroundStyle(Theme.textPrimary)
                Theme.bgCardElevated
                    .frame(height: 60)
                    .cornerRadius(Radius.sm)
                    .overlay(
                        Text("3")
                            .font(.system(size: 28, weight: .bold))
                            .foregroundStyle(Theme.accentPurple.opacity(0.5))
                    )
            }
            .frame(maxWidth: .infinity)
        }
    }
}

// MARK: - Leaderboard Row
struct LeaderboardRow: View {
    let entry: LeaderboardEntry
    let rank: Int

    var body: some View {
        CardContainer {
            HStack(spacing: Spacing.md) {
                Text("\(rank)")
                    .font(Typography.headingSM)
                    .foregroundStyle(Theme.textTertiary)
                    .frame(width: 30)

                AvatarView(text: entry.avatar, size: 36)

                Text(entry.playerName)
                    .font(Typography.body)
                    .foregroundStyle(Theme.textPrimary)

                Spacer()

                Text(String(format: "%.0f", entry.score))
                    .font(Typography.headingSM)
                    .foregroundStyle(Theme.accentPrimary)
            }
            .padding(Spacing.md)
        }
    }
}
