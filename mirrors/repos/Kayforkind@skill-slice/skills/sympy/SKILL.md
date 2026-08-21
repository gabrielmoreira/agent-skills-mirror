---
name: sympy
version: 1.1.1
description: "Computes exact SymPy results: assumed symbols, solve/solveset/dsolve, calculus, symbolic matrices, lambdify, and LaTeX or C/Fortran codegen. Use when the user needs closed-form algebra instead of floats. Not for NumPy/SciPy heavy numerics or Monte Carlo integration."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-14
license: https://github.com/sympy/sympy/blob/master/LICENSE
metadata:
  skill-author: K-Dense Inc.
---

# SymPy — Symbolic Mathematics in Python

## When to Use

Use this skill when the user needs **exact symbolic results** rather than numerical approximations, or when working with mathematical formulas that contain variables and parameters. Specific triggers:

- Solving equations symbolically (algebraic, differential, systems of equations)
- Performing calculus operations (derivatives, integrals, limits, series expansions)
- Manipulating and simplifying algebraic expressions
- Working with matrices and linear algebra symbolically
- Physics calculations (classical mechanics, quantum mechanics, vector analysis)
- Number theory computations (primes, factorization, modular arithmetic)
- Geometric calculations (2D/3D analytic geometry)
- Converting mathematical expressions to executable code (Python, C, Fortran)
- Generating LaTeX or other formatted mathematical output

### Do NOT Use

- **Purely numerical heavy-lifting** where performance is critical and symbolic representation is unnecessary — use NumPy/SciPy instead.
- **High-dimensional numerical integration** or solving massive linear systems where iterative numerical methods (LU decomposition, Monte Carlo) are required for stability and speed.
- **Complex non-linear root-finding** where `nsolve()` (numerical solver) is more appropriate than `solve()` for finding specific roots.

## Prerequisites

- Python 3.8+ installed and accessible from PowerShell
- SymPy installed: `pip install sympy`
- (Optional, for numeric pipelines) NumPy and Matplotlib: `pip install numpy matplotlib`
- (Optional, for code generation targets) SciPy: `pip install scipy`

**Verify installation (PowerShell):**

```powershell
python -c "import sympy; print(sympy.__version__)"
```

Expected output: a version string such as `1.13.x`.

## Procedure

### Step 1 — Define Symbols First (Always)

Every variable in a symbolic expression must be explicitly declared. Failure to do so raises `NameError`.

```python
from sympy import symbols, Symbol

x, y, z = symbols('x y z')
expr = x**2 + 2*x + 1
```

**With assumptions** (crucial for correct simplification):

```python
x = symbols('x', real=True, positive=True)
n = symbols('n', integer=True)
```

Common assumptions: `real`, `positive`, `negative`, `integer`, `rational`, `complex`, `even`, `odd`.

### Step 2 — Use Exact Arithmetic

Avoid floating-point literals in symbolic expressions. Use `Rational` or `S` for exact fractions.

```python
from sympy import Rational, S

# Correct (exact):
expr = Rational(1, 2) * x   # x/2
expr = S(1)/2 * x           # x/2

# Incorrect (floating-point contamination):
expr = 0.5 * x              # 0.5*x — approximate, not exact
```

### Step 3 — Simplify and Manipulate

```python
from sympy import simplify, expand, factor, cancel, trigsimp

simplify(sin(x)**2 + cos(x)**2)       # 1
expand((x + 1)**3)                     # x**3 + 3*x**2 + 3*x + 1
factor(x**2 - 1)                       # (x - 1)*(x + 1)
trigsimp(sin(x)**2 + cos(x)**2)        # 1
```

> **Load `references/core-capabilities.md`** when the user needs detailed coverage of symbols, algebra, calculus, simplification, or equation solving beyond the quick examples below.

### Step 4 — Calculus Operations

**Derivatives:**

```python
from sympy import diff
diff(x**2, x)              # 2*x
diff(x**4, x, 3)           # 24*x  (third derivative)
diff(x**2*y**3, x, y)      # 6*x*y**2  (mixed partial)
```

**Integrals:**

```python
from sympy import integrate, oo
integrate(x**2, x)                  # x**3/3  (indefinite)
integrate(x**2, (x, 0, 1))          # 1/3     (definite)
integrate(exp(-x), (x, 0, oo))      # 1       (improper)
```

**Limits and Series:**

```python
from sympy import limit, series
limit(sin(x)/x, x, 0)               # 1
series(exp(x), x, 0, 6)             # 1 + x + x**2/2 + x**3/6 + x**4/24 + x**5/120 + O(x**6)
```

### Step 5 — Solve Equations

**Single-variable algebraic:**

```python
from sympy import solveset, solve, Eq
solveset(x**2 - 4, x)       # {-2, 2}
solve(Eq(x**2, 4), x)       # [-2, 2]
```

**Systems:**

```python
from sympy import linsolve, nonlinsolve
linsolve([x + y - 2, x - y], x, y)          # {(1, 1)}
nonlinsolve([x**2 + y - 2, x + y**2 - 3], x, y)
```

**Differential equations:**

```python
from sympy import Function, dsolve, Derivative
f = symbols('f', cls=Function)
dsolve(Derivative(f(x), x) - f(x), f(x))    # Eq(f(x), C1*exp(x))
```

**Solver selection guide:**

| Solver | Use case |
|---|---|
| `solveset` | Modern single-variable equation solver; returns a set |
| `linsolve` | Linear systems |
| `nonlinsolve` | Non-linear systems |
| `dsolve` | ODEs and PDEs |
| `nsolve` | Numerical root-finding when no closed form exists |
| `solve` | General purpose; less rigorous than `solveset` |

### Step 6 — Matrices and Linear Algebra

```python
from sympy import Matrix, eye, zeros

M = Matrix([[1, 2], [3, 4]])
M_inv = M**-1          # Inverse
M.det()                # Determinant
M.T                    # Transpose

# Eigenvalues / eigenvectors
M.eigenvals()          # {eigenvalue: multiplicity}
M.eigenvects()         # [(eigenval, mult, [eigenvectors])]
P, D = M.diagonalize() # M = P*D*P^-1

# Solve Ax = b
A = Matrix([[1, 2], [3, 4]])
b = Matrix([5, 6])
sol = A.solve(b)
```

> **Load `references/matrices-linear-algebra.md`** when the user needs comprehensive linear algebra coverage: matrix decompositions, symbolic row reduction, or advanced eigenvalue problems.

### Step 7 — Physics and Mechanics

**Classical mechanics (Lagrangian):**

```python
from sympy.physics.mechanics import dynamicsymbols, LagrangesMethod
from sympy import symbols, cos

q = dynamicsymbols('q')
m, g, l = symbols('m g l')
L = m*(l*q.diff())**2/2 - m*g*l*(1 - cos(q))
LM = LagrangesMethod(L, [q])
```

**Vector analysis:**

```python
from sympy.physics.vector import ReferenceFrame, dot, cross
N = ReferenceFrame('N')
v1 = 3*N.x + 4*N.y
v2 = 1*N.x + 2*N.z
dot(v1, v2)
cross(v1, v2)
```

**Quantum mechanics:**

```python
from sympy.physics.quantum import Ket, Bra, Commutator, Operator
psi = Ket('psi')
A = Operator('A')
B = Operator('B')
comm = Commutator(A, B).doit()
```

> **Load `references/physics-mechanics.md`** when the user needs detailed physics capabilities: classical mechanics, quantum mechanics, vectors, or unit systems.

### Step 8 — Advanced Mathematics

SymPy supports: geometry (2D/3D analytic), number theory (primes, factorization, GCD/LCM, modular arithmetic, Diophantine equations), combinatorics (permutations, combinations, partitions, group theory), logic and sets, statistics (distributions, random variables, expectation, variance), special functions (Gamma, Bessel, orthogonal polynomials, hypergeometric), and polynomials (roots, factorization, Groebner bases).

> **Load `references/advanced-topics.md`** when the user needs detailed coverage of geometry, number theory, combinatorics, logic, sets, statistics, or special functions.

### Step 9 — Code Generation and Output

**Convert to fast NumPy function:**

```python
from sympy import lambdify
import numpy as np

x = symbols('x')
expr = x**2 + 2*x + 1
f = lambdify(x, expr, 'numpy')
f(np.array([1, 2, 3]))     # array([ 4,  9, 16])
```

**Generate C/Fortran code:**

```python
from sympy.utilities.codegen import codegen
[(c_name, c_code), (h_name, h_header)] = codegen(('my_func', expr), 'C')
```

**LaTeX output:**

```python
from sympy import latex
latex_str = latex(expr)
```

> **Load `references/code-generation-printing.md`** when the user needs comprehensive code generation: lambdify backends, codegen targets, LaTeX/pretty printing, or custom printing.

### Step 10 — Numerical Evaluation When Needed

Use `.evalf()` for high-precision numerical approximations from symbolic results.

```python
from sympy import pi, sqrt
result = sqrt(8) + pi
result.evalf()      # 5.96371554103586
result.evalf(50)    # 50 digits of precision
```

## Examples

### Example 1: Solve and Verify

```python
from sympy import symbols, solve, simplify

x = symbols('x')
equation = x**2 - 5*x + 6
solutions = solve(equation, x)   # [2, 3]

for sol in solutions:
    assert simplify(equation.subs(x, sol)) == 0
```

### Example 2: Symbolic-to-Numeric Pipeline

```python
from sympy import symbols, sin, cos, simplify, diff, lambdify
import numpy as np

x, y = symbols('x y')
expr = sin(x) + cos(y)
derivative = diff(expr, x)              # cos(x)
f = lambdify((x, y), derivative, 'numpy')
results = f(np.linspace(0, 1, 10), np.linspace(0, 1, 10))
```

### Example 3: Plot with Matplotlib

```python
import matplotlib.pyplot as plt
import numpy as np
from sympy import symbols, lambdify, sin

x = symbols('x')
expr = sin(x) / x
f = lambdify(x, expr, 'numpy')
x_vals = np.linspace(-10, 10, 1000)
y_vals = f(x_vals)

plt.plot(x_vals, y_vals)
plt.show()
```

### Example 4: Numerical Root-Finding with SciPy

```python
from scipy.optimize import fsolve
from sympy import symbols, lambdify

x = symbols('x')
equation = x**3 - 2*x - 5
f = lambdify(x, equation, 'numpy')
solution = fsolve(f, 2)
```

### Example 5: Matrix Eigenvalues

```python
from sympy import Matrix
M = Matrix([[1, 2], [2, 1]])
M.eigenvals()   # {3: 1, -1: 1}
```

## Pitfalls

1. **`NameError: name 'x' is not defined`** — Always define symbols using `symbols()` before use. SymPy does not auto-create symbols.

2. **Unexpected floating-point results** (e.g., `0.333333333333333` instead of `1/3`) — Caused by using `0.5` instead of `Rational(1, 2)`. Use `Rational()` or `S()` for exact arithmetic. **HARD RULE: never mix Python floats into symbolic expressions when exact results are required.**

3. **Slow performance in loops** — Using `subs()` and `evalf()` repeatedly is O(n) with high constant overhead. Use `lambdify()` to create a fast vectorized numerical function instead.

4. **`simplify` not simplifying as expected** — Try targeted functions: `factor`, `expand`, `trigsimp`, `cancel`. Add assumptions to symbols (e.g., `positive=True`). Use `simplify(expr, force=True)` for aggressive simplification, but verify the result.

5. **`sqrt(x**2)` returns `Abs(x)` instead of `x`** — This is correct behavior without assumptions. Define `x = symbols('x', positive=True, real=True)` to get `x`.

6. **`solve()` fails on complex non-linear systems** — Switch to `nsolve()` with a good initial guess for numerical root-finding. Check if a closed-form solution exists before resorting to numerical methods.

7. **`lambdify` output mismatch** — Always verify that `lambdify` outputs match the symbolic expression's numerical evaluation at a few test points before relying on the generated function.

8. **Code generation does not compile** — Check that generated C/Fortran code includes all necessary headers and that variable names are valid in the target language.

## Verification

Run these checks after performing symbolic computations:

```powershell
# 1. Verify SymPy is installed and importable
python -c "import sympy; print(sympy.__version__)"

# 2. Run a quick sanity check (quadratic solve + derivative)
python -c "from sympy import symbols, solve, diff, sin; x=symbols('x'); print(solve(x**2-5*x+6, x)); print(diff(sin(x**2), x))"
```

Expected output:
```
[2, 3]
2*x*cos(x**2)
```

```powershell
# 3. Verify lambdify produces correct numeric output
python -c "from sympy import symbols, lambdify; import numpy as np; x=symbols('x'); f=lambdify(x, x**2+2*x+1, 'numpy'); print(f(np.array([1,2,3])))"
```

Expected output:
```
[ 4  9 16]
```

Checklist:
- [ ] All examples execute without `NameError` or import errors
- [ ] Symbolic results match expected exact forms (no unexpected floats)
- [ ] `lambdify` outputs match symbolic expression's numerical evaluation at test points
- [ ] Generated C/Fortran code compiles correctly
- [ ] Assumptions on symbols are set where simplification depends on domain

## Reference Files

This skill uses modular reference files. Load them on demand:

| File | Load when... |
|---|---|
| `references/core-capabilities.md` | User needs detailed symbols, algebra, calculus, simplification, or equation solving |
| `references/matrices-linear-algebra.md` | User needs comprehensive matrix operations, decompositions, or eigenvalue problems |
| `references/physics-mechanics.md` | User needs classical mechanics, quantum mechanics, vectors, or unit systems |
| `references/advanced-topics.md` | User needs geometry, number theory, combinatorics, logic, sets, statistics, or special functions |
| `references/code-generation-printing.md` | User needs lambdify backends, codegen targets, LaTeX/pretty printing, or custom printing |

## Quick Reference: Most Common Imports

```python
# Symbols
from sympy import symbols, Symbol

# Basic operations
from sympy import simplify, expand, factor, collect, cancel
from sympy import sqrt, exp, log, sin, cos, tan, pi, E, I, oo

# Calculus
from sympy import diff, integrate, limit, series, Derivative, Integral

# Solving
from sympy import solve, solveset, linsolve, nonlinsolve, dsolve, nsolve

# Matrices
from sympy import Matrix, eye, zeros, ones, diag

# Logic and sets
from sympy import And, Or, Not, Implies, FiniteSet, Interval, Union

# Output
from sympy import latex, pprint, lambdify, init_printing, pretty

# Utilities
from sympy import evalf, N, nsimplify, S, Rational
```

## Additional Resources

- Official Documentation: https://docs.sympy.org/
- Tutorial: https://docs.sympy.org/latest/tutorials/intro-tutorial/index.html
- API Reference: https://docs.sympy.org/latest/reference/index.html
- Examples: https://github.com/sympy/sympy/tree/master/examples

## Related Skills

*No related skills are explicitly listed.*
