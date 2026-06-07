//
//  RoomListView.swift
//  AI推理叙事游戏 - 房间列表
//

import SwiftUI

struct RoomListView: View {
    @State private var rooms: [Room] = []
    @State private var isLoading = true
    @State private var showCreateRoom = false
    @State private var joiningRoomId: String?

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            VStack(spacing: 0) {
                // Create button
                GhostButton(title: "+ 创建房间", action: { showCreateRoom = true })
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.vertical, Spacing.lg)

                ThemeDivider()

                if isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity, minHeight: 200)
                } else if rooms.isEmpty {
                    VStack(spacing: Spacing.lg) {
                        Image(systemName: "person.2.slash")
                            .font(.system(size: 48))
                            .foregroundStyle(Theme.textTertiary)
                        Text("暂无可用房间")
                            .font(Typography.headingMD)
                            .foregroundStyle(Theme.textSecondary)
                        Text("创建新房间邀请好友一起玩")
                            .font(Typography.bodySecondary)
                            .foregroundStyle(Theme.textTertiary)
                    }
                    .frame(maxWidth: .infinity, minHeight: 200)
                } else {
                    ScrollView {
                        LazyVStack(spacing: Spacing.md) {
                            ForEach(rooms) { room in
                                RoomRow(room: room, isJoining: joiningRoomId == room.room_id) {
                                    await joinRoom(room)
                                }
                            }
                        }
                        .padding(.horizontal, Spacing.containerPadding)
                    }
                }
            }
        }
        .navigationTitle("游戏房间")
        .sheet(isPresented: $showCreateRoom) {
            CreateRoomView()
        }
        .task { await loadRooms() }
    }

    private func loadRooms() async {
        isLoading = true
        do {
            let dtos = try await APIService.shared.fetchRooms()
            withAnimation {
                rooms = dtos.map { Room(from: $0) }
            }
        } catch {
            print("Failed to load rooms: \(error)")
            rooms = []
        }
        isLoading = false
    }

    @MainActor
    private func joinRoom(_ room: Room) async {
        joiningRoomId = room.room_id
        do {
            let _ = try await APIService.shared.joinRoom(roomId: room.room_id)
            // Navigate to game after joining
            withAnimation { rooms.removeAll { $0.room_id == room.room_id } }
        } catch {
            print("Failed to join room: \(error)")
        }
        joiningRoomId = nil
    }
}

// MARK: - Room Row
struct RoomRow: View {
    let room: Room
    let isJoining: Bool
    let onJoin: () async -> Void

    var body: some View {
        CardContainer {
            VStack(alignment: .leading, spacing: Spacing.md) {
                HStack {
                    Text(room.script_name)
                        .font(Typography.headingMD)
                        .foregroundStyle(Theme.textPrimary)
                    Spacer()
                    StatusBadgeView(
                        text: room.status == .waiting ? "等待中" : room.status == .playing ? "游戏中" : "已结束",
                        color: room.status == .waiting ? Theme.accentGreen : room.status == .playing ? Theme.accentWarning : Theme.textTertiary
                    )
                }

                HStack {
                    Label("\(room.current_players)/\(room.max_players)", systemImage: "person.fill")
                        .font(Typography.caption)
                        .foregroundStyle(Theme.textTertiary)
                    Text(room.host_name)
                        .font(Typography.caption)
                        .foregroundStyle(Theme.textTertiary)
                    if room.ai_fill {
                        Text("AI补位")
                            .font(Typography.captionTiny)
                            .foregroundStyle(Theme.accentTeal)
                            .padding(.horizontal, Spacing.sm)
                            .padding(.vertical, Spacing.xs)
                            .background(Theme.accentTeal.opacity(0.15))
                            .cornerRadius(Radius.sm)
                    }
                    Spacer()
                    if room.canJoin {
                        Button(action: { Task { await onJoin() } }) {
                            if isJoining {
                                ProgressView()
                                    .frame(width: 40)
                            } else {
                                Text("加入")
                                    .font(Typography.button)
                                    .padding(.horizontal, Spacing.xl)
                                    .padding(.vertical, Spacing.sm)
                            }
                        }
                        .foregroundStyle(Theme.textOnAccent)
                        .background(Theme.accentPrimary)
                        .cornerRadius(Radius.sm)
                        .disabled(isJoining)
                    } else if room.status == .playing {
                        Text("游戏中")
                            .font(Typography.caption)
                            .foregroundStyle(Theme.accentWarning)
                    }
                }
            }
        }
    }
}

// MARK: - Create Room View
struct CreateRoomView: View {
    @Environment(\.dismiss) var dismiss
    @State private var selectedScript = ""
    @State private var roomName = ""
    @State private var isPrivate = false
    @State private var password = ""
    @State private var isCreating = false

    var body: some View {
        NavigationView {
            ZStack {
                Theme.bgApp.ignoresSafeArea()

                ScrollView {
                    VStack(spacing: Spacing.xl) {
                        VStack(alignment: .leading, spacing: Spacing.lg) {
                            LabeledField(label: "房间名称", placeholder: "输入房间名称", text: $roomName)
                            LabeledField(label: "选择剧本ID", placeholder: "输入剧本ID", text: $selectedScript)
                        }
                        .padding(.horizontal, Spacing.containerPadding)

                        // Privacy toggle
                        HStack {
                            Text("私密房间")
                                .font(Typography.body)
                                .foregroundStyle(Theme.textPrimary)
                            Spacer()
                            Toggle("", isOn: $isPrivate)
                                .labelsHidden()
                                .tint(Theme.accentPrimary)
                        }
                        .padding(.horizontal, Spacing.containerPadding)

                        if isPrivate {
                            LabeledField(label: "房间密码", placeholder: "设置密码", text: $password, isSecure: true)
                                .padding(.horizontal, Spacing.containerPadding)
                        }

                        Spacer()

                        NeonButton(title: "创建房间", action: createRoom, isLoading: isCreating)
                            .padding(.horizontal, Spacing.containerPadding)
                    }
                    .padding(.top, Spacing.xl)
                }
            }
            .navigationTitle("创建房间")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("取消") { dismiss() }
                        .foregroundStyle(Theme.accentPrimary)
                }
            }
        }
    }

    private func createRoom() {
        guard !roomName.isEmpty && !selectedScript.isEmpty else { return }
        isCreating = true
        Task {
            do {
                let _ = try await APIService.shared.createRoom(
                    name: roomName,
                    scriptId: selectedScript
                )
                dismiss()
            } catch {
                print("Failed to create room: \(error)")
            }
            isCreating = false
        }
    }
}

struct LabeledField: View {
    let label: String
    let placeholder: String
    @Binding var text: String
    var isSecure: Bool = false

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.sm) {
            Text(label)
                .font(Typography.headingSM)
                .foregroundStyle(Theme.textSecondary)
            if isSecure {
                SecureField(placeholder, text: $text)
                    .font(Typography.body)
                    .foregroundStyle(Theme.textPrimary)
                    .padding(.vertical, Spacing.lg)
                    .padding(.horizontal, Spacing.lg)
                    .background(Theme.bgSearchBar)
                    .cornerRadius(Radius.md)
                    .overlay(
                        RoundedRectangle(cornerRadius: Radius.md)
                            .stroke(Theme.borderCard, lineWidth: 1)
                    )
            } else {
                TextField(placeholder, text: $text)
                    .font(Typography.body)
                    .foregroundStyle(Theme.textPrimary)
                    .padding(.vertical, Spacing.lg)
                    .padding(.horizontal, Spacing.lg)
                    .background(Theme.bgSearchBar)
                    .cornerRadius(Radius.md)
                    .overlay(
                        RoundedRectangle(cornerRadius: Radius.md)
                            .stroke(Theme.borderCard, lineWidth: 1)
                    )
                    .autocorrectionDisabled()
            }
        }
    }
}
