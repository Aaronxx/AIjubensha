//
//  ScriptDetailView.swift
//  AI推理叙事游戏 - 剧本详情页
//

import SwiftUI

struct ScriptDetailView: View {
    let script: Script
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var appState: AppState
    @State private var isLoading = false

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            ScrollView {
                VStack(spacing: 0) {
                    // Cover
                    Theme.bgCardElevated
                        .frame(height: 200)
                        .cornerRadius(Radius.md)
                        .overlay(
                            VStack {
                                if script.is_free {
                                    Tag(text: "免费", color: Theme.accentGreen)
                                        .frame(maxWidth: .infinity, alignment: .topLeading)
                                        .padding(Spacing.md)
                                }
                                Spacer()
                                LinearGradient(
                                    colors: [.clear, Theme.bgApp],
                                    startPoint: .top,
                                    endPoint: .bottom
                                )
                                .frame(height: 80)
                            }
                        )
                        .padding(.horizontal, Spacing.containerPadding)
                        .padding(.top, Spacing.md)

                    // Title & Info
                    VStack(alignment: .leading, spacing: Spacing.md) {
                        Text(script.title)
                            .font(Typography.headingLG)
                            .foregroundStyle(Theme.textPrimary)

                        HStack(spacing: Spacing.sm) {
                            Tag(text: script.genre, color: Theme.accentSecondary)
                            Text(script.difficultyLabel)
                                .font(Typography.caption)
                                .foregroundStyle(Theme.accentGold)
                            Text("\(script.min_players)-\(script.max_players)人")
                                .font(Typography.caption)
                                .foregroundStyle(Theme.textTertiary)
                            Text("\(script.duration_minutes)分钟")
                                .font(Typography.caption)
                                .foregroundStyle(Theme.textTertiary)
                        }

                        Text(script.description)
                            .font(Typography.bodySecondary)
                            .foregroundStyle(Theme.textSecondary)
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.top, Spacing.lg)

                    // Price / Start button
                    CardContainer {
                        HStack {
                            VStack(alignment: .leading, spacing: Spacing.xs) {
                                Text(script.is_free ? "免费体验" : "兑换价格")
                                    .font(Typography.caption)
                                    .foregroundStyle(Theme.textTertiary)
                                Text(script.is_free ? "无需星星" : "\(script.price_stars) 星")
                                    .font(Typography.statNumber)
                                    .foregroundStyle(script.is_free ? Theme.accentGreen : Theme.accentGold)
                            }
                            Spacer()
                            NeonButton(title: "开始游戏", action: { appState.enterGame(sessionId: script.script_id) }, isLoading: isLoading)
                                .frame(width: 140)
                        }
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.top, Spacing.lg)

                    // Characters section (placeholder)
                    VStack(alignment: .leading, spacing: Spacing.lg) {
                        SectionHeader(title: "角色介绍", showMore: false)
                            .padding(.horizontal, Spacing.containerPadding)

                        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: Spacing.listGap) {
                            ForEach(0..<script.max_players, id: \.self) { i in
                                CharacterPreviewCard(index: i)
                            }
                        }
                        .padding(.horizontal, Spacing.containerPadding)
                    }
                    .padding(.top, Spacing.xl)
                }
                .padding(.bottom, 100)
            }
        }
        .navigationTitle("剧本详情")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("关闭") { dismiss() }
                    .foregroundStyle(Theme.accentPrimary)
            }
        }
    }
}

// MARK: - Character Preview Card
struct CharacterPreviewCard: View {
    let index: Int

    var body: some View {
        VStack(spacing: Spacing.sm) {
            AvatarView(text: "角", size: 48)
                .overlay(
                    Text("\(index + 1)")
                        .font(Typography.captionTiny)
                        .foregroundStyle(Theme.textOnAccent)
                        .frame(width: 18, height: 18)
                        .background(Theme.accentPrimary)
                        .clipShape(Circle())
                        .offset(x: 12, y: 12)
                )

            Text("角色 \(index + 1)")
                .font(Typography.headingSM)
                .foregroundStyle(Theme.textPrimary)

            Text("身份待揭晓")
                .font(Typography.caption)
                .foregroundStyle(Theme.textTertiary)
        }
        .padding(Spacing.lg)
        .background(Theme.bgCard)
        .cornerRadius(Radius.md)
        .overlay(
            RoundedRectangle(cornerRadius: Radius.md)
                .stroke(Theme.borderCard, lineWidth: 1)
        )
    }
}
