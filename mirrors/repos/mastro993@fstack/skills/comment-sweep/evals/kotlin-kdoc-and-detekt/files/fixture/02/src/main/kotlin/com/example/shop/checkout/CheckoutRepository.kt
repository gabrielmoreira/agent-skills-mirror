package com.example.shop.checkout

import com.example.shop.cart.Cart
import com.example.shop.cart.CartRepository
import java.io.IOException
import retrofit2.HttpException

/**
 * Places orders for the signed-in user's cart, and clears the cart once an order goes through.
 */
class CheckoutRepository(
    private val api: CheckoutApi,
    private val carts: CartRepository,
) {

    /**
     * Gets the cart.
     * @param id the id
     * @return the cart
     */
    suspend fun getCart(id: String): Cart? = carts.find(id)

    /**
     * Fetches the quote for [cart].
     *
     * @throws CheckoutException if the server can't be reached or rejects the cart.
     */
    suspend fun quote(cart: Cart): QuoteDto {
        // call the api
        return callApi { api.quote(cart.id) }
    }

    /**
     * Places an order for every item in [cart], then clears the cart.
     *
     * The amount sent is the cart subtotal in minor units (cents for EUR), never a decimal amount.
     *
     * @throws IllegalStateException if [cart] has no items.
     * @throws CheckoutException if the server can't be reached or rejects the order.
     */
    suspend fun placeOrder(cart: Cart): OrderDto {
        // TODO: throw when the cart is empty
        check(cart.items.isNotEmpty()) { "Cannot check out cart ${cart.id}: it has no items" }

        // build the request
        val request = OrderRequest(
            cartId = cart.id,
            amount = cart.subtotalCents(),
            currency = cart.currency,
        )
        // call the api
        val order = callApi { api.placeOrder(request) }
        // Log.d(TAG, "placed order ${order.id} for cart ${cart.id}")
        carts.clear(cart.id)
        return order
    }

    private suspend fun <T> callApi(block: suspend () -> T): T = try {
        block()
    } catch (e: HttpException) {
        // wrap the error
        throw CheckoutException("$API_LABEL rejected the request: HTTP ${e.code()}", e)
    } catch (e: IOException) {
        throw CheckoutException("$API_LABEL is unreachable", e)
    }
}

/** A checkout request failed; [message] is safe to show to the user. */
class CheckoutException(message: String, cause: Throwable) : Exception(message, cause)
