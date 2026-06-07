//
//  InvestigationPhaseView.swift
//  AI推理叙事游戏 - 搜证阶段
//

import SwiftUI

struct InvestigationPhaseView: View {
    let round: Int
    let totalAP: Int
    @Binding var selectedLocation: InvestigationLocation?
    @State private var apSpent = 0
    @State private var discoveredClues: [DiscoveredClue] = []
    @State private var showClueDetail: DiscoveredClue?
    @State private var isInvestigating = false

    var apRemaining: Int { totalAP - apSpent }

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            VStack(spacing: 0) {
                // AP Bar
                HStack {
                    HStack(spacing: Spacing.xs) {
                        Image(systemName: "bolt.fill")
                            .foregroundStyle(Theme.accentGold)
                        Text("\(apRemaining)/\(totalAP)")
                            .font(Typography.statNumber)
                            .foregroundStyle(Theme.accentGold)
                    }
                    Spacer()
                    Text("第\(round)轮搜证")
                        .font(Typography.headingMD)
                        .foregroundStyle(Theme.textPrimary)
                }
                .padding(.horizontal, Spacing.containerPadding)
                .padding(.vertical, Spacing.md)
                .background(Theme.bgBottomBar)

                ScrollView {
                    VStack(spacing: Spacing.lg) {
                        // Locations
                        ForEach(locationsForRound(round)) { location in
                            LocationCard(
                                location: location,
                                apRemaining: apRemaining,
                                isInvestigating: isInvestigating
                            ) {
                                await investigate(location)
                            }
                        }

                        // Discovered clues
                        if !discoveredClues.isEmpty {
                            VStack(alignment: .leading, spacing: Spacing.md) {
                                SectionHeader(title: "已发现线索 (\(discoveredClues.count))", showMore: false)
                                    .padding(.horizontal, Spacing.containerPadding)

                                ForEach(discoveredClues) { clue in
                                    ClueCard(clue: clue) {
                                        showClueDetail = clue
                                    }
                                }
                                .padding(.horizontal, Spacing.containerPadding)
                            }
                            .padding(.top, Spacing.lg)
                        }

                        // Hint
                        CardContainer {
                            HStack(spacing: Spacing.sm) {
                                Image(systemName: "lightbulb.fill")
                                    .foregroundStyle(Theme.accentPrimary)
                                Text("提示：通过对话获得信息后，可解锁新的调查目标")
                                    .font(Typography.caption)
                                    .foregroundStyle(Theme.textSecondary)
                            }
                            .padding(Spacing.md)
                        }
                        .padding(.horizontal, Spacing.containerPadding)
                        .padding(.top, Spacing.lg)
                    }
                    .padding(.bottom, 100)
                }
            }

            // Complete button bar
            VStack {
                Spacer()
                if apRemaining == 0 || !locationsForRound(round).contains(where: { !$0.isCompleted }) {
                    GhostButton(title: "结束搜证", action: {
                        // Navigate back or advance phase
                    })
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.bottom, 40)
                }
            }
        }
        .navigationTitle("搜证")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(item: $showClueDetail) { clue in
            ClueDetailView(clue: clue)
        }
    }

    private func investigate(_ location: InvestigationLocation) async {
        guard apRemaining >= location.apCost && !location.isCompleted else { return }
        isInvestigating = true
        try? await Task.sleep(nanoseconds: 1_500_000_000)

        withAnimation {
            apSpent += location.apCost
            discoveredClues.append(contentsOf: location.clues.prefix(location.apCost).map { c in
                DiscoveredClue(name: c, location: location.name, timestamp: Date())
            })
            isInvestigating = false
        }
    }
}

// MARK: - Models
struct InvestigationLocation: Identifiable {
    let id = UUID()
    let name: String
    let icon: String
    let apCost: Int
    let isCompleted: Bool
    let isLocked: Bool
    let lockReason: String?
    let clues: [String]
}

struct DiscoveredClue: Identifiable, Hashable {
    let id = UUID()
    let name: String
    let location: String
    let timestamp: Date
}

// MARK: - Location Card
struct LocationCard: View {
    let location: InvestigationLocation
    let apRemaining: Int
    let isInvestigating: Bool
    let onInvestigate: () async -> Void

    var canInvestigate: Bool {
        apRemaining >= location.apCost && !location.isCompleted && !location.isLocked
    }

    var body: some View {
        CardContainer {
            HStack(spacing: Spacing.md) {
                Image(systemName: location.icon)
                    .font(.system(size: 24))
                    .foregroundStyle(location.isCompleted ? Theme.accentGreen : location.isLocked ? Theme.textTertiary : Theme.accentPrimary)
                    .frame(width: 40)

                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(location.name)
                        .font(Typography.headingSM)
                        .foregroundStyle(location.isLocked ? Theme.textTertiary : Theme.textPrimary)

                    if location.isLocked {
                        Text(location.lockReason ?? "需要前序线索解锁")
                            .font(Typography.caption)
                            .foregroundStyle(Theme.textTertiary)
                    } else if location.isCompleted {
                        Tag(text: "已调查", color: Theme.accentGreen)
                    } else {
                        Text("需要 \(location.apCost) AP")
                            .font(Typography.caption)
                            .foregroundStyle(Theme.textTertiary)
                    }
                }

                Spacer()

                if !location.isCompleted && !location.isLocked {
                    Button(action: { Task { await onInvestigate() } }) {
                        if isInvestigating {
                            ProgressView()
                        } else {
                            Text("调查")
                                .font(Typography.button)
                        }
                    }
                    .foregroundStyle(Theme.textOnAccent)
                    .padding(.horizontal, Spacing.lg)
                    .padding(.vertical, Spacing.sm)
                    .background(canInvestigate ? Theme.accentPrimary : Theme.textTertiary)
                    .cornerRadius(Radius.sm)
                    .disabled(!canInvestigate || isInvestigating)
                }
            }
            .padding(Spacing.lg)
        }
        .padding(.horizontal, Spacing.containerPadding)
    }
}

// MARK: - Clue Card
struct ClueCard: View {
    let clue: DiscoveredClue
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundStyle(Theme.accentPrimary)
                    .frame(width: 24)
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(clue.name)
                        .font(Typography.headingSM)
                        .foregroundStyle(Theme.textPrimary)
                    Text(clue.location)
                        .font(Typography.caption)
                        .foregroundStyle(Theme.textTertiary)
                }
                Spacer()
                Image(systemName: "chevron.right")
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
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Clue Detail View
struct ClueDetailView: View {
    let clue: DiscoveredClue
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationView {
            ZStack {
                Theme.bgApp.ignoresSafeArea()
                ScrollView {
                    CardContainer {
                        VStack(alignment: .leading, spacing: Spacing.lg) {
                            HStack {
                                Image(systemName: "doc.text.fill")
                                    .font(.system(size: 24))
                                    .foregroundStyle(Theme.accentPrimary)
                                Text(clue.name)
                                    .font(Typography.headingMD)
                                    .foregroundStyle(Theme.textPrimary)
                            }
                            ThemeDivider()
                            Text("线索内容将在这里展示。该线索在 \(clue.location) 被发现。")
                                .font(Typography.body)
                                .foregroundStyle(Theme.textSecondary)
                            ThemeDivider()
                            Text("发现时间: \(clue.timestamp, format: .dateTime.hour().minute())")
                                .font(Typography.caption)
                                .foregroundStyle(Theme.textTertiary)
                        }
                        .padding(Spacing.lg)
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.top, Spacing.xl)
                }
            }
            .navigationTitle("线索详情")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("关闭") { dismiss() }
                        .foregroundStyle(Theme.accentPrimary)
                }
            }
        }
    }
}

// MARK: - Data
func locationsForRound(_ round: Int) -> [InvestigationLocation] {
    if round == 1 {
        return [
            InvestigationLocation(name: "死者房间", icon: "door.left.hand.closed", apCost: 2, isCompleted: false, isLocked: false, lockReason: nil, clues: ["尸体周围有挣扎痕迹", "床头柜上的水杯是倒的"]),
            InvestigationLocation(name: "客厅", icon: "sofa", apCost: 1, isCompleted: false, isLocked: false, lockReason: nil, clues: ["茶几上有两杯未喝完的红酒"]),
            InvestigationLocation(name: "花园", icon: "tree", apCost: 1, isCompleted: false, isLocked: false, lockReason: nil, clues: ["花坛边缘有脚印"]),
        ]
    } else {
        return [
            InvestigationLocation(name: "死者房间·深入", icon: "magnifyingglass", apCost: 3, isCompleted: false, isLocked: false, lockReason: nil, clues: ["隐藏保险箱", "死者的日记"]),
            InvestigationLocation(name: "书房", icon: "book.fill", apCost: 2, isCompleted: false, isLocked: true, lockReason: "需要先询问管家", clues: ["书架上的密道入口"]),
            InvestigationLocation(name: "地下室", icon: "arrow.down.to.line", apCost: 3, isCompleted: false, isLocked: true, lockReason: "需要先发现书房密道", clues: ["血迹斑斑的工具"]),
        ]
    }
}
