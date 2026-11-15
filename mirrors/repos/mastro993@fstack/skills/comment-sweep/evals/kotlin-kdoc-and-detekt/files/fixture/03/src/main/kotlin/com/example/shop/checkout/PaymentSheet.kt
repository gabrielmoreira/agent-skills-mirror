package com.example.shop.checkout

import android.app.Activity
import android.content.Context
import android.content.Intent
import androidx.activity.result.contract.ActivityResultContract

/** What the checkout screen asks the payment sheet to charge, in minor units of [currency]. */
data class PaymentRequest(val amountCents: Long, val currency: String)

/** What the payment sheet returned: a [paymentId] when the charge went through. */
data class PaymentResult(val paymentId: String?, val cancelled: Boolean)

/**
 * Launches the payment sheet activity and reads back its result.
 */
class PaymentSheetContract : ActivityResultContract<PaymentRequest, PaymentResult>() {

    override fun createIntent(context: Context, input: PaymentRequest): Intent =
        Intent(ACTION_PAY)
            .setPackage(context.packageName)
            .putExtra(EXTRA_AMOUNT_CENTS, input.amountCents)
            .putExtra(EXTRA_CURRENCY, input.currency)

    override fun parseResult(resultCode: Int, intent: Intent?): PaymentResult {
        // check the result code
        if (resultCode != Activity.RESULT_OK) return PaymentResult(paymentId = null, cancelled = true)
        return PaymentResult(paymentId = intent?.getStringExtra(EXTRA_PAYMENT_ID), cancelled = false)
    }

    private companion object {
        const val ACTION_PAY = "com.example.shop.action.PAY"
        const val EXTRA_AMOUNT_CENTS = "amount_cents"
        const val EXTRA_CURRENCY = "currency"
        const val EXTRA_PAYMENT_ID = "payment_id"
    }
}
