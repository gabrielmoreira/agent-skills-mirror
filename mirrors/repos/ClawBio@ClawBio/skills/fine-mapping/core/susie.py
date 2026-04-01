"""
susie.py — Pure-Python SuSiE (Sum of Single Effects) fine-mapping.

Implements the Iterative Bayesian Stepwise Selection (IBSS) algorithm from:
    Wang et al. (2020) JRSS-B doi:10.1111/rssb.12388

This is a pure-numpy implementation that requires no R or external SuSiE
package. It matches the core algorithm but omits some advanced features
(e.g. SuSiE-inf, intercept estimation).
"""

from __future__ import annotations

import numpy as np
from .abf import _log_abf, DEFAULT_W


def run_susie(
    z: np.ndarray,
    R: np.ndarray,
    n: int,
    L: int = 10,
    w: float = DEFAULT_W,
    max_iter: int = 100,
    tol: float = 1e-3,
    min_purity: float = 0.5,
) -> dict:
    """Run SuSiE fine-mapping.

    Parameters
    ----------
    z : (p,) z-score vector
    R : (p, p) LD correlation matrix
    n : effective sample size
    L : maximum number of causal signals
    w : prior variance on each single effect (Wakefield W)
    max_iter : maximum IBSS iterations
    tol : ELBO convergence tolerance
    min_purity : minimum average pairwise |r| within a credible set

    Returns
    -------
    dict with keys:
        alpha   : (L, p) posterior weight matrix (each row sums to 1)
        mu      : (L, p) posterior mean effect sizes
        mu2     : (L, p) posterior second moments
        pip     : (p,) posterior inclusion probabilities
        elbo    : list of ELBO values per iteration
        converged : bool
        n_iter  : int
    """
    p = len(z)
    z = z.astype(float)
    R = R.astype(float)

    # Variance of z-scores ≈ 1/n (used to derive V_i = 1/n for all variants)
    V = np.full(p, 1.0 / n)

    # Initialise
    alpha = np.ones((L, p)) / p       # posterior weights (uniform init)
    mu    = np.zeros((L, p))           # posterior means
    mu2   = np.zeros((L, p))           # posterior second moments

    elbo_history = []
    converged = False

    for iteration in range(max_iter):
        alpha_prev = alpha.copy()

        # Precompute total fitted effect for residual updates
        fitted_all = (alpha * mu).sum(axis=0)  # (p,)

        for l in range(L):
            # Residual z-score: remove all other effects from z
            # r_l = z - R @ sum_{l' != l} alpha_{l'} * mu_{l'}
            other = fitted_all - alpha[l] * mu[l]  # shape (p,)
            r_l = z - R @ other  # shape (p,)

            # Single-effect regression: compute log ABF for each variant
            # treating r_l as observed z-score with variance V
            log_bf = _log_abf(r_l, V, w)

            # Posterior weights for this effect
            log_bf_shifted = log_bf - np.max(log_bf)
            alpha[l] = np.exp(log_bf_shifted) / np.exp(log_bf_shifted).sum()

            # Posterior mean and second moment (Gaussian single-effect)
            # mu_l_j  = w / (V_j + w) * r_l_j    (scalar approximation per variant)
            # For the mixture: mu[l] = sum_j alpha[l,j] * mu_j^posterior
            post_mean_j = (w / (V + w)) * r_l          # posterior mean per variant
            post_var_j  = w * V / (V + w)              # posterior variance per variant

            mu[l]  = alpha[l] * post_mean_j            # weighted by alpha
            mu2[l] = alpha[l] * (post_mean_j**2 + post_var_j)

            # Keep fitted_all in sync for the next effect's residual
            fitted_all = (alpha * mu).sum(axis=0)

        # ELBO (approximate): use KL between current and previous alpha
        elbo = _compute_elbo(z, R, alpha, mu, mu2, V, w)
        elbo_history.append(elbo)

        if iteration > 0 and abs(elbo_history[-1] - elbo_history[-2]) < tol:
            converged = True
            break

    # Compute PIPs: PIP_i = 1 - prod_l (1 - alpha_{l,i})
    pip = 1.0 - np.prod(1.0 - alpha, axis=0)
    pip = np.clip(pip, 0.0, 1.0)

    return {
        "alpha": alpha,
        "mu": mu,
        "mu2": mu2,
        "pip": pip,
        "elbo": elbo_history,
        "converged": converged,
        "n_iter": iteration + 1,
    }


def _compute_elbo(
    z: np.ndarray,
    R: np.ndarray,
    alpha: np.ndarray,
    mu: np.ndarray,
    mu2: np.ndarray,
    V: np.ndarray,
    w: float,
) -> float:
    """Approximate ELBO for convergence monitoring.

    Uses the expected log-likelihood minus KL divergence.
    This is a simplified scalar approximation sufficient for convergence checks.
    """
    L, p = alpha.shape
    n = 1.0 / V[0]  # approximate

    # Expected fitted values
    fitted = (alpha * mu).sum(axis=0)  # (p,)
    residual = z - R @ fitted
    ell = -0.5 * n * float(residual @ residual)

    # KL: sum_l sum_j alpha[l,j] * (log alpha[l,j] - log(1/p))
    with np.errstate(divide="ignore", invalid="ignore"):
        log_alpha = np.where(alpha > 0, np.log(alpha), 0.0)
    kl = float(np.sum(alpha * (log_alpha - np.log(1.0 / p))))

    return ell - kl
