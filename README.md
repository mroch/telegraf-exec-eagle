# telegraf-exec-eagle

A [Telegraf](https://influxdata.com/time-series-platform/telegraf/) plugin to forward data from your electricity Smart Meter to InfluxDB, via a [Rainforest Eagle](https://rainforestautomation.com/rfa-z109-eagle/) energy gateway.

The Eagle operates in two modes:

- **Push**: you run an HTTP server on your network, and configure it as the "Cloud" on your Eagle. The Eagle will push changes to you every ~8 seconds.
- **Pull**: the Eagle runs an HTTP server on your network, and you periodically query it for demand, summation and pricing data.

This project provides plugins for both modes. The **pull** plugin is likely more useful, because it logs both summation and pricing data as a single point which allows you to calculate cost.
