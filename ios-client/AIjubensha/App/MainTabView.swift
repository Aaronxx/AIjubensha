//
//  MainTabView.swift
//  AI推理叙事游戏 - 主标签页
//

import SwiftUI

struct MainTabView: View {
    @State private var selectedTab = 0
    @EnvironmentObject var authManager: AuthManager

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            TabView(selection: $selectedTab) {
                tab(for: 0, icon: "house.fill", title: "首页") {
                    NavigationView { HomeView() }
                }
                tab(for: 1, icon: "person.3.fill", title: "房间") {
                    NavigationView { RoomListView() }
                }
                tab(for: 2, icon: "gamecontroller.fill", title: "游戏") {
                    NavigationView { GameView() }
                }
                tab(for: 3, icon: "cart.fill", title: "商城") {
                    NavigationView { ShopView() }
                }
                tab(for: 4, icon: "person.fill", title: "我的") {
                    NavigationView { ProfileView() }
                }
            }
            .tint(Theme.accentPrimary)
        }
    }

    @ViewBuilder
    private func tab<Content: View>(for tag: Int, icon: String, title: String, @ViewBuilder content: () -> Content) -> some View {
        content()
            .tabItem {
                VStack(spacing: 2) {
                    Image(systemName: icon)
                        .font(.system(size: 20))
                    Text(title)
                        .font(.system(size: 10))
                }
            }
            .tag(tag)
    }
}
