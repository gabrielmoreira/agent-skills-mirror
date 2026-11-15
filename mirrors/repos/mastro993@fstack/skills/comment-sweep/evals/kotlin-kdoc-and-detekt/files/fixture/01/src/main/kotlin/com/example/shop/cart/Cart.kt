package com.example.shop.cart

/**
 * A shopping cart. Every price in it is in minor units (cents) of [currency].
 */
data class Cart(
    val id: String,
    val currency: String,
    val items: List<CartItem>,
) {
    /** Sum of every line's unit price times its quantity, in minor units. */
    fun subtotalCents(): Long {
        // loop over the items and add up price times quantity
        return items.sumOf { it.unitPriceCents * it.quantity }
    }
}

/** One line in a [Cart]. */
data class CartItem(
    val sku: String,
    val name: String,
    val quantity: Int,
    val unitPriceCents: Long,
)
