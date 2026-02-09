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

## Problems

- the text is already way too long, how can i shorten it best
    -  maybe combine archs
    - combine edge providers (e.g. fastly, CW, DD) into one as they behave similarly
    - find shorter ways to phrase things, maybe kick tail ratio and / or std and find a better metric to describe this


# Outline

## Main observations

- ???: What to do about differing number of measurements for each configuration-language class
- this affects the median and falsifies overall latency
- if we reduce the number of measurements to the minimum amount in one of them, which ones do we eliminate

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


## Experiments

### Warmstarts
- add to experiment design that we filtered out all coldstarts

- interesting metrics:
    - warmstart latency (how high, variant, arch, language, mem)
    - also how many coldstarts occurred might be interesting, as this has a big impact on cost
    - how old are functions -> how often are they reused
    - weekly, daily patterns

### Coldstarts
- add to experiment design that we filtered out all warmstarts and chose the execution frequency in a way that would maximize coldstarts (e.g. run it less)

- interesting metrics:
    - coldstart latency (how high, variant, arch, langiuage, mem)
    - how many coldstarts occur? (very different across providers, is it also different across configs) -> actually more relevant for before
    - weekly daily patterns
    - maybe a comparison number to warmstart speed (as in coldstart/warmstart)

### Geodis

- Basically: edge good hyperscaler no good
- obrservations:
    - hyperscalers have multimodality in violin plots
    - CW has shit cape town for some reason
    - Deno bad behavior for edge provider in comparison (deno has less and less access points)
    - for hyperscalers correlated latency make sense and advantage of edge is no correlated failures there except for deno who dont have many zones
