---
name: speaker-clustering
description: "Clusters L2-normalized speaker embeddings into IDs with hierarchical cuts (unknown count) or KMeans/agglomerative when k is known, then stitches adjacent same-speaker turns. Trigger after VAD and embedding extraction while segments are still anonymous. Not a VAD or encoder stage and not a leading-silence trimmer (silence-detector)."
version: 1.1.1
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## When to Use

Reach for this skill once you have one speaker embedding per VAD segment and need to decide *which segments came from the same person*. Clustering is the step that turns a pile of anonymous vectors into "speaker 0 / speaker 1 / speaker 2" labels.

- **After embedding extraction.** Each VAD segment has been encoded into a fixed-length vector by a modern speaker encoder (e.g. an ECAPA-TDNN or WavLM-based model). Clustering operates on those vectors, not on raw audio.
- **When you need to group similar speakers.** The whole point is to collapse many segments into a small set of speaker identities.
- **When the speaker count is unknown *or* known.** The method you pick depends on this — hierarchical clustering discovers the count, KMeans and agglomerative require you to supply it. That trade-off is the core decision this skill helps you make.

## Prerequisites

- Python environment with `numpy`, `scipy`, and `scikit-learn` installed.
- Speaker embeddings extracted from VAD segments (e.g., via ECAPA-TDNN or WavLM-based model).
- Windows host is primary (PowerShell). Ensure your Python environment is activated in PowerShell before running scripts.

## Procedure

### Overview

The pipeline is always the same shape: validate and normalize embeddings once, then hand the normalized array to whichever clustering method matches what you know about the speaker count. Sharing a single, validated, normalized array across methods keeps every comparison apples-to-apples and means input bugs surface in exactly one place.

Every example below assumes the input has already passed through this helper. It is the single source of truth for validation and normalization, so the clustering functions can stay focused on clustering.

```python
import numpy as np
import numpy.typing as npt


def prepare_embeddings(
    raw_embeddings: list[list[float]] | npt.NDArray[np.floating],
) -> npt.NDArray[np.float32]:
    """Validate, convert, and L2-normalize speaker embeddings.

    Why this exists: every clustering method here uses cosine distance, which
    only behaves like a real angular metric when each vector lies on the unit
    hypersphere. Skip normalization and a vector with larger magnitude
    dominates the distance, silently degrading the clustering. We normalize
    once, here, and reuse the result everywhere so that bug can only happen in
    one place.

    Args:
        raw_embeddings: A 2-D collection of shape (n_segments, embedding_dim)
            holding one speaker embedding per VAD segment.

    Returns:
        A contiguous float32 array of shape (n_segments, embedding_dim) whose
        non-zero rows are unit length. float32 is chosen because speaker
        encoders emit float32 and downstream libraries (scipy, scikit-learn)
        run their vectorized paths fastest on it.

    Raises:
        ValueError: If the input is empty, not 2-D, or contains NaN/Inf — all
            of which indicate a broken extraction step that must be fixed
            before clustering can mean anything.
    """
    embeddings = np.asarray(raw_embeddings, dtype=np.float32)

    if embeddings.ndim != 2:
        raise ValueError(
            "Expected a 2-D array of shape (n_segments, embedding_dim), got "
            f"{embeddings.ndim}-D with shape {embeddings.shape}."
        )
    if embeddings.shape[0] == 0:
        raise ValueError("No embeddings supplied; there is nothing to cluster.")
    if not np.all(np.isfinite(embeddings)):
        raise ValueError(
            "Embeddings contain NaN or Inf; inspect the embedding-extraction "
            "step before clustering."
        )

    # Divide by max(norm, eps), not np.clip, because we only need a *lower*
    # bound to avoid divide-by-zero. A genuinely silent (all-zero) segment that
    # slipped past VAD then stays at the origin instead of exploding to Inf.
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    safe_norms = np.maximum(norms, np.float32(1e-12))
    return (embeddings / safe_norms).astype(np.float32, copy=False)
```

### Available Clustering Methods

#### 1. Hierarchical Clustering (Recommended for Auto-tuning)

**Best for:** Automatically determining the number of speakers when you have no prior count.

**Why start here:** hierarchical clustering builds a single linkage tree and lets you "cut" it at any height to get a different number of clusters. You can therefore search for a good cut without re-clustering from scratch — ideal when the speaker count is unknown. We use `'average'` linkage because speaker embeddings form roughly spherical clusters on the unit sphere: `'average'` compares the *mean* pairwise distance between groups and tolerates the occasional outlier segment that VAD boundaries produce, whereas `'single'` linkage chains through outliers and `'complete'` over-splits.

```python
import numpy as np
import numpy.typing as npt
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import pdist


def cluster_hierarchical(
    embeddings_normalized: npt.NDArray[np.float32],
    initial_threshold: float = 0.7,
    min_speakers: int = 2,
    max_speakers: int | None = None,
) -> tuple[npt.NDArray[np.int_], float, int]:
    """Group speaker embeddings without knowing the speaker count up front.

    Args:
        embeddings_normalized: Unit-length embeddings of shape
            (n_segments, embedding_dim). Run `prepare_embeddings` first.
        initial_threshold: Starting cosine-distance cut height. Modern speaker
            encoders separate distinct speakers cleanly in the 0.6-0.8 range,
            so 0.7 is a sensible default starting point.
        min_speakers: Lower bound on the returned speaker count.
        max_speakers: Upper bound on the returned speaker count. When None it
            defaults to a data-driven cap of n_segments // 2 — you cannot have
            more speakers than half your segments and still trust the split.

    Returns:
        (labels, chosen_threshold, n_speakers). `labels` holds one integer
        speaker id per segment.

    Raises:
        ValueError: If fewer than two segments are supplied or the bounds are
            inconsistent.
    """
    n_segments = int(embeddings_normalized.shape[0])
    if n_segments < 2:
        raise ValueError(
            f"Hierarchical clustering needs at least 2 segments, got {n_segments}."
        )
    if min_speakers < 1:
        raise ValueError(f"min_speakers must be >= 1, got {min_speakers}.")

    resolved_max = (
        max_speakers if max_speakers is not None else min(10, n_segments // 2)
    )
    resolved_max = max(min_speakers, resolved_max)

    # pdist returns the condensed (upper-triangular) distance vector, which is
    # exactly what linkage expects. Building it directly avoids materializing
    # the full n*n matrix and halves memory on long recordings.
    condensed_distances = pdist(embeddings_normalized, metric="cosine")
    linkage_matrix = linkage(condensed_distances, method="average")

    threshold = float(initial_threshold)
    labels = fcluster(linkage_matrix, t=threshold, criterion="distance")
    n_speakers = int(np.unique(labels).size)

    # Re-cut the *same* tree to merge over-segmented speakers (raise the cut)
    # or split under-segmented ones (lower the cut). Each re-cut is cheap
    # because the expensive linkage step already happened.
    if n_speakers > resolved_max:
        for candidate in np.linspace(threshold, 1.2, num=6):
            labels = fcluster(linkage_matrix, t=float(candidate), criterion="distance")
            n_speakers = int(np.unique(labels).size)
            if n_speakers <= resolved_max:
                threshold = float(candidate)
                break
    elif n_speakers < min_speakers:
        for candidate in np.linspace(threshold, 0.4, num=4):
            labels = fcluster(linkage_matrix, t=float(candidate), criterion="distance")
            n_speakers = int(np.unique(labels).size)
            if n_speakers >= min_speakers:
                threshold = float(candidate)
                break

    return labels.astype(np.int_, copy=False), threshold, n_speakers
```

**Advantages**
- Determines the speaker count automatically by choosing a cut height.
- The threshold is a single, interpretable knob (cosine distance), easy to tune per dataset.
- Strong default when the number of speakers is genuinely unknown.
- The linkage tree can be rendered as a dendrogram for a visual sanity check.

**Scaling note**
- The condensed distance matrix is O(n²) in memory and the linkage step is O(n²) or worse. For very large segment counts, chunk the distance computation, downsample segments, or switch to a specialized library such as `fastcluster`. There is no GPU shortcut in stock scipy, so plan capacity around the CPU cost.

#### 2. KMeans Clustering

**Best for:** A known (or tightly bounded) speaker count where speed matters.

**Why KMeans here:** it is by far the cheapest option, so when the count is constrained — a two-person interview, a panel of four — you can sweep a small range of `k` and pick the best by silhouette score in milliseconds. We score with the *same* cosine metric used implicitly by the normalized space so that model selection stays consistent with the clustering objective; selecting `k` with Euclidean silhouette while reasoning about angular separation would pick the wrong `k`.

```python
import numpy as np
import numpy.typing as npt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def cluster_kmeans(
    embeddings_normalized: npt.NDArray[np.float32],
    min_k: int = 2,
    max_k: int = 6,
    random_state: int = 0,
) -> tuple[npt.NDArray[np.int_], int, float]:
    """Cluster when you already know roughly how many speakers to expect.

    Args:
        embeddings_normalized: Unit-length embeddings of shape
            (n_segments, embedding_dim).
        min_k: Smallest speaker count to try. Must be >= 2 because silhouette
            score is undefined for a single cluster.
        max_k: Largest speaker count to try (capped internally at
            n_segments - 1, since silhouette needs at least one segment to
            remain outside each cluster).
        random_state: Seed so repeated runs are reproducible — KMeans is
            otherwise sensitive to its random initialization.

    Returns:
        (labels, best_k, best_score). If no value of k yields at least two
        populated clusters, every segment is assigned to speaker 0 and
        best_score is -1.0 to signal "no meaningful split found".

    Raises:
        ValueError: On fewer than two segments or an empty k range.
    """
    n_segments = int(embeddings_normalized.shape[0])
    if n_segments < 2:
        raise ValueError(f"KMeans needs at least 2 segments, got {n_segments}.")
    if min_k < 2:
        raise ValueError(
            f"min_k must be >= 2 (silhouette needs >= 2 clusters), got {min_k}."
        )

    upper_k = min(max_k, n_segments - 1)
    if upper_k < min_k:
        raise ValueError(
            f"k range is empty: min_k={min_k} but {n_segments} segments only "
            f"allow k up to {upper_k}."
        )

    best_k = min_k
    best_score = -1.0
    best_labels: npt.NDArray[np.int_] = np.zeros(n_segments, dtype=np.int_)

    for k in range(min_k, upper_k + 1):
        # n_init="auto" lets scikit-learn choose a sensible number of restarts,
        # which guards against KMeans settling into a poor local minimum.
        estimator = KMeans(n_clusters=k, random_state=random_state, n_init="auto")
        labels = estimator.fit_predict(embeddings_normalized)

        # silhouette_score requires 2 <= n_clusters <= n_samples - 1; a
        # degenerate fit outside that band cannot be scored, so skip it.
        unique_count = int(np.unique(labels).size)
        if not 1 < unique_count < n_segments:
            continue

        score = float(
            silhouette_score(embeddings_normalized, labels, metric="cosine")
        )
        if score > best_score:
            best_score = score
            best_k = k
            best_labels = labels.astype(np.int_, copy=False)

    return best_labels, best_k, best_score
```

**Advantages**
- Lowest latency of the three methods, which is why it is the production default when the count is known.
- Simple, well-understood, and stable across scikit-learn versions.
- Scales to large segment counts far better than the O(n²) hierarchical path.

**Disadvantages**
- Requires you to specify (or sweep) the number of clusters.
- Random initialization means results vary unless you fix `random_state`; it can also converge to a local minimum, mitigated by `n_init="auto"`.

#### 3. Agglomerative Clustering

**Best for:** A fixed number of clusters where you need fully deterministic, reproducible labels.

**Why agglomerative over KMeans:** it has no random initialization, so identical input always yields identical labels. That determinism matters in research and regression tests where you compare runs and need the speaker assignments to be stable. Because we evaluate several `n_clusters` values whose pairwise distances are identical, we precompute the cosine distance matrix once and reuse it — recomputing O(n²) distances inside the loop would be pure waste.

```python
import numpy as np
import numpy.typing as npt
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score


def cluster_agglomerative(
    embeddings_normalized: npt.NDArray[np.float32],
    min_n: int = 2,
    max_n: int = 5,
) -> tuple[npt.NDArray[np.int_], int, float]:
    """Deterministic alternative to KMeans for a fixed cluster count.

    Args:
        embeddings_normalized: Unit-length embeddings of shape
            (n_segments, embedding_dim).
        min_n: Smallest cluster count to try (>= 2).
        max_n: Largest cluster count to try (capped at n_segments - 1).

    Returns:
        (labels, best_n, best_score). Falls back to all-zeros / -1.0 when no
        configuration produces at least two populated clusters.

    Raises:
        ValueError: On fewer than two segments or an empty n range.
    """
    n_segments = int(embeddings_normalized.shape[0])
    if n_segments < 2:
        raise ValueError(
            f"Agglomerative clustering needs >= 2 segments, got {n_segments}."
        )
    if min_n < 2:
        raise ValueError(f"min_n must be >= 2, got {min_n}.")

    upper_n = min(max_n, n_segments - 1)
    if upper_n < min_n:
        raise ValueError(
            f"n_clusters range is empty: min_n={min_n} but {n_segments} "
            f"segments only allow up to {upper_n}."
        )

    # squareform turns the condensed pdist vector into the dense (n, n) matrix
    # AgglomerativeClustering needs when metric='precomputed'. Computed once,
    # reused for every candidate n_clusters below.
    distance_matrix = squareform(pdist(embeddings_normalized, metric="cosine"))

    best_n = min_n
    best_score = -1.0
    best_labels: npt.NDArray[np.int_] = np.zeros(n_segments, dtype=np.int_)

    for n_clusters in range(min_n, upper_n + 1):
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            metric="precomputed",  # consume our cosine distance matrix directly
            linkage="average",     # 'ward' is invalid with a precomputed metric
        )
        labels = clustering.fit_predict(distance_matrix)

        unique_count = int(np.unique(labels).size)
        if not 1 < unique_count < n_segments:
            continue

        # Score against the same precomputed distances so selection and
        # clustering share one metric.
        score = float(
            silhouette_score(distance_matrix, labels, metric="precomputed")
        )
        if score > best_score:
            best_score = score
            best_n = n_clusters
            best_labels = labels.astype(np.int_, copy=False)

    return best_labels, best_n, best_score
```

**Advantages**
- Deterministic: no random seed, so labels are reproducible run to run.
- Reuses one precomputed distance matrix across all candidate counts, avoiding redundant O(n²) work.
- Accepts different linkage strategies (`average`, `complete`, `single`) so you can match cluster geometry to your data.

### End-to-end example

The snippet below ties the helpers together on synthetic data so it runs with no external files. `raw_embeddings` would normally be the per-segment vectors from your encoder; here we fabricate two well-separated speakers so the result is predictable.

```python
import numpy as np

# Two segments from speaker A near the origin, one from speaker B shifted away,
# all 192-D (a typical ECAPA-TDNN embedding size). A fixed seed keeps the demo
# reproducible.
rng = np.random.default_rng(seed=42)
speaker_a = rng.normal(loc=0.0, scale=1.0, size=(2, 192))
speaker_b = rng.normal(loc=5.0, scale=1.0, size=(1, 192))
raw_embeddings = np.vstack([speaker_a, speaker_b]).astype(np.float32)

normalized = prepare_embeddings(raw_embeddings)
labels, threshold, n_speakers = cluster_hierarchical(normalized)

print(f"Detected {n_speakers} speakers at cut height {threshold:.2f}")
print(f"Per-segment labels: {labels.tolist()}")
# Expected: 2 speakers, with the two speaker-A segments sharing a label.
```

### Threshold tuning (for hierarchical cuts)

The cluster count is *monotonic* in the cut height: raising the threshold only ever merges clusters, never splits them. That monotonicity is exactly what makes binary search valid — each probe tells you which half of the range still contains the target, so you converge in a handful of steps instead of scanning a grid.

```python
import numpy as np
import numpy.typing as npt
from scipy.cluster.hierarchy import fcluster


def find_optimal_threshold(
    linkage_matrix: npt.NDArray[np.float64],
    target_speakers: int,
    low: float = 0.1,
    high: float = 2.0,
    iterations: int = 8,
) -> float:
    """Binary-search the cut height that yields `target_speakers` clusters.

    Args:
        linkage_matrix: The (n-1, 4) matrix returned by scipy `linkage`.
        target_speakers: Desired number of clusters.
        low: Lower bound of the search interval (more, tighter clusters).
        high: Upper bound of the search interval (fewer, looser clusters).
        iterations: Number of bisection steps. 8 narrows a [0.1, 2.0] range to
            within ~0.007 — finer than the metric's useful resolution.

    Returns:
        The midpoint of the final interval, used as the chosen cut height.

    Raises:
        ValueError: If the linkage matrix is malformed, the bounds are
            inverted, or the target is non-positive.
    """
    if linkage_matrix.ndim != 2 or linkage_matrix.shape[1] != 4:
        raise ValueError(
            "Expected an (n-1, 4) scipy linkage matrix, got shape "
            f"{linkage_matrix.shape}."
        )
    if target_speakers < 1:
        raise ValueError(f"target_speakers must be >= 1, got {target_speakers}.")
    if not low < high:
        raise ValueError(f"Require low < high, got low={low}, high={high}.")

    for _ in range(iterations):
        mid = (low + high) / 2.0
        n_clusters = int(
            np.unique(fcluster(linkage_matrix, t=mid, criterion="distance")).size
        )
        if n_clusters > target_speakers:
            low = mid   # too many clusters -> cut higher to merge more
        else:
            high = mid  # at or below target -> cut lower to refine
    return (low + high) / 2.0
```

### Post-Clustering: Merging Segments

Diarization emits many short segments because VAD cuts on brief pauses. Two consecutive segments from the same speaker separated by a tiny gap are almost always one turn, so we stitch them. We then drop anything still shorter than `min_duration`, because sub-300ms "turns" are usually backchannels or mislabeled noise rather than real speech.

The gap tolerance is *adaptive* on purpose. A 0.15s pause inside a long monologue clearly belongs to the same turn, but the identical gap between two short utterances may be a genuine speaker switch. Scaling the allowed gap with the current segment's length tolerates natural pauses in long turns without over-merging rapid back-and-forth dialogue.

```python
LabeledSegment = tuple[float, float, int]  # (start_seconds, end_seconds, speaker_id)


def merge_speaker_segments(
    labeled_segments: list[LabeledSegment],
    base_gap: float = 0.15,
    min_duration: float = 0.3,
) -> list[LabeledSegment]:
    """Stitch adjacent same-speaker segments and drop sub-threshold noise.

    Args:
        labeled_segments: List of (start, end, speaker_id), times in seconds.
        base_gap: Baseline silence (seconds) bridged between same-speaker
            segments before any length-based scaling is applied.
        min_duration: Minimum length (seconds) a merged segment must reach to
            survive the final filter.

    Returns:
        Time-sorted, merged, duration-filtered segments.

    Raises:
        ValueError: If any segment has a negative timestamp or end <= start,
            which would indicate corrupt upstream timing.
    """
    if not labeled_segments:
        return []

    for start, end, speaker in labeled_segments:
        if start < 0.0 or end < 0.0:
            raise ValueError(
                f"Negative timestamp in segment ({start}, {end}, {speaker})."
            )
        if end <= start:
            raise ValueError(
                f"Segment end must be after start, got ({start}, {end}, {speaker})."
            )

    # Sort by (start, end) so the single forward pass below sees segments in
    # chronological order; merging relies on that ordering.
    ordered = sorted(labeled_segments, key=lambda seg: (seg[0], seg[1]))

    merged: list[LabeledSegment] = []
    cur_start, cur_end, cur_speaker = ordered[0]

    for start, end, speaker in ordered[1:]:
        allowed_gap = base_gap + 0.1 * (cur_end - cur_start)
        same_speaker = speaker == cur_speaker
        within_gap = start <= cur_end + allowed_gap

        if same_speaker and within_gap:
            cur_end = max(cur_end, end)  # extend the currently open turn
        else:
            if (cur_end - cur_start) >= min_duration:
                merged.append((cur_start, cur_end, cur_speaker))
            cur_start, cur_end, cur_speaker = start, end, speaker

    # Flush the final open turn through the same duration filter.
    if (cur_end - cur_start) >= min_duration:
        merged.append((cur_start, cur_end, cur_speaker))

    return merged
```

## Pitfalls

- **Unnormalized embeddings with cosine distance.** Cosine distance is only a true angular metric on unit-length vectors. If magnitudes vary, a louder or longer segment can sit "closer" purely because its vector is bigger, corrupting the clusters. Always L2-normalize first (see `prepare_embeddings` above).
- **Audio that still contains non-speech.** If VAD left in music, laughter, or silence, those segments produce embeddings that do not correspond to any speaker and pull cluster centroids off target. Clean the input upstream rather than hoping clustering will ignore the noise.
- **Hard real-time, strict-latency paths.** Hierarchical clustering builds an O(n²) distance matrix and a linkage tree, so its cost grows quickly with segment count. For low-latency streaming, prefer KMeans (or an online clustering variant) and accept that you must supply or estimate the speaker count.
- **Euclidean distance on speaker embeddings.** These encoders are trained so that *angle*, not magnitude, encodes speaker identity. Euclidean distance mixes the two and degrades separation. Use cosine (or its monotonic cousin, angular distance).

## Examples

### Indicative comparison

The timings below are rough orders of magnitude on a commodity CPU and will vary with embedding dimension, segment count, and library version. Treat the *relative* ordering as the durable signal, not the absolute numbers.

| Method        | Auto speaker count | Relative speed (ms / 100 emb) | Best for              | When to default to it |
|---------------|--------------------|-------------------------------|-----------------------|-----------------------|
| Hierarchical  | Yes                | ~120 (slowest)                | Unknown speaker count | Gold standard for discovery |
| KMeans        | No                 | ~18 (fastest)                 | Known speaker count   | Production default when count is fixed |
| Agglomerative | No                 | ~85                           | Fixed, reproducible clusters | Research / regression-tested pipelines |

The takeaway: KMeans is fastest but needs the count; hierarchical is slowest but discovers the count; agglomerative trades KMeans' speed for determinism.

## Verification

- [ ] Run the end-to-end example and confirm it reports 2 speakers with the two speaker-A segments sharing a label.
- [ ] Assert embeddings are L2-normalized before clustering — for non-silent segments, `np.allclose(np.linalg.norm(normalized, axis=1), 1.0, atol=1e-5)` should hold. (All-zero rows from silent segments are the one expected exception.)
- [ ] Feed a deliberately malformed input (empty array, 1-D array, an array containing `np.nan`) to `prepare_embeddings` and confirm it raises `ValueError` rather than silently producing garbage clusters.
- [ ] For hierarchical clustering, render the dendrogram (`scipy.cluster.hierarchy.dendrogram`) and confirm the chosen cut height lands in a visually large vertical gap.
- [ ] Exercise `merge_speaker_segments` with overlapping and sub-`min_duration` segments and confirm short noise segments are dropped while long same-speaker turns are stitched.

## Related skills

- **Automatic Speech Recognition** — run Whisper (large-v3 or newer) *after* diarization so each transcript line can be attributed to a clustered speaker.
- **Voice Activity Detection (VAD)** — produces the segments you embed and then cluster; clustering quality is bounded by VAD quality.
- **Speaker Embedding Extraction** — the encoder (e.g. ECAPA-TDNN or a WavLM-based model) whose output vectors feed `prepare_embeddings`.
- **Cluster Visualization** — project embeddings to 2-D/3-D (e.g. UMAP) to eyeball whether clusters are well separated before trusting the labels.
