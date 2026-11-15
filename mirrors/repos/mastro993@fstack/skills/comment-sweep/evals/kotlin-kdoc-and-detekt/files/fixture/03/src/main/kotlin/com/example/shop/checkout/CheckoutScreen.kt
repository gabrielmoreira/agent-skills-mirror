@file:Suppress("FunctionNaming")

package com.example.shop.checkout

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.compose.foundation.layout.* // ktlint-disable no-wildcard-imports
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle

private const val COLLAPSED_LINES = 3

private const val NO_SKU = "/* no sku */"

/* ktlint-disable max-line-length */
private const val TERMS = "By placing this order you agree to the Terms of Sale and confirm that the delivery address is correct."
/* ktlint-enable max-line-length */

/**
 * The checkout screen for the cart with [cartId]: its lines, the quote, and the pay button.
 * Calls [onDone] once with the placed order.
 */
@Composable
fun CheckoutScreen(viewModel: CheckoutViewModel, cartId: String, onDone: (OrderDto) -> Unit) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    val paymentLauncher = rememberLauncherForActivityResult(PaymentSheetContract()) { result ->
        viewModel.onPaymentResult(result)
    }

    // load the cart when the screen opens
    LaunchedEffect(cartId) { viewModel.load(cartId) }

    when (val current = state) {
        // show a spinner while loading
        CheckoutUiState.Loading -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
        is CheckoutUiState.Ready -> ReadyContent(
            state = current,
            onPay = {
                paymentLauncher.launch(PaymentRequest(current.quote.totalCents, current.cart.currency))
            },
        )
        is CheckoutUiState.Placed -> LaunchedEffect(current.order.id) { onDone(current.order) }
        is CheckoutUiState.Failed -> Text(
            text = current.message,
            color = MaterialTheme.colorScheme.error,
            modifier = Modifier.padding(16.dp),
        )
    }
}

@Composable
private fun ReadyContent(state: CheckoutUiState.Ready, onPay: () -> Unit) {
    //noinspection AutoboxingStateCreation
    var visibleLines by rememberSaveable { mutableStateOf(COLLAPSED_LINES) }
    val currency = state.cart.currency

    Column(Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        // render each item
        state.cart.items.take(visibleLines).forEach { item ->
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("${item.quantity} × ${item.name} // ${item.sku.ifBlank { NO_SKU }}")
                Text(formatMoney(item.unitPriceCents * item.quantity, currency))
            }
        }
        if (state.cart.items.size > visibleLines) {
            TextButton(onClick = { visibleLines = Int.MAX_VALUE }) {
                Text("Show all ${state.cart.itemCount()} items")
            }
        }

        HorizontalDivider()
        // TotalRow("Subtotal", state.quote.subtotalCents, currency)
        TotalRow("Shipping", state.quote.shippingCents, currency)
        TotalRow("Tax", state.quote.taxCents, currency)
        TotalRow("Total", state.quote.totalCents, currency)

        Spacer(Modifier.weight(1f))
        Text(TERMS, style = MaterialTheme.typography.bodySmall)
        Button(onClick = onPay, enabled = !state.placing, modifier = Modifier.fillMaxWidth()) {
            Text(if (state.placing) "Placing order…" else "Pay ${formatMoney(state.quote.totalCents, currency)}")
        }
    }
}

@Composable
private fun TotalRow(label: String, amountCents: Long, currency: String) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label)
        Text(formatMoney(amountCents, currency))
    }
}
