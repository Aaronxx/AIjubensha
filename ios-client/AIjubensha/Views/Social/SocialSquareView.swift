//
//  SocialSquareView.swift
//  AI推理叙事游戏 - 社交广场
//

import SwiftUI

struct SocialSquareView: View {
    @State private var posts: [SocialPost] = []
    @State private var selectedTab: String = "热门"
    @State private var isLoading = true
    @State private var showNewPost = false

    let tabs = ["热门", "最新", "评价", "话题"]

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            VStack(spacing: 0) {
                // Tab bar
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: Spacing.lg) {
                        ForEach(tabs, id: \.self) { tab in
                            Text(tab)
                                .font(Typography.body)
                                .foregroundStyle(selectedTab == tab ? Theme.accentPrimary : Theme.textTertiary)
                                .padding(.vertical, Spacing.sm)
                                .onTapGesture { selectedTab = tab }
                        }
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                }
                .overlay(
                    Rectangle()
                        .frame(height: 1)
                        .foregroundStyle(Theme.borderCard),
                    alignment: .bottom
                )

                // Posts list
                ScrollView {
                    LazyVStack(spacing: Spacing.md) {
                        ForEach(posts) { post in
                            PostCard(post: post)
                        }
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.top, Spacing.md)

                    if isLoading {
                        ProgressView()
                            .frame(maxWidth: .infinity, minHeight: 200)
                    }
                }
            }
        }
        .navigationTitle("社交广场")
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button(action: { showNewPost = true }) {
                    Image(systemName: "square.and.pencil")
                        .foregroundStyle(Theme.accentPrimary)
                }
            }
        }
        .sheet(isPresented: $showNewPost) {
            NewPostView()
        }
        .task { await loadPosts() }
    }

    private func loadPosts() async {
        isLoading = true
        try? await Task.sleep(nanoseconds: 500_000_000)
        withAnimation {
            posts = samplePosts
        }
        isLoading = false
    }
}

// MARK: - Models
struct SocialPost: Identifiable {
    let id: String
    let authorName: String
    let avatar: String
    let content: String
    let scriptTag: String?
    let timestamp: String
    let likes: Int
    let comments: Int
    let isLiked: Bool
}

let samplePosts: [SocialPost] = [
    SocialPost(id: "1", authorName: "推理小王", avatar: "推", content: "山庄晚宴的核诡太精彩了！最后发现是密室的时候整个人起鸡皮疙瘩", scriptTag: "山庄晚宴", timestamp: "2小时前", likes: 42, comments: 12, isLiked: true),
    SocialPost(id: "2", authorName: "探案达人", avatar: "探", content: "有人愿意一起拼车午夜列车吗？缺3人，AI补位也行", scriptTag: nil, timestamp: "4小时前", likes: 15, comments: 8, isLiked: false),
    SocialPost(id: "3", authorName: "真相猎手", avatar: "真", content: "第三次刷蝴蝶之翼了，每次结局都不一样，蝴蝶效应系统真的绝", scriptTag: "蝴蝶之翼", timestamp: "6小时前", likes: 89, comments: 23, isLiked: false),
]

// MARK: - Post Card
struct PostCard: View {
    let post: SocialPost

    var body: some View {
        CardContainer {
            VStack(alignment: .leading, spacing: Spacing.md) {
                // Author
                HStack {
                    AvatarView(text: post.avatar, size: 32)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(post.authorName)
                            .font(Typography.headingSM)
                            .foregroundStyle(Theme.textPrimary)
                        Text(post.timestamp)
                            .font(Typography.captionTiny)
                            .foregroundStyle(Theme.textTertiary)
                    }
                    Spacer()
                    if let scriptTag = post.scriptTag {
                        Tag(text: scriptTag, color: Theme.accentSecondary)
                    }
                }

                // Content
                Text(post.content)
                    .font(Typography.body)
                    .foregroundStyle(Theme.textSecondary)
                    .lineSpacing(4)

                // Actions
                HStack(spacing: Spacing.xl) {
                    Button(action: {}) {
                        HStack(spacing: Spacing.xs) {
                            Image(systemName: post.isLiked ? "heart.fill" : "heart")
                                .foregroundStyle(post.isLiked ? Theme.accentError : Theme.textTertiary)
                            Text("\(post.likes)")
                                .foregroundStyle(post.isLiked ? Theme.accentError : Theme.textTertiary)
                        }
                    }

                    Button(action: {}) {
                        HStack(spacing: Spacing.xs) {
                            Image(systemName: "bubble.left")
                                .foregroundStyle(Theme.textTertiary)
                            Text("\(post.comments)")
                                .foregroundStyle(Theme.textTertiary)
                        }
                    }

                    Spacer()
                    Button(action: {}) {
                        Image(systemName: "arrowshape.turn.up.right")
                            .foregroundStyle(Theme.textTertiary)
                    }
                }
                .font(Typography.caption)
            }
            .padding(Spacing.lg)
        }
    }
}

// MARK: - New Post View
struct NewPostView: View {
    @Environment(\.dismiss) var dismiss
    @State private var content = ""
    @State private var selectedScript = ""

    var body: some View {
        NavigationView {
            ZStack {
                Theme.bgApp.ignoresSafeArea()
                ScrollView {
                    VStack(spacing: Spacing.xl) {
                        TextEditor(text: $content)
                            .font(Typography.body)
                            .foregroundStyle(Theme.textPrimary)
                            .padding()
                            .background(Theme.bgCard)
                            .cornerRadius(Radius.md)
                            .overlay(
                                RoundedRectangle(cornerRadius: Radius.md)
                                    .stroke(Theme.borderCard, lineWidth: 1)
                            )
                            .frame(minHeight: 200)
                            .padding(.horizontal, Spacing.containerPadding)

                        // Script tag
                        HStack {
                            Text("关联剧本")
                                .foregroundStyle(Theme.textSecondary)
                            Spacer()
                            Button(action: {}) {
                                Text(selectedScript.isEmpty ? "选择剧本" : selectedScript)
                                    .foregroundStyle(Theme.accentPrimary)
                            }
                        }
                        .padding(.horizontal, Spacing.containerPadding)
                    }
                    .padding(.top, Spacing.xl)
                }
            }
            .navigationTitle("发动态")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("取消") { dismiss() }
                        .foregroundStyle(Theme.textSecondary)
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("发布") { dismiss() }
                        .foregroundStyle(content.isEmpty ? Theme.textTertiary : Theme.accentPrimary)
                        .disabled(content.isEmpty)
                }
            }
        }
    }
}
