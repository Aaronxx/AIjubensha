//
//  AuthView.swift
//  AI推理叙事游戏 - 登录注册界面
//

import SwiftUI

struct AuthView: View {
    @State private var isLoginMode = true
    @State private var username = ""
    @State private var email = ""
    @State private var password = ""
    @EnvironmentObject var authManager: AuthManager

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            ScrollView {
                VStack(spacing: Spacing.xxl) {
                    // Logo
                    VStack(spacing: Spacing.md) {
                        Image(systemName: "magnifyingglass.circle.fill")
                            .font(.system(size: 64))
                            .foregroundStyle(Theme.accentPrimary)
                        Text("AI推理叙事")
                            .font(.system(size: 28, weight: .bold))
                            .foregroundStyle(Theme.textPrimary)
                        Text("线上剧本杀，AI NPC 陪你推理")
                            .font(Typography.bodySecondary)
                            .foregroundStyle(Theme.textTertiary)
                    }
                    .padding(.top, 80)

                    // Form
                    VStack(spacing: Spacing.lg) {
                        AuthTextField(placeholder: "用户名", text: $username)

                        if !isLoginMode {
                            AuthTextField(placeholder: "邮箱", text: $email)
                                .keyboardType(.emailAddress)
                        }

                        AuthSecureField(placeholder: "密码", text: $password)

                        // Submit
                        NeonButton(
                            title: isLoginMode ? "登录" : "注册",
                            action: submit,
                            isLoading: authManager.isLoading
                        )
                        .disabled(isFormInvalid)
                    }
                    .padding(.horizontal, Spacing.xxl)

                    // Error
                    if let error = authManager.errorMessage {
                        Text(error)
                            .font(Typography.caption)
                            .foregroundStyle(Theme.accentError)
                    }

                    // Toggle
                    HStack {
                        Text(isLoginMode ? "还没有账号？" : "已有账号？")
                            .foregroundStyle(Theme.textTertiary)
                        Button(isLoginMode ? "去注册" : "去登录") {
                            isLoginMode.toggle()
                            authManager.errorMessage = nil
                        }
                        .foregroundStyle(Theme.accentPrimary)
                    }
                    .font(Typography.body)
                    .padding(.bottom, 40)

                    Spacer(minLength: 60)
                }
            }
        }
        .navigationBarHidden(true)
    }

    private var isFormInvalid: Bool {
        username.isEmpty || password.isEmpty || (!isLoginMode && email.isEmpty)
    }

    private func submit() {
        Task {
            if isLoginMode {
                await authManager.login(username: username, password: password)
            } else {
                await authManager.register(username: username, email: email, password: password)
            }
        }
    }
}

struct AuthTextField: View {
    let placeholder: String
    @Binding var text: String

    var body: some View {
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

struct AuthSecureField: View {
    let placeholder: String
    @Binding var text: String

    var body: some View {
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
    }
}
