package metrics

import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    HttpRequestsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "Total number of HTTP requests",
		},
		[]string{"method", "endpoint", "status", "platform"},
	)

	HttpRequestDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "http_request_duration_seconds",
			Help:    "Duration of HTTP requests in seconds",
			Buckets: prometheus.DefBuckets, // стандартные интервалы от 0.005с до 10с
		},
		[]string{"method", "endpoint", "platform"},
	)

	VisibleProfilesCount = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "music_app_visible_profiles_total",
			Help: "Current number of profiles with IsVisible = true",
		},
	)
)