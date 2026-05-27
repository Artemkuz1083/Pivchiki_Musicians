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

	RegistrationStarted = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "app_registration_started_total", Help: "Количество начатых регистраций"}, []string{"source"})

	RegistrationSuccess = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "app_registration_success_total", Help: "Количество успешно завершённых регистраций"}, []string{"source"})

	RegistrationUsername = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "app_registration_username", Help: "Количество дошедших до введения имени"}, []string{"source"})

	RegistrationCity = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "app_registration_city", Help: "Количество дошедших до введения города"}, []string{"source"})

	RegistrationInstrument = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "app_registration_instrument", Help: "Количество дошедших до введения инструмента"}, []string{"source"})

	RegistrationInstrumentRating = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "app_registration_instrument_rating", Help: "Количество дошедших до знаний об инструменте"}, []string{"source"})

	RegistrationGenre = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "app_registration_genre", Help: "Количество дошедших до жанров"}, []string{"source"})

	RegistrationContacts = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "app_registration_contacts", Help: "Количество дошедших до контактов"}, []string{"source"})

	RegistrationErrors = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "app_registration_errors_total", Help: "Количество ошибок при регистрации"}, []string{"source", "step"})

	RegistrationDuration = promauto.NewHistogramVec(prometheus.HistogramOpts{
		Name: "app_registration_duration_seconds", Help: "Время прохождения регистрации"}, []string{"source"})

	RegistrationStepDuration = promauto.NewHistogramVec(prometheus.HistogramOpts{
		Name: "registration_step_duration_seconds", Help: "Время на каждом шаге"}, []string{"source", "step"})
)
