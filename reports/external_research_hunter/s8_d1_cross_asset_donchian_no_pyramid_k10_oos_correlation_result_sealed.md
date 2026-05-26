# s8-D1 No-Pyramid - K10 OOS Correlation Result (SEALED, side product of P9.5a audit)

**K10 OOS seal:** `ccb3609b42f92e61bd3940a74c25ffc2a813f8c09bbd16d3527b3aa07268c3f0`
**Predecessor (P9 OOS-S1) seal:** `dedd8003381a8b9ae01e9432cacefdccda49f658a909b7bb8fcda9f2cda60c4f`
**Companion (P9.5a audit) seal:** `9d65511f83553de01d333814347e514d9ea19d0f6aabac0a2f6af26bd3df1c04`
**In-sample K10 (reference) seal:** `221e759e09cc70b22e7a7d8001e30190e2dc1388506c1f330850f447303e3443`

### avg_pairwise_correlation OOS: **0.051590253717225566**
### K10 OOS threshold (> 0.50): **PASS**

### In-sample vs OOS comparison

- In-sample avg_pairwise_correlation: 0.065030
- OOS avg_pairwise_correlation:       0.051590253717225566
- delta:                              -0.013439746282774438
- regime_shift_observed (|delta| > 0.10): False

### Per-pair correlations OOS

| pair | n_common_days | pearson_r |
|---|---|---|
| NQ-GC | 666 | 0.057167 |
| NQ-ZN | 758 | -0.017233 |
| NQ-CL | 759 | 0.107979 |
| GC-ZN | 679 | 0.223576 |
| GC-CL | 679 | 0.137653 |
| ZN-CL | 771 | -0.199600 |

*End of K10 OOS correlation result (side product of P9.5a audit).*
