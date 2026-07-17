# Real-Options Lattice — Plain-Math Derivation

The runtime implements a two-stage compound real-options model. The model is used
to value a "growth option" that an organisation has on a technology investment.

## 1. Stage 1: Single-Period Binomial (Cox-Ross-Rubinstein)

`
dt    = T1 / n1
u_1   = exp(sigma_1 * sqrt(dt))
d_1   = 1 / u_1
p_1   = (exp(r * dt) - d_1) / (u_1 - d_1)
S_u   = S0 * u_1
S_d   = S0 * d_1
V_u   = max(S_u - K1, 0)
V_d   = max(S_d - K1, 0)
V_1   = exp(-r * dt) * (p_1 * V_u + (1 - p_1) * V_d)
`

The "up" state represents the upside scenario where the asset value grows by u_1
and the "down" state represents the downside. The risk-neutral probability p_1
ensures the model is arbitrage-free.

## 2. Stage 2: Compound Option

The Stage-2 spot price is the Stage-1 value plus a learning delta:

`
learning_delta = 10.0 * (1 - 0.6 * deception_score)
S0_2           = V_1 + learning_delta
`

deception_score comes from the Deception Scanner. A high deception score reduces
the learning delta — an organisation that signals deception learns less between
Stage 1 and Stage 2.

Stage 2 then applies the same binomial formula with K2, T2, sigma_2 and 
2.

## 3. Total Compound Value

`
V_total = V_1 + V_2
threshold = (K1 + K2) * 0.85
decision  = "GO"  if V_total > threshold
            "DEFER" otherwise
`

## 4. Volatility Adjustments

The runtime clamps the deception-adjusted volatility to [0.05, 0.95] and the
entropy-adjusted volatility to [0.05, 0.90]. This prevents pathological inputs
from producing nonsensical valuations.

## 5. Audit Determinism

The lattice uses no random number generator. The same inputs always produce the
same output. This is required for the audit trail to be reproducible.
