package com.example.shop.net

import java.util.concurrent.TimeUnit
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor

/** The OkHttp client every API in the app shares, so they share one connection pool. */
object HttpClients {

    private const val TIMEOUT_SECONDS = 15L

    /** The shared client, with timeouts sized for mobile networks. */
    val shared: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .connectTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .readTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .addInterceptor(HttpLoggingInterceptor().setLevel(HttpLoggingInterceptor.Level.BASIC))
            .build()
    }
}
