//
//  ShopView.swift
//  AI推理叙事游戏 - 商城
//

import SwiftUI

struct ShopView: View {
    @State private var products: [ShopProduct] = []
    @State private var starsBalance = 0
    @State private var selectedCategory: String = "全部"
    @State private var showRechargeSheet = false
    @State private var isLoading = true
    @State private var purchasingProductId: String?

    let categories = ["全部", "剧本", "主题", "头像框", "礼物"]

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            ScrollView {
                VStack(spacing: 0) {
                    // Balance card
                    CardContainer {
                        HStack {
                            HStack(spacing: Spacing.xs) {
                                Image(systemName: "star.fill")
                                    .foregroundStyle(Theme.accentGold)
                                Text("\(starsBalance)")
                                    .font(Typography.statNumber)
                                    .foregroundStyle(Theme.accentGold)
                            }
                            Spacer()
                            Button(action: { showRechargeSheet = true }) {
                                Text("充值")
                                    .font(Typography.button)
                                    .foregroundStyle(Theme.textOnAccent)
                                    .padding(.horizontal, Spacing.xl)
                                    .padding(.vertical, Spacing.sm)
                                    .background(Theme.accentPrimary)
                                    .cornerRadius(Radius.sm)
                            }
                        }
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.bottom, Spacing.lg)

                    // Category filter
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: Spacing.md) {
                            ForEach(categories, id: \.self) { category in
                                Text(category)
                                    .font(Typography.tag)
                                    .padding(.horizontal, Spacing.lg)
                                    .padding(.vertical, Spacing.sm)
                                    .background(selectedCategory == category ? Theme.accentPrimary : Theme.bgSearchBar)
                                    .foregroundStyle(selectedCategory == category ? Theme.textOnAccent : Theme.textTertiary)
                                    .cornerRadius(Radius.sm)
                                    .onTapGesture { selectedCategory = category }
                            }
                        }
                        .padding(.horizontal, Spacing.containerPadding)
                    }
                    .padding(.bottom, Spacing.lg)

                    // Product grid
                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: Spacing.listGap) {
                        ForEach(filteredProducts) { product in
                            ProductCard(product: product, isPurchasing: purchasingProductId == product.product_id) {
                                await purchase(product)
                            }
                        }
                    }
                    .padding(.horizontal, Spacing.containerPadding)

                    if isLoading {
                        ProgressView()
                            .frame(maxWidth: .infinity, minHeight: 200)
                    } else if products.isEmpty {
                        VStack(spacing: Spacing.lg) {
                            Image(systemName: "cart.badge.plus")
                                .font(.system(size: 48))
                                .foregroundStyle(Theme.textTertiary)
                            Text("暂无商品")
                                .font(Typography.headingMD)
                                .foregroundStyle(Theme.textSecondary)
                        }
                        .frame(maxWidth: .infinity, minHeight: 200)
                    }
                }
                .padding(.bottom, 100)
            }
        }
        .navigationTitle("商城")
        .sheet(isPresented: $showRechargeSheet) {
            RechargeView()
        }
        .task { await loadProducts() }
    }

    private var filteredProducts: [ShopProduct] {
        selectedCategory == "全部" ? products : products.filter { $0.category == selectedCategory }
    }

    private func loadProducts() async {
        isLoading = true
        do {
            let (dtos, balance) = try await (
                APIService.shared.fetchProducts(),
                APIService.shared.getStarsBalance()
            )
            withAnimation {
                products = dtos.map { ShopProduct(from: $0) }
                starsBalance = balance.balance
            }
        } catch {
            print("Failed to load products: \(error)")
            products = []
        }
        isLoading = false
    }

    @MainActor
    private func purchase(_ product: ShopProduct) async {
        purchasingProductId = product.product_id
        do {
            try await APIService.shared.purchaseProduct(productId: product.product_id)
            // Refresh balance after purchase
            let balance = try await APIService.shared.getStarsBalance()
            starsBalance = balance.balance
        } catch {
            print("Purchase failed: \(error)")
        }
        purchasingProductId = nil
    }
}

// MARK: - Product Card
struct ProductCard: View {
    let product: ShopProduct
    let isPurchasing: Bool
    let onPurchase: () async -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.sm) {
            // Preview image placeholder
            Theme.bgSearchBar
                .frame(height: 100)
                .cornerRadius(Radius.sm)

            Text(product.name)
                .font(Typography.headingSM)
                .foregroundStyle(Theme.textPrimary)
                .lineLimit(1)

            Text(product.description)
                .font(Typography.caption)
                .foregroundStyle(Theme.textTertiary)
                .lineLimit(2)

            HStack {
                Image(systemName: "star.fill")
                    .foregroundStyle(Theme.accentGold)
                    .font(Typography.captionTiny)
                Text("\(product.price_stars)")
                    .font(Typography.headingSM)
                    .foregroundStyle(Theme.accentGold)
                Spacer()
                Button(action: { Task { await onPurchase() } }) {
                    if isPurchasing {
                        ProgressView()
                            .frame(width: 30)
                    } else {
                        Text("购买")
                    }
                }
                .font(Typography.caption)
                .foregroundStyle(Theme.textOnAccent)
                .padding(.horizontal, Spacing.lg)
                .padding(.vertical, Spacing.xs)
                .background(Theme.accentPrimary)
                .cornerRadius(Radius.sm)
                .disabled(isPurchasing)
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

// MARK: - Recharge View
struct RechargeView: View {
    @Environment(\.dismiss) var dismiss

    let tiers = [
        (id: "tier_6", amount: 6, stars: 60),
        (id: "tier_30", amount: 30, stars: 310),
        (id: "tier_68", amount: 68, stars: 710),
        (id: "tier_128", amount: 128, stars: 1360),
        (id: "tier_328", amount: 328, stars: 3560),
        (id: "tier_648", amount: 648, stars: 7160)
    ]

    var body: some View {
        NavigationView {
            ZStack {
                Theme.bgApp.ignoresSafeArea()

                List(tiers, id: \.id) { tier in
                    HStack {
                        VStack(alignment: .leading) {
                            Text("\(tier.stars) 星星")
                                .font(Typography.headingMD)
                                .foregroundStyle(Theme.textPrimary)
                            if tier.stars != tier.amount * 10 {
                                Text("含赠送 \(tier.stars - tier.amount * 10) 星")
                                    .font(Typography.caption)
                                    .foregroundStyle(Theme.accentGreen)
                            }
                        }
                        Spacer()
                        Text("¥\(tier.amount)")
                            .font(Typography.statNumber)
                            .foregroundStyle(Theme.accentPrimary)
                    }
                    .padding(.vertical, Spacing.md)
                    .contentShape(Rectangle())
                    .onTapGesture {
                        // Process recharge (needs native Apple Pay / in-app purchase)
                    }
                }
                .scrollContentBackground(.hidden)
                .listRowBackground(Theme.bgCard)
            }
            .navigationTitle("充值")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("取消") { dismiss() }
                        .foregroundStyle(Theme.accentPrimary)
                }
            }
        }
    }
}
