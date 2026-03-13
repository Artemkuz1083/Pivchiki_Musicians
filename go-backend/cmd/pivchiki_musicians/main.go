package main

import (
	"context"
	"log"
	"net/http"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/katrinani/pivchiki-bot/backend/internal/db"
	delivery "github.com/katrinani/pivchiki-bot/backend/internal/delivery/http"
	"github.com/katrinani/pivchiki-bot/backend/internal/repository"
	"github.com/katrinani/pivchiki-bot/backend/internal/service"
)

const postgresqlConnString = "postgres://postgres:parol123@db:5432/music_app"

// @title           Pivchiki API
// @version         1.0
// @description     API для музыкального сервиса "Пивчики"
// @host            localhost:8080
// @BasePath        /

// @securityDefinitions.apikey ApiKeyAuth
// @in header
// @name Authorization
// @description Введите JWT токен в формате: Bearer <ваш_токен>
func main() {
	pool, err := pgxpool.New(context.Background(), postgresqlConnString)
	if err != nil {
		log.Fatal(err)
	}
	defer pool.Close()

	queries := db.New(pool)

	repo := repository.NewInMemoryNoteRepository(queries)

	service := service.NewProfileService(repo)

	handler := delivery.NewProfileHandler(service)

	router := delivery.NewAppRouter(handler)

	log.Println("Сервер запускается на порту :8080...")
	const addr = ":8080"
	server := http.Server{
		Addr:    addr,
		Handler: router,
	}

	server.ListenAndServe()
}
