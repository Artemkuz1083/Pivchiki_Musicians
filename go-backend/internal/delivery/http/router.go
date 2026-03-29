package delivery

import (
	"net/http"

	_ "github.com/katrinani/pivchiki-bot/backend/docs"
	httpSwagger "github.com/swaggo/http-swagger"
)

func ProfileRouter(handler *ProfileHandler) http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("GET /", handler.GetProfile)
	mux.HandleFunc("PATCH /", handler.UpdateProfile)
	mux.HandleFunc("POST /", handler.CreateProfile)

	return mux
}

func FeedRouter(handler *ProfileHandler) http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("GET /feed", handler.GetFeed)

	return mux
}

func AuthRouter(handler *AuthHandler) http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("POST /login", handler.Login)
	mux.HandleFunc("POST /registry", handler.Registry)

	return mux
}

func NewAppRouter(profileHandler *ProfileHandler, authHandler *AuthHandler) http.Handler {
	mux := http.NewServeMux()

	mux.Handle("/swagger/", httpSwagger.WrapHandler)
	
	mux.Handle("/api/v1/profile", AuthMiddleWare(ProfileRouter(profileHandler)))

	mux.Handle("/api/v1/profile/", http.StripPrefix("/api/v1/profile", AuthMiddleWare(FeedRouter(profileHandler))))
	mux.Handle("/api/v1/auth/", http.StripPrefix("/api/v1/auth", AuthRouter(authHandler)))

	return mux
}