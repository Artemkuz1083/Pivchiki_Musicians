package metrics

import (
	"context"
	"log"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

type MetricsWorker struct {
	pool     *pgxpool.Pool
	interval time.Duration
}

func NewMetricsWorker(pool *pgxpool.Pool, interval time.Duration) *MetricsWorker {
	return &MetricsWorker{
		pool:     pool,
		interval: interval,
	}
}

func (w *MetricsWorker) Run(ctx context.Context) {
	ticker := time.NewTicker(w.interval)
	defer ticker.Stop()

	log.Println("[METRICS_WORKER] Started")

	for {
		select {
		case <-ticker.C:
			w.updateVisibleProfiles(ctx)
		case <-ctx.Done():
			log.Println("[METRICS_WORKER] Stopped")
			return
		}
	}
}

func (w *MetricsWorker) updateVisibleProfiles(ctx context.Context) {
	var count int
	err := w.pool.QueryRow(ctx, "SELECT COUNT(*) FROM users WHERE is_visible = true").Scan(&count)
	if err != nil {
		log.Printf("[METRICS_WORKER:ERROR] failed to count visible profiles: %v", err)
		return
	}
	VisibleProfilesCount.Set(float64(count))
}