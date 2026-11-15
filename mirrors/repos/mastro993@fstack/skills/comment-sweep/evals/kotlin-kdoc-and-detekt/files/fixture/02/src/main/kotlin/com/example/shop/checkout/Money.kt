package com.example.shop.checkout

import java.text.NumberFormat
import java.util.Currency
import java.util.Locale

/**
 * Formats [amountCents], an amount in minor units of [currencyCode], for display in [locale]:
 * 1999 in EUR is "€19.99" in Locale.US. Assumes the currency has two decimal places.
 */
@Suppress("MagicNumber")
fun formatMoney(amountCents: Long, currencyCode: String, locale: Locale = Locale.getDefault()): String {
    val format = NumberFormat.getCurrencyInstance(locale)
    format.currency = Currency.getInstance(currencyCode)
    return format.format(amountCents / 100.0)
}
