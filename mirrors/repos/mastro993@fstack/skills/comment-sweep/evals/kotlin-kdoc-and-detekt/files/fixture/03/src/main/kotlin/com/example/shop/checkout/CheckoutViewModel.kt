package com.example.shop.checkout

import androidx.lifecycle.LiveData
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.shop.cart.Cart
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/** What the checkout screen shows. */
sealed interface CheckoutUiState {

    /** The cart and its quote are loading. */
    data object Loading : CheckoutUiState

    /** The cart is quoted and ready to pay; [placing] is true while the order is in flight. */
    data class Ready(val cart: Cart, val quote: QuoteDto, val placing: Boolean = false) : CheckoutUiState

    /** The order went through. */
    data class Placed(val order: OrderDto) : CheckoutUiState

    /** Loading or ordering failed; [message] is shown to the user. */
    data class Failed(val message: String) : CheckoutUiState
}

/**
 * Drives the checkout screen: loads the cart and its quote, then places the order once the
 * payment sheet reports a successful charge.
 */
class CheckoutViewModel(
    private val repository: CheckoutRepository,
    private val savedStateHandle: SavedStateHandle,
) : ViewModel() {

    // ===================== State =====================

    // refactored to use StateFlow as discussed
    private val _state = MutableStateFlow<CheckoutUiState>(CheckoutUiState.Loading)

    /** The current screen state. */
    val state: StateFlow<CheckoutUiState> = _state.asStateFlow()

    /** The id of the last successful payment; the legacy OrderFragment host observes it. */
    val paymentId: LiveData<String?> = savedStateHandle.getLiveData(KEY_PAYMENT_ID)

    /* Old LiveData version, kept for reference:
    private val _uiState = MutableLiveData<CheckoutUiState>(CheckoutUiState.Loading)
    /* val uiState: LiveData<CheckoutUiState> = _uiState */
    fun reload(cartId: String) {
        _uiState.value = CheckoutUiState.Loading
        load(cartId)
    }
    */

    // ===================== Actions =====================

    /** Loads the cart with [cartId] and its quote. */
    fun load(cartId: String) {
        viewModelScope.launch {
            val cart = repository.getCart(cartId)
            if (cart == null || cart.items.isEmpty()) {
                // update the state
                _state.value = CheckoutUiState.Failed("Your cart is empty")
                return@launch
            }
            _state.value = try {
                CheckoutUiState.Ready(cart, repository.quote(cart))
            } catch (e: CheckoutException) {
                CheckoutUiState.Failed(e.message ?: "Could not load your total")
            }
        }
    }

    /**
     * Applies the result the payment sheet returned, and places the order when the charge went
     * through.
     *
     * Must be called on the main thread: [paymentId] is a SavedStateHandle LiveData, so writing
     * its key calls LiveData.setValue, which throws on any other thread.
     */
    fun onPaymentResult(result: PaymentResult) {
        val paymentId = result.paymentId
        if (result.cancelled || paymentId == null) return
        val ready = _state.value as? CheckoutUiState.Ready ?: return

        savedStateHandle[KEY_PAYMENT_ID] = paymentId
        // update the state
        _state.value = ready.copy(placing = true)
        viewModelScope.launch {
            _state.value = try {
                CheckoutUiState.Placed(repository.placeOrder(ready.cart))
            } catch (e: CheckoutException) {
                CheckoutUiState.Failed(e.message ?: "Checkout failed")
            }
        }
    }

    private companion object {
        const val KEY_PAYMENT_ID = "payment_id"
    }
}
