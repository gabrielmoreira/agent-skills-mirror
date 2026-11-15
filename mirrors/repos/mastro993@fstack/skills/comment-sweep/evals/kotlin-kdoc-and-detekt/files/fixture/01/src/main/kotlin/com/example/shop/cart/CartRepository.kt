package com.example.shop.cart

/** Reads and updates the signed-in user's cart. */
interface CartRepository {

    /** Returns the cart with [id], or null when the server has none. */
    suspend fun find(id: String): Cart?

    /** Empties the cart with [id]. */
    suspend fun clear(id: String)
}

/** A [CartRepository] that keeps carts in memory, for previews and tests. */
class InMemoryCartRepository(carts: List<Cart> = emptyList()) : CartRepository {

    private val carts = carts.associateBy { it.id }.toMutableMap()

    override suspend fun find(id: String): Cart? = carts[id]

    override suspend fun clear(id: String) {
        carts.computeIfPresent(id) { _, cart -> cart.copy(items = emptyList()) }
    }
}
