This document is to document the manner of which the probabilities are being calculated. 


## The Problem

```js
// Hypothetical current approach, e.g.:
let distance = Math.abs(teamMmr - averageNeeded);
let mmrWeight = 1 / distance; // Or something that grows excessively as distance -> 0
```

Right now, this produces very large values when the distance is near zero. In practice, players whose MMR is very close to your target “averageNeeded” get heavily favored, sometimes far beyond what we want.


Our code is:

```python
diff = abs(pmmr - ideal_mmr)
w = 1.0 / (diff + 1.0)
final_w = w * factor
```
It causes the problem of
- If diff is very small, you get w near 1.0 (or sometimes larger in ratio than you’d like).
- As diff grows even moderately, it drops fairly quickly.



## The Solution

We can try using a sigmoid solution that smoothly transitions between low and high values. A logistic function would be what we're aiming for. 

```js
// A sample logistic weight for MMR difference:
function mmrSigmoidWeight(distance, center, steepness) {
    // center ~ the distance at which your weight hits about 0.5
    // steepness ~ how quickly it transitions
    return 1 / (1 + Math.exp(steepness * (distance - center)));
    // We inverse the weight because we want the lower distance to yield higher weight
}
```
Therefore:
    When distance is less than center, we get a weight > 0.5.
    When distance is greater than center, we get a weight < 0.5.


But we then run into the problem where the weight needs to be maximum (1) at distance=0. To deal with this, we probably need to clamp the values. 


## Implementation


1. MMR-difference weighting – Replace the current 1.0/(diff+1.0) with a smoother “sigmoid” (or other gentle) function so that:

- Players extremely close to the ideal MMR do not get an absurdly high boost.
- Players very far from the ideal MMR do not drop to near zero too aggressively.
- The difference in the “middle” still matters, but is gently scaled.
- Role preference weighting – Make it more configurable so that you can:

    - Adjust how much a 1st/2nd/3rd preference factor should matter (instead of the hard-coded 0.9, 0.6, 0.1).
    - Decide how much role preference factors into the final probability relative to MMR proximity.