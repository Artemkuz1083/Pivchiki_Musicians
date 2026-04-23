package delivery

import (
	"net/http"

	_ "github.com/katrinani/pivchiki-bot/backend/docs"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	httpSwagger "github.com/swaggo/http-swagger"
)

func ProfileRouter(handler *ProfileHandler) http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("GET /", handler.GetProfile)
	mux.HandleFunc("PATCH /", handler.UpdateProfile)
	mux.HandleFunc("POST /", handler.CreateProfile)

	return mux
}

func PostProfileRouter(handler *ProfileHandler) http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("GET /feed", handler.GetFeed)
	mux.HandleFunc("POST /feed/{id}/swipe", handler.Swipe)
	mux.HandleFunc("POST /media", handler.UploadMedia)

	return mux
}

func AuthRouter(handler *AuthHandler) http.Handler {
	mux := http.NewServeMux()

	mux.HandleFunc("POST /login", handler.Login)
	mux.HandleFunc("POST /registry", handler.Registry)

	return mux
}

func PublicRouter(handler *ProfileHandler) http.Handler {
    mux := http.NewServeMux()
    mux.HandleFunc("GET /feed", handler.GetPublicFeed)
    return mux
}

func NewAppRouter(profileHandler *ProfileHandler, authHandler *AuthHandler) http.Handler {
    apiMux := http.NewServeMux()

	apiMux.Handle("/api/v1/public/", http.StripPrefix("/api/v1/public", PublicRouter(profileHandler)))
    
    apiMux.Handle("/api/v1/profile", AuthMiddleWare(ProfileRouter(profileHandler)))
    apiMux.Handle("/api/v1/profile/", http.StripPrefix("/api/v1/profile", AuthMiddleWare(PostProfileRouter(profileHandler))))
    apiMux.Handle("/api/v1/auth/", http.StripPrefix("/api/v1/auth", AuthRouter(authHandler)))

    mainMux := http.NewServeMux()

	fs := http.FileServer(http.Dir("uploads"))
    mainMux.Handle("/uploads/", http.StripPrefix("/uploads/", fs))

    mainMux.Handle("/swagger/", httpSwagger.WrapHandler)
    mainMux.Handle("/metrics", promhttp.Handler())
    mainMux.Handle("/api/v1/", MetricsMiddleware(apiMux))

    return mainMux
}
