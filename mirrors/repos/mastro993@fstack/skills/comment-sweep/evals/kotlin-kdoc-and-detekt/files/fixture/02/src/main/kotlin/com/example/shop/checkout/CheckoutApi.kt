package com.example.shop.checkout

import com.example.shop.net.HttpClients
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

// Paths in CheckoutApi have no leading slash: Retrofit resolves "/checkout/..." against the host
// root and drops the /v2/ from this base URL.
// https://square.github.io/retrofit/2.x/retrofit/retrofit2/Retrofit.Builder.html#baseUrl(okhttp3.HttpUrl)
internal const val BASE_URL = "https://api.example.com/v2/"

internal const val API_LABEL = """https://api.example.com // v2"""

/**
 * Retrofit service for the checkout endpoints.
 */
interface CheckoutApi {

    /**
     * Fetches the quote.
     */
    @GET("checkout/quotes/{cartId}")
    suspend fun quote(@Path("cartId") cartId: String): QuoteDto

    // TODO(https://github.com/example/shop-android/issues/412): send an Idempotency-Key header so
    //  a retried POST can't place the same order twice.
    /**
     * Places an order for the cart in [request] and returns it as the server stored it.
     */
    @POST("checkout/orders")
    suspend fun placeOrder(@Body request: OrderRequest): OrderDto

    // @GET("checkout/orders/{orderId}")
    // suspend fun order(@Path("orderId") orderId: String): OrderDto

    /** Builds the [CheckoutApi]. */
    companion object {

        /** Creates the service on the app's shared OkHttp client. */
        fun create(): CheckoutApi = Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(HttpClients.shared)
            .addConverterFactory(MoshiConverterFactory.create())
            .build()
            .create(CheckoutApi::class.java)
    }
}

/** Body of POST checkout/orders. */
data class OrderRequest(
    val cartId: String,
    val amount: Long, // amount in euros
    val currency: String,
)

/** The price breakdown the server quotes for a cart, in minor units. */
data class QuoteDto(
    val subtotalCents: Long,
    val shippingCents: Long,
    val taxCents: Long,
    val totalCents: Long,
)

/** An order as the server stored it. */
data class OrderDto(
    val id: String,
    val status: String,
    val totalCents: Long,
)
