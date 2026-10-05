# WeatherNext 3: Increasing Resolution and Performance of Global Weather Models with Raw Observations

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/google/technical-reports/weathernext-3-technical-report--arxiv-v1.pdf) · [Official source](https://arxiv.org/abs/2609.03582)

## Architecture · Figure 1

Source page: 2 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/google/technical-reports/weathernext-3-technical-report--arxiv-v1.pdf#page=2)

![Architecture](figure-01.png)

Figure 1 | Model overview. Schematic showing the different input and output modalities, and
spatiotemporal resolutions of WeatherNext 3 (WN3). WN3 takes two sources of input: (a) two analysis
frames (6 hours apart), with an operational latency of 5 hours, and (b) the 12 most recent geostationary
satellite mosaic frames, which are available every hour and the most recent of which has an operational
latency of just under 1 hour. Analysis inputs are 0.1◦resolution for a subset of key atmospheric variables
and surface variables, and 0.25◦for other variables. WN3 predicts precipitation, surface variables
and some atmospheric variables at hourly temporal resolution, with the remaining variables predicted
in 6 hour timesteps. WN3’s station output head predicts 2m temperature and 2m relative humidity
at arbitrary spatial and temporal resolution (i.e. is continuously query-able in space and time). WN3
also produces off-grid sparse or tabular cyclone predictions at 6-hourly temporal resolution.

## Results · Figure 2

Source page: 11 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/google/technical-reports/weathernext-3-technical-report--arxiv-v1.pdf#page=11)

![Results](figure-02.png)

Figure 2 | Analysis results. (a) Upper-level CRPS scorecard comparing WN3 to the previous state-
of-the-art model WN2 at 0.25◦. Blue squares indicate improvement. (b) Single-level variable CRPS
scorecard of WN2 vs WN3 evaluated at 0.1◦. WN2 forecasts were interpolated bilinearly. (c) Scorecard
of variables not in WN2 against ECMWF ENS at 0.1◦. The ground truth for (a), (b) and (c) is HRES-fc0.
All scores computed for 00/12 UTC initializations in 2024.
