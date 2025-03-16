This document is to document the manner of which the probabilities are being calculated. 


## The Problem

```js
// Hypothetical current approach, e.g.:
let distance = Math.abs(teamMmr - averageNeeded);
let mmrWeight = 1 / distance; // Or something that grows excessively as distance -> 0
```

Right now, this produces very large values when the distance is near zero. In practice, players whose MMR is very close to your target “averageNeeded” get heavily favored, sometimes far beyond what we want.


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