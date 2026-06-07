//
//  HomeView.swift
//  AI推理叙事游戏 - 首页
//

import SwiftUI

struct HomeView: View {
    @State private var scripts: [Script] = []
    @State private var isLoading = true
    @State private var selectedGenre: String = "全部"
    @State private var searchText = ""
    @EnvironmentObject var appState: AppState

    let genres = ["全部", "本格推理", "社交博弈", "情感沉浸"]

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    // Header
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        Text("推理叙事")
                            .font(Typography.headingLG)
                            .foregroundStyle(Theme.textPrimary)
                        Text("选择剧本，开始你的推理之旅")
                            .font(Typography.bodySecondary)
                            .foregroundStyle(Theme.textTertiary)
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.top, Spacing.md)
                    .padding(.bottom, Spacing.lg)

                    // Search
                    ThemeSearchField(text: $searchText)
                        .padding(.horizontal, Spacing.containerPadding)
                        .padding(.bottom, Spacing.lg)

                    // Genre filter
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: Spacing.md) {
                            ForEach(genres, id: \.self) { genre in
                                Text(genre)
                                    .font(Typography.tag)
                                    .padding(.horizontal, Spacing.lg)
                                    .padding(.vertical, Spacing.sm)
                                    .background(selectedGenre == genre ? Theme.accentPrimary : Theme.bgSearchBar)
                                    .foregroundStyle(selectedGenre == genre ? Theme.textOnAccent : Theme.textTertiary)
                                    .cornerRadius(Radius.sm)
                                    .onTapGesture { selectedGenre = genre }
                            }
                        }
                        .padding(.horizontal, Spacing.containerPadding)
                    }
                    .padding(.bottom, Spacing.lg)

                    // Featured banner
                    if !filteredScripts.isEmpty {
                        NavigationLink(destination: ScriptDetailView(script: filteredScripts[0])) {
                            FeaturedScriptCard(script: filteredScripts[0])
                        }
                        .buttonStyle(PlainButtonStyle())
                        .padding(.horizontal, Spacing.containerPadding)
                        .padding(.bottom, Spacing.lg)
                    }

                    // Section header
                    SectionHeader(title: "热门剧本", showMore: false)
                        .padding(.bottom, Spacing.md)

                    // Script grid
                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: Spacing.listGap) {
                        ForEach(Array(filteredScripts.dropFirst())) { script in
                            NavigationLink(destination: ScriptDetailView(script: script)) {
                                ScriptCard(script: script)
                            }
                        }
                    }
                    .padding(.horizontal, Spacing.containerPadding)

                    if isLoading {
                        ProgressView()
                            .frame(maxWidth: .infinity, minHeight: 200)
                    } else if filteredScripts.isEmpty {
                        VStack(spacing: Spacing.lg) {
                            Image(systemName: "doc.text.magnifyingglass")
                                .font(.system(size: 48))
                                .foregroundStyle(Theme.textTertiary)
                            Text("暂无剧本")
                                .font(Typography.headingMD)
                                .foregroundStyle(Theme.textSecondary)
                        }
                        .frame(maxWidth: .infinity, minHeight: 200)
                    }
                }
                .padding(.bottom, 100)
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        .task { await loadScripts() }
    }

    private var filteredScripts: [Script] {
        var result = scripts
        if selectedGenre != "全部" {
            result = result.filter { $0.genre == selectedGenre }
        }
        if !searchText.isEmpty {
            result = result.filter { $0.title.localizedStandardContains(searchText) }
        }
        return result
    }

    private func loadScripts() async {
        isLoading = true
        do {
            let dtos = try await APIService.shared.fetchScripts()
            withAnimation {
                scripts = dtos.map { Script(from: $0) }
            }
        } catch {
            print("Failed to load scripts: \(error)")
            scripts = []
        }
        isLoading = false
    }
}

// MARK: - Featured Script Card
struct FeaturedScriptCard: View {
    let script: Script

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.md) {
            // Cover
            ZStack {
                Theme.bgCardElevated
                    .frame(height: 140)
                    .cornerRadius(Radius.md)

                if script.is_free {
                    Tag(text: "免费", color: Theme.accentGreen)
                        .padding(Spacing.md)
                        .frame(maxWidth: .infinity, alignment: .topLeading)
                }
            }

            Text(script.title)
                .font(Typography.headingMD)
                .foregroundStyle(Theme.textPrimary)
                .lineLimit(1)

            HStack(spacing: Spacing.sm) {
                Tag(text: script.genre, color: Theme.accentSecondary)
                Text(script.difficultyLabel)
                    .font(Typography.caption)
                    .foregroundStyle(Theme.accentGold)
                Spacer()
                Text("\(script.min_players)-\(script.max_players)人")
                    .font(Typography.caption)
                    .foregroundStyle(Theme.textTertiary)
            }

            HStack {
                Text(script.description)
                    .font(Typography.bodySecondary)
                    .foregroundStyle(Theme.textTertiary)
                    .lineLimit(2)
                Spacer()
            }
        }
        .padding(Spacing.lg)
        .background(Theme.bgCardHighlight)
        .cornerRadius(Radius.md)
        .overlay(
            RoundedRectangle(cornerRadius: Radius.md)
                .stroke(Theme.accentPurple.opacity(0.3), lineWidth: 1)
        )
    }
}

// MARK: - Script Card
struct ScriptCard: View {
    let script: Script

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.sm) {
            // Cover
            ZStack {
                Theme.bgCard
                    .frame(height: 100)
                    .cornerRadius(Radius.sm)

                if script.is_free {
                    Tag(text: "免费", color: Theme.accentGreen)
                        .padding(Spacing.sm)
                        .frame(maxWidth: .infinity, alignment: .topLeading)
                }
            }

            Text(script.title)
                .font(Typography.headingSM)
                .foregroundStyle(Theme.textPrimary)
                .lineLimit(1)

            HStack(spacing: Spacing.xs) {
                Tag(text: script.genre, color: Theme.accentSecondary)
                Text(script.difficultyLabel)
                    .font(Typography.captionTiny)
                    .foregroundStyle(Theme.accentGold)
            }

            HStack {
                Label("\(script.min_players)-\(script.max_players)人", systemImage: "person.fill")
                    .font(Typography.captionTiny)
                    .foregroundStyle(Theme.textTertiary)
                Spacer()
                Text(script.is_unlocked ? "已解锁" : "\(script.price_stars)星")
                    .font(Typography.caption)
                    .foregroundStyle(script.is_unlocked ? Theme.accentGreen : Theme.accentPrimary)
            }
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
