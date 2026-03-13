package delivery

import (
	"net/http"
	_ "github.com/katrinani/pivchiki-bot/backend/docs"
	httpSwagger "github.com/swaggo/http-swagger"
)

func NewProfileRouter(handler *ProfileHandler) http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("GET /", handler.GetProfile)
	// mux.HandleFunc("PATCH /", handler.UpdateProfile)
	// mux.HandleFunc("DELETE /", handler.DeleteProfile)

	return mux
}

func NewAppRouter(profileHandler *ProfileHandler) http.Handler {
	mux := http.NewServeMux()

	mux.Handle("/swagger/", httpSwagger.WrapHandler)

	mux.Handle("/api/v1/profile", AuthMiddleWare(NewProfileRouter(profileHandler)))

	return mux
}
