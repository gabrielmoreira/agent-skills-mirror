# Research Brief: Mandelbrot Set Escape Dynamics

## 1. Problem Statement
Determine whether a given complex parameter $c \in \mathbb{C}$ lies inside the Mandelbrot Set $\mathcal{M}$ up to a bounded iteration horizon $N_{\max} \ge 1$ by iterating the monic complex quadratic polynomial $f_c(z) = z^2 + c$ from the critical point $z_0 = 0$ and detecting divergence via the exact escape-radius theorem $|z_n| > 2$.

## 2. Candidate Comparison Table

| Algorithm / Method | Canonical Literature Citation | Verified Link / Reference | Governing Mathematical Formulation | Complexity & Constraints | Trade-offs & Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Direct Escape-Time Iteration** | Mandelbrot (1982); Douady & Hubbard (1984) | `https://doi.org/10.1119/1.13295` / `https://en.wikipedia.org/wiki/Mandelbrot_set` | $\displaystyle z_{n+1} = z_n^2 + c,\; z_0 = 0,\; |z_n| > 2$ | Time: $O(N_{\max})$, Space: $O(1)$<br>Constraints: $N_{\max} \ge 1$ | Exact escape threshold $R=2$; simple, deterministic IEEE-754 double-precision realization. |
| **Cardioid & Period-2 Bulb Pre-Check + Escape Loop** | Douady & Hubbard (1984) | *Étude dynamique des polynômes complexes*, Orsay (1984) | $\displaystyle q\left(q + (x - \tfrac{1}{4})\right) \le \tfrac{1}{4} y^2$ | Time: $O(1)$ interior / $O(N_{\max})$ boundary | Accelerates interior points analytically while delegating exterior points to the escape loop. |
| **Perturbation Theory / Arbitrary-Precision Orbit** | Martin (2013); Douady & Hubbard (1984) | `https://en.wikipedia.org/wiki/Plotting_algorithms_for_the_Mandelbrot_set` | $\displaystyle \Delta_{n+1} = 2 Z_n \Delta_n + \Delta_n^2 + \delta c$ | Time: $O(N_{\max})$ amortized | Needed only for ultra-deep zooms ($< 10^{-14}$) beyond IEEE-754 `float64`. |

## 3. Detailed Candidate Breakdown

### 1. Direct Escape-Time Iteration (Escape Radius $R = 2$)
* **Canonical Literature Reference:**
  - Benoit B. Mandelbrot, *The Fractal Geometry of Nature*, W. H. Freeman and Company, 1982, Chapter 3 (`https://doi.org/10.1119/1.13295`).
  - Adrien Douady and John H. Hubbard, *Étude dynamique des polynômes complexes*, Prépublications mathématiques d'Orsay, 1984–1985 (proving the escape-radius criterion $|z_n| > 2 \implies |z_k| \to \infty$).
* **Governing Mathematical Formulation:**
  $$\displaystyle z_0 = 0, \qquad z_{n+1} = z_n^2 + c, \qquad c \notin \mathcal{M} \iff \exists\, n \ge 1 \text{ such that } |z_n| > 2$$
* **Core Computational Mechanism:** Initialize $z \leftarrow 0 + 0i$ and iterate $z \leftarrow z^2 + c$ for $n = 1, \dots, N_{\max}$. Terminate early returning `(False, n)` as soon as $|z| > 2.0$; otherwise return `(True, N_{\max})`.
* **Preconditions & Domain Invariants:** $c \in \mathbb{C}$, $N_{\max} \in \mathbb{Z}_{\ge 1}$, conjugate reflection symmetry $f_{\bar{c}}(\bar{z}) = \overline{f_c(z)}$, and boundedness of $c = 0$ for all $N_{\max}$.

## 4. Recommended Approach & Justification
* **Primary Recommendation:** Direct Escape-Time Iteration with Escape Radius $R = 2$.
* **Technical Justification:** Satisfies standard double-precision (`complex128`) membership and escape-step queries cleanly with exact algebraic symmetry and exterior escape postconditions (`OBL-1`–`OBL-3`).
* **Pre-Manifest Handoff Readiness:** Governing recurrence (`SPEC-1`), Douady–Hubbard escape criterion (`SPEC-2`), and canonical citations are verified for Stage 1 extraction into `manifest.json`.
