---
name: custom-distance-metrics
version: 1.1.1
description: "Builds two-argument sklearn metric callables and scipy cdist/pdist precomputes (weighted Euclidean/cosine, Numba Manhattan factories) for DBSCAN, HDBSCAN, AgglomerativeClustering, and NearestNeighbors. Needed when Euclidean, cosine, or Jaccard discard sequence, graph, or mixed-type structure. Do not use Lloyd K-Means with a custom metric; do not run a slow Python pairwise on large n without JIT, vectorize, or a precomputed matrix."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Custom Distance Metrics

A custom distance metric lets you define what "similar" and "different" mean for *your* data instead of accepting the assumptions baked into a generic metric. Distance is the single lever almost every unsupervised and neighbour-based algorithm pulls: clustering, manifold learning, and k-NN all make their decisions *only* through the distance function. Change the metric and you change the result, without touching the algorithm itself.

Custom metrics earn their keep in domains where off-the-shelf choices quietly misrepresent the data — bioinformatics sequences, natural-language embeddings, time series, graphs, or any mixed-type record where Euclidean geometry does not apply.

## When to Use

Reach for a custom metric when the *shape* of similarity in your problem does not match what a built-in metric measures.

1. **Algorithms that accept a `metric` argument** — DBSCAN, HDBSCAN, `AgglomerativeClustering`, `NearestNeighbors`, t-SNE, UMAP, k-NN. These algorithms route every decision through the distance function, so swapping the metric is the most direct way to change what they treat as "close."
2. **Built-in metrics misrepresent your domain.** Euclidean assumes features are comparable and independent; cosine ignores magnitude; Jaccard assumes sets. Forcing categorical data, alignment-sensitive time series, graphs, or mixed-type records through a generic metric discards exactly the structure you care about.
3. **You need to encode domain knowledge as parameters** — per-feature weights, tolerances, or scaling you want to tune. A parameterised metric lets you state "a one-day gap in timestamps matters less than a one-dollar gap in price" directly in the geometry.
4. **Genuinely non-Euclidean spaces** — angles, probability distributions, strings — where geometric distance is meaningless and a purpose-built measure (great-circle distance, KL divergence, edit distance) is the only thing that makes sense.

### When NOT to use

- **A built-in already captures your notion of similarity.** The `euclidean`, `cosine`, and `jaccard` implementations in sklearn/scipy run in compiled C and are orders of magnitude faster than a Python callable. If one fits, a custom metric only adds latency and maintenance burden.
- **Large datasets with no optimisation plan.** A pairwise computation makes O(n²) calls; a pure-Python metric crossing the interpreter boundary on every call can turn minutes into hours. At scale, vectorise, precompute the distance matrix once, or JIT-compile with Numba/Cython *before* reaching for a bespoke metric.
- **The metric breaks the math the algorithm relies on.** Many algorithms assume non-negativity, symmetry, identity of indiscernibles, and/or the triangle inequality. A function that violates them still *runs*, but can produce order-dependent, irreproducible clusters — a silent correctness bug. If you only have a similarity score, convert it to a proper distance deliberately.
- **A transform would let you keep a standard metric.** If feature scaling, PCA, or a kernel maps your data into a space where Euclidean or cosine already works, that is usually simpler and faster.
- **The algorithm hard-codes its metric.** Lloyd's-algorithm K-Means is defined around squared Euclidean distance (it relies on the arithmetic mean minimising it), so feeding it an arbitrary metric is meaningless. Use k-medoids, precomputed distances, or a kernel method instead.

## Prerequisites

- Python 3.10+ with `numpy`, `scikit-learn`, `scipy` installed.
- For accelerated metrics: `numba` (install with `pip install numba`).
- Windows PowerShell is the primary host. Use `python` (not `python3`) to run scripts.

```powershell
pip install numpy scikit-learn scipy numba
```

## Procedure

### Step 1 — Define a callable metric for sklearn

sklearn's clustering and neighbour algorithms accept either the *name* of a built-in metric or a *callable*. When you pass a callable, the algorithm invokes it with two 1-D arrays — a single pair of points — and expects one non-negative float back. It repeats this for every pair it needs, so the function must be self-contained, deterministic, and fast.

**HARD RULE:** Always scale features *before* computing distance. Distance metrics are sensitive to feature magnitudes; an unscaled feature with a large numeric range will dominate the distance regardless of any weights you choose.

**HARD RULE:** Validate inputs explicitly inside the metric. Silent wrong numbers corrupt clustering; loud errors are debuggable.

```python
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_blobs


def first_feature_weighted_distance(
    point_a: NDArray[np.float64],
    point_b: NDArray[np.float64],
) -> float:
    """Weighted Euclidean distance that emphasises the first feature.

    sklearn calls a callable ``metric`` once per pair of points, always with two
    1-D arrays, and expects a single float back. The call happens deep inside the
    algorithm, so we cannot thread extra arguments through here -- the weights are
    fixed for this particular metric.

    Args:
        point_a: First data point as a 1-D float64 array.
        point_b: Second data point as a 1-D float64 array of the same shape.

    Returns:
        The non-negative weighted Euclidean distance.

    Raises:
        TypeError: If either argument is not a NumPy array.
        ValueError: If the arrays are not 1-D, disagree in shape, or are not
            two-dimensional points (this metric is defined for 2 features).
    """
    if not isinstance(point_a, np.ndarray) or not isinstance(point_b, np.ndarray):
        raise TypeError("Both points must be numpy.ndarray instances.")
    if point_a.ndim != 1 or point_b.ndim != 1:
        raise ValueError("Both points must be 1-D arrays.")
    if point_a.shape != point_b.shape:
        raise ValueError(
            f"Points must share a shape; got {point_a.shape} and {point_b.shape}."
        )
    if point_a.shape[0] != 2:
        raise ValueError(
            f"This metric is defined for 2-feature data; got {point_a.shape[0]}."
        )

    weights: NDArray[np.float64] = np.array([2.0, 0.5], dtype=np.float64)
    diff = point_a.astype(np.float64) - point_b.astype(np.float64)
    return float(np.sqrt(np.sum(weights * diff * diff)))


def main() -> None:
    features, _ = make_blobs(
        n_samples=300, centers=4, cluster_std=0.6, random_state=42
    )
    scaled: NDArray[np.float64] = (
        StandardScaler().fit_transform(features).astype(np.float64)
    )

    db = DBSCAN(eps=0.7, min_samples=5, metric=first_feature_weighted_distance)
    labels: NDArray[np.int64] = db.fit_predict(scaled)

    n_clusters = len(set(labels.tolist())) - (1 if -1 in labels else 0)
    n_noise = int(np.sum(labels == -1))
    print(f"Clusters found: {n_clusters}")
    print(f"Noise points:   {n_noise}")
    print(f"First 10 labels: {labels[:10].tolist()}")


if __name__ == "__main__":
    main()
```

Run on Windows PowerShell:

```powershell
python custom_metric_dbscan.py
```

### Step 2 — Parameterise with a factory (closure)

To make a metric configurable, build it with a factory that "bakes in" the parameters and returns the two-argument callable sklearn expects. A factory is cleaner than a module-level global because a global makes the metric's behaviour depend on hidden state — impossible to test reliably and impossible to use in two different configurations at once.

**HARD RULE:** Validate parameters *once* inside the factory, not inside the inner function. You get a clear error at construction time instead of the same error raised on every one of millions of pairwise calls.

**HARD RULE:** Copy and freeze validated weights (`copy=True`) so later mutation of the caller's array cannot silently change the metric's behaviour.

```python
from __future__ import annotations

from typing import Callable

import numpy as np
from numpy.typing import NDArray
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_moons

DistanceFn = Callable[[NDArray[np.float64], NDArray[np.float64]], float]


def make_weighted_euclidean(feature_weights: NDArray[np.float64]) -> DistanceFn:
    """Build a weighted Euclidean metric with the weights baked in.

    Args:
        feature_weights: A 1-D array of non-negative per-feature weights. Its
            length defines how many features the returned metric expects.

    Returns:
        A two-argument callable suitable for ``sklearn``'s ``metric`` parameter.

    Raises:
        TypeError: If ``feature_weights`` is not a NumPy array.
        ValueError: If it is not 1-D, is empty, or contains a negative weight.
    """
    if not isinstance(feature_weights, np.ndarray):
        raise TypeError("feature_weights must be a numpy.ndarray.")
    if feature_weights.ndim != 1:
        raise ValueError("feature_weights must be a 1-D array.")
    if feature_weights.size == 0:
        raise ValueError("feature_weights must contain at least one weight.")
    if np.any(feature_weights < 0.0):
        raise ValueError("feature_weights must all be non-negative.")

    weights: NDArray[np.float64] = feature_weights.astype(np.float64, copy=True)
    expected_dim: int = weights.shape[0]

    def weighted_distance(
        a: NDArray[np.float64], b: NDArray[np.float64]
    ) -> float:
        if a.shape != b.shape:
            raise ValueError(
                f"Points must share a shape; got {a.shape} and {b.shape}."
            )
        if a.shape[0] != expected_dim:
            raise ValueError(
                f"Points have {a.shape[0]} features but the metric was built "
                f"for {expected_dim}."
            )
        diff = a.astype(np.float64) - b.astype(np.float64)
        return float(np.sqrt(np.sum(weights * diff * diff)))

    return weighted_distance


def main() -> None:
    features, _ = make_moons(n_samples=200, noise=0.05, random_state=42)
    scaled: NDArray[np.float64] = (
        StandardScaler().fit_transform(features).astype(np.float64)
    )

    configs: dict[str, NDArray[np.float64]] = {
        "equal":   np.array([1.0, 1.0], dtype=np.float64),
        "x-heavy": np.array([2.0, 0.5], dtype=np.float64),
        "y-heavy": np.array([0.5, 2.0], dtype=np.float64),
    }

    for name, weights in configs.items():
        metric: DistanceFn = make_weighted_euclidean(weights)
        labels: NDArray[np.int64] = DBSCAN(
            eps=0.3, min_samples=5, metric=metric
        ).fit_predict(scaled)
        n_clusters = len(set(labels.tolist())) - (1 if -1 in labels else 0)
        n_noise = int(np.sum(labels == -1))
        print(f"weights={name:<8} -> clusters={n_clusters}, noise={n_noise}")


if __name__ == "__main__":
    main()
```

### Step 3 — Accelerate with Numba for large datasets

Pure-Python metrics are slow at scale because sklearn calls them O(n²) times and each call crosses the Python/C boundary. Numba JIT-compiles the inner loop to machine code, typically recovering most of that overhead.

**HARD RULE:** Keep all *validation* in plain Python outside the compiled kernel. Numba's `nopython` mode supports only a narrow subset of Python; doing argument checks outside keeps error messages rich and the kernel tight.

**HARD RULE:** Do NOT use `cache=True` on a closure that captures a runtime value — Numba cannot cache it and will only emit a warning. The captured float is frozen into the compiled code as a constant.

**HARD RULE:** A standalone (non-closure) kernel captures nothing, so `cache=True` is safe and recommended for faster cold starts across processes.

```python
from __future__ import annotations

from typing import Callable

import numpy as np
from numpy.typing import NDArray
from numba import njit, float64
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler
from sklearn.datasets import make_circles

DistanceFn = Callable[[NDArray[np.float64], NDArray[np.float64]], float]


def make_scaled_manhattan(scale: float = 1.0) -> DistanceFn:
    """Build a Numba-JIT Manhattan metric scaled by a constant factor.

    Args:
        scale: A finite, non-negative multiplier applied to the total Manhattan
            distance. Validated here, before compilation, so a bad value fails
            immediately rather than on the first pairwise call.

    Returns:
        A Numba-compiled two-argument distance callable.

    Raises:
        TypeError: If ``scale`` is not a real number.
        ValueError: If ``scale`` is non-finite or negative.
    """
    if not isinstance(scale, (int, float)) or isinstance(scale, bool):
        raise TypeError(f"scale must be a real number, got {type(scale)!r}.")
    if not np.isfinite(scale):
        raise ValueError("scale must be finite.")
    if scale < 0.0:
        raise ValueError("scale must be non-negative.")

    scale_value: float = float(scale)

    @njit(float64(float64[:], float64[:]))
    def manhattan_scaled(a: NDArray[np.float64], b: NDArray[np.float64]) -> float:
        if a.shape[0] != b.shape[0]:
            raise ValueError("Points must have the same number of features.")
        total = 0.0
        for i in range(a.shape[0]):
            total += abs(a[i] - b[i])
        return scale_value * total

    return manhattan_scaled


@njit(float64(float64[:], float64[:]), cache=True)
def numba_euclidean(a: NDArray[np.float64], b: NDArray[np.float64]) -> float:
    total = 0.0
    for i in range(a.shape[0]):
        delta = a[i] - b[i]
        total += delta * delta
    return np.sqrt(total)


def main() -> None:
    features, _ = make_circles(
        n_samples=400, factor=0.5, noise=0.05, random_state=42
    )
    scaled: NDArray[np.float64] = (
        MinMaxScaler().fit_transform(features).astype(np.float64)
    )

    scaled_manhattan: DistanceFn = make_scaled_manhattan(scale=1.5)
    labels_manhattan: NDArray[np.int64] = DBSCAN(
        eps=0.15, min_samples=5, metric=scaled_manhattan
    ).fit_predict(scaled)
    n_manhattan = len(set(labels_manhattan.tolist())) - (
        1 if -1 in labels_manhattan else 0
    )
    print(f"scaled Manhattan -> clusters={n_manhattan}")

    labels_euclid: NDArray[np.int64] = DBSCAN(
        eps=0.10, min_samples=5, metric=numba_euclidean
    ).fit_predict(scaled)
    n_euclid = len(set(labels_euclid.tolist())) - (1 if -1 in labels_euclid else 0)
    print(f"JIT Euclidean    -> clusters={n_euclid}")


if __name__ == "__main__":
    main()
```

### Step 4 — Precompute distance matrices with scipy

`scipy.spatial.distance.cdist` (cross-distance between two sets) and `pdist` (pairwise within one set) are the right tools when an algorithm wants a *full* distance matrix. Computing the matrix once and feeding it to an algorithm as `metric="precomputed"` avoids re-running an expensive custom metric inside the algorithm's own loops.

**HARD RULE:** Always clip cosine similarity to `[-1, 1]` before computing `1 - similarity`. Floating-point error can push it outside this range, producing negative distances or distances > 2.

**HARD RULE:** Handle zero-norm vectors explicitly. A zero vector's direction is undefined; returning the maximum distance (1.0 for cosine distance) is the conventional, NaN-free choice.

```python
from __future__ import annotations

from typing import Callable

import numpy as np
from numpy.typing import NDArray
from scipy.spatial.distance import cdist, pdist, squareform
from sklearn.cluster import AgglomerativeClustering
from sklearn.datasets import make_classification

VectorMetric = Callable[[NDArray[np.float64], NDArray[np.float64]], float]

_ZERO_NORM_DISTANCE: float = 1.0


def make_weighted_cosine(feature_weights: NDArray[np.float64]) -> VectorMetric:
    """Build a weighted cosine *distance* (1 - weighted cosine similarity).

    Args:
        feature_weights: A 1-D array of non-negative per-feature weights whose
            length defines the expected vector dimension.

    Returns:
        A two-argument callable suitable for ``cdist``/``pdist``.

    Raises:
        TypeError: If ``feature_weights`` is not a NumPy array.
        ValueError: If it is not 1-D or contains a negative weight.
    """
    if not isinstance(feature_weights, np.ndarray):
        raise TypeError("feature_weights must be a numpy.ndarray.")
    if feature_weights.ndim != 1:
        raise ValueError("feature_weights must be 1-D.")
    if np.any(feature_weights < 0.0):
        raise ValueError("feature_weights must be non-negative.")

    weights: NDArray[np.float64] = feature_weights.astype(np.float64, copy=True)
    expected_dim: int = weights.shape[0]

    def weighted_cosine(
        u: NDArray[np.float64], v: NDArray[np.float64]
    ) -> float:
        if u.shape != v.shape:
            raise ValueError(
                f"Vectors must share a shape; got {u.shape} and {v.shape}."
            )
        if u.shape[0] != expected_dim:
            raise ValueError(
                f"Vectors have {u.shape[0]} features but the metric expects "
                f"{expected_dim}."
            )
        u_weighted = u.astype(np.float64) * weights
        v_weighted = v.astype(np.float64) * weights
        norm_u = float(np.linalg.norm(u_weighted))
        norm_v = float(np.linalg.norm(v_weighted))
        if norm_u == 0.0 or norm_v == 0.0:
            return _ZERO_NORM_DISTANCE
        similarity = float(np.dot(u_weighted, v_weighted) / (norm_u * norm_v))
        similarity = max(-1.0, min(1.0, similarity))
        return 1.0 - similarity

    return weighted_cosine


def main() -> None:
    features, _ = make_classification(
        n_samples=100,
        n_features=5,
        n_informative=3,
        n_redundant=0,
        random_state=42,
    )
    features = features.astype(np.float64)
    group_a: NDArray[np.float64] = features[:50]
    group_b: NDArray[np.float64] = features[50:]

    metric: VectorMetric = make_weighted_cosine(
        np.array([1.0, 1.0, 2.0, 0.5, 1.0], dtype=np.float64)
    )

    cross: NDArray[np.float64] = cdist(group_a, group_b, metric=metric)
    print(f"cdist matrix shape: {cross.shape}")
    print(f"top-left 3x3 block:\n{np.round(cross[:3, :3], 4)}\n")

    condensed: NDArray[np.float64] = pdist(group_a, metric=metric)
    print(f"pdist condensed length: {condensed.shape[0]}")
    print(f"first 10 values: {np.round(condensed[:10], 4).tolist()}\n")

    square: NDArray[np.float64] = squareform(condensed)
    print(f"squareform shape: {square.shape}")
    print(f"diagonal (should be 0): {np.round(np.diag(square)[:5], 6).tolist()}\n")

    labels: NDArray[np.int64] = AgglomerativeClustering(
        n_clusters=3, linkage="average", metric="precomputed"
    ).fit_predict(square)
    print(f"agglomerative labels (first 10): {labels[:10].tolist()}")


if __name__ == "__main__":
    main()
```

## Pitfalls

1. **Unscaled features silently dominate distance.** A feature with range 0–10000 will overwhelm a feature with range 0–1 regardless of your weights. Always run `StandardScaler` or `MinMaxScaler` before computing distances.

2. **Module-level globals for metric parameters.** A global weight array makes the metric's behaviour depend on hidden state — impossible to test reliably and impossible to use in two configurations simultaneously. Use a factory/closure instead.

3. **`cache=True` on a Numba closure capturing runtime values.** Numba cannot cache a closure that captures a runtime value; it will emit a warning and provide no benefit. Only use `cache=True` on standalone (non-closure) kernels.

4. **Cosine similarity outside `[-1, 1]`.** Floating-point error can push the dot-product ratio slightly beyond 1.0 or below -1.0, producing negative distances or distances > 2. Always clip: `similarity = max(-1.0, min(1.0, similarity))`.

5. **Zero-norm vectors produce `NaN`.** Dividing by `||u|| * ||v||` when either norm is 0 yields `NaN`, which silently propagates through the entire distance matrix. Handle it explicitly by returning the maximum distance.

6. **Violating metric axioms silently corrupts clustering.** DBSCAN and k-NN assume symmetry; several agglomerative linkages assume the triangle inequality. A metric that violates them still *runs* but can yield clusters that depend on data visitation order — a bug that is very hard to trace later.

7. **K-Means with a custom metric is meaningless.** Lloyd's algorithm is defined around squared Euclidean distance (the arithmetic mean minimises it). Feeding it an arbitrary metric produces mathematically invalid results. Use k-medoids, precomputed distances, or a kernel method instead.

8. **Pure-Python metrics at scale.** A pairwise computation makes O(n²) calls; each call crosses the Python/C boundary. At scale (n > ~1000), always vectorise, precompute the distance matrix, or JIT-compile with Numba.

## Verification

Work through this checklist before trusting a custom metric in production. Each item exists because of a concrete failure mode: a metric that passes its unit tests can still break an algorithm if it silently violates an axiom or returns `NaN`.

### Checklist

- [ ] **Functional correctness**
  - [ ] Distance from a point to itself is 0, and `d(a, b) == d(b, a)` for representative pairs.
  - [ ] The metric integrates with the target algorithm (DBSCAN, `cdist`, etc.) and produces sensible cluster counts.
  - [ ] Edge cases are handled: zero vectors, identical points, extreme values, and any special data types you support.
- [ ] **Mathematical properties (when the algorithm requires them)**
  - [ ] **Non-negativity:** `d(x, y) >= 0`.
  - [ ] **Identity of indiscernibles:** `d(x, y) == 0` if and only if `x == y`.
  - [ ] **Symmetry:** `d(x, y) == d(y, x)`.
  - [ ] **Triangle inequality:** `d(x, z) <= d(x, y) + d(y, z)`. Violating it can make DBSCAN/agglomerative results depend on visitation order.
- [ ] **Performance**
  - [ ] Benchmark against a comparable built-in with `timeit` for several dataset sizes.
  - [ ] If performance matters, benchmark the Numba version against the pure-Python one to confirm the speedup is real.
- [ ] **Robustness**
  - [ ] Input validation (array type, matching shapes, non-negative weights) rejects bad input loudly.
  - [ ] `NaN`/`inf` cannot leak out — divide-by-zero and out-of-range cosine values are handled explicitly.

### Runnable axiom verification script

Run this as part of CI whenever you change a metric. Axiom violations are invisible until an algorithm produces subtly wrong clusters.

```python
from __future__ import annotations

from typing import Callable, Sequence

import numpy as np
from numpy.typing import NDArray
from numba import njit, float64

DistanceFn = Callable[[NDArray[np.float64], NDArray[np.float64]], float]


def make_test_manhattan(scale: float = 1.0) -> DistanceFn:
    """Factory mirroring the performance example, used by the tests below.

    Args:
        scale: A non-negative multiplier on the Manhattan distance.

    Returns:
        A Numba-compiled two-argument distance callable.

    Raises:
        ValueError: If ``scale`` is negative.
    """
    if scale < 0.0:
        raise ValueError("scale must be non-negative.")
    scale_value: float = float(scale)

    @njit(float64(float64[:], float64[:]))
    def manhattan(a: NDArray[np.float64], b: NDArray[np.float64]) -> float:
        if a.shape[0] != b.shape[0]:
            raise ValueError("Points must have the same number of features.")
        total = 0.0
        for i in range(a.shape[0]):
            total += abs(a[i] - b[i])
        return scale_value * total

    return manhattan


def verify_metric_axioms(
    metric: DistanceFn,
    sample_points: Sequence[NDArray[np.float64]],
    *,
    tolerance: float = 1e-9,
) -> None:
    """Assert the four metric axioms hold across a sample of points.

    Args:
        metric: The two-argument distance callable under test.
        sample_points: At least three 1-D points of identical shape.
        tolerance: Slack allowed for floating-point error.

    Raises:
        ValueError: If fewer than three points are supplied.
        AssertionError: If any axiom is violated.
    """
    points: list[NDArray[np.float64]] = [
        np.ascontiguousarray(p, dtype=np.float64) for p in sample_points
    ]
    if len(points) < 3:
        raise ValueError("Need at least three points to test the triangle inequality.")

    for x in points:
        d_xx = float(metric(x, x))
        assert abs(d_xx) <= tolerance, f"identity failed: d(x, x) = {d_xx}, expected 0."

    for i, x in enumerate(points):
        for y in points[i + 1:]:
            d_xy = float(metric(x, y))
            d_yx = float(metric(y, x))
            assert d_xy >= -tolerance, f"non-negativity failed: d(x, y) = {d_xy}."
            assert abs(d_xy - d_yx) <= tolerance, (
                f"symmetry failed: d(x, y)={d_xy}, d(y, x)={d_yx}."
            )

    for x in points:
        for y in points:
            for z in points:
                d_xz = float(metric(x, z))
                d_xy = float(metric(x, y))
                d_yz = float(metric(y, z))
                assert d_xz <= d_xy + d_yz + tolerance, (
                    "triangle inequality failed: "
                    f"d(x,z)={d_xz} > d(x,y)+d(y,z)={d_xy + d_yz}."
                )


def main() -> None:
    metric: DistanceFn = make_test_manhattan(scale=1.5)
    rng = np.random.default_rng(seed=7)
    sample: NDArray[np.float64] = rng.standard_normal((6, 4)).astype(np.float64)

    verify_metric_axioms(metric, list(sample))
    print("All metric axioms hold for the scaled Manhattan metric.")

    origin: NDArray[np.float64] = np.zeros(4, dtype=np.float64)
    ones: NDArray[np.float64] = np.ones(4, dtype=np.float64)
    expected = 6.0
    actual = float(metric(origin, ones))
    assert abs(actual - expected) <= 1e-9, f"got {actual}, expected {expected}."
    print(f"Known-value check passed: d(0, 1) = {actual} (expected {expected}).")


if __name__ == "__main__":
    main()
```

Run on Windows PowerShell:

```powershell
python verify_metric_axioms.py
```

Expected output:

```
All metric axioms hold for the scaled Manhattan metric.
Known-value check passed: d(0, 1) = 6.0 (expected 6.0).
```

## Related skills

- `sklearn.cluster.DBSCAN`, `sklearn.cluster.AgglomerativeClustering`, `sklearn.neighbors.NearestNeighbors`
- `scipy.spatial.distance.cdist`, `scipy.spatial.distance.pdist`, `scipy.spatial.distance.squareform`
- `numpy` for efficient array operations and vectorisation
- `numba` for JIT compilation of Python functions to accelerate custom metrics
- `metric learning` techniques (e.g. LMNN, ITML) for learning an optimal distance metric from data
- `dimensionality reduction` (e.g. PCA, t-SNE, UMAP) to transform data into a space where standard metrics are more effective
- `feature engineering` to construct features that better represent the similarities you care about
