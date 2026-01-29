# TODO

- check IO and CPU more carefully, see where data is missing and if there is a pattern

- investigate the time between 20.11 and 04.12
    - how did latency behave
    - how did coldstarts behave
    - did it affect all providers

- take a look at the transfer experiment 
    - take a look at the rise for cloudflare and deno half way through
    - take a look at fastly with suspicously low time

- cpu cloudflare does not seem right

- drop in constant number of colstarts for flyio end of november

- look at elasticity

## Questions trever

- mean or median?

# Findings

## Coldstarts

- strong latency but also variability differences in coldstart performance between providers
- aws deno cloudflare fastly are low and stable
- flyio has very high latency but kinda stable (in relation)
- oracle has performance all over the place especially for arm arch


## Warmstarts

- median and variance much more stable across all providers
- can kind of be split into two classes: one around 45-55ms and one around 10 ms
- 10ms: fastly, flyio, cloudflare, deno
- 50ms: oracle, aws, google

- configurations perform mostly very similar
    -  fastly has better js than go performance

- wide variance between providers in how many coldstarts there are during the warmstart experiments
    - this will affect cost
    - can also be seen when looking at number of executions per function and related latency, functions that are executed only once, have high latency since coldstarts
    - function that are executed often have lower latency
    - functions of all configurations seem to have the same number of coldstarts (proportionally to the total number over all configurations)

- google function are executed up to 50k times -> are reused most often
- aws between 0 - 600 times with a suspiciously hard cutoff (interesting outlier)
- for oracle most function are only executed once with another cluster near 1400 times
    - has a big impact on average latency since coldstarts are so slow
- cloudflare shows clusters with execution times appearing often and a spike in latency for functions that are executed ~20 times
- flyio also almost exclusively all only executed once with outlier near 25k executions
- fastly same with outlier near 320k executions


## CPU

- also shows different levels or variance for providers
    - fastly, aws, flyio are relatively stable (except fallout fly end of november)
    - google, oracle and deno have pretty high variability

- error rates are pretty constant for aws
- almost nor errors for cloudflare, deno, oracle, google, flyio
- correlated errors end of november for flyio


## IO

- pretty constant for aws and flyio little more variance for oracle
- high variance and latency for google

- alomost no errors except for aws where there is a constant error rate

## Transfer

- inverse correlation between latency in transfer and failure rates for google
    - meaning when requests take too long they are killed so the median latency goes down there
    - if they are not meadian latency goes up

- for the other providers there is explicitly no correlation 


## TODO

- coldstarts in warm per provider per configuration as boxplot
- not count for function but age in minutes
- check function id unknown
- warmstarts ove day
- general overview in beginning and then experiment based aftyer
- change points, can be done in statistics but you can also just use your eyes


# Outline

## Main observations

- No operational problems on our side 
- gathered data for 53 days, 12 gb
- two kinds of deviations from "baseline"
    - isolated events
    - general trends / differences in performance when comparing providers

- isolated events
    - latency spikes beginning of december
    - weekly patterns, daily patterns (NightShift)

- general trends
    - new kids have generally better performance caused by modern technologies in virtualization and edge distribution
    - difference between compiled and interpreted language
    - difference between architectures
    