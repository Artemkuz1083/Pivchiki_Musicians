package delivery

import (
	"context"
	"encoding/json"
	"net/http"
	"os"

	"github.com/golang-jwt/jwt"
)

var (
	secret = os.Getenv("JWT_SECRET")
)

type ErrorMsg struct {
	Message string `json:"message"`
}

func JSONError(w http.ResponseWriter, err ErrorMsg, code int) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.WriteHeader(code)
	json.NewEncoder(w).Encode(err)
}

func renderJSON(w http.ResponseWriter, code int, data interface{}) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.WriteHeader(code)
	json.NewEncoder(w).Encode(data)
}

func AuthMiddleWare(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		authHeader := r.Header.Get("Authorization")
		tokenString := authHeader

		if len(authHeader) > 7 && authHeader[:7] == "Bearer " {
            tokenString = authHeader[7:]
        }

		if tokenString == "" {
            tokenString = r.URL.Query().Get("token")
        }

        if tokenString == "" {
            msg := ErrorMsg{Message: "У тебя нет токена"}
            JSONError(w, msg, http.StatusUnauthorized)
            return
        }

		token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
			return []byte(secret), nil
		})
		if err != nil || !token.Valid {
			msg := ErrorMsg{Message: "У тебя неверный токен"}
			JSONError(w, msg, http.StatusUnauthorized)
			return
		}

		if claims, ok := token.Claims.(jwt.MapClaims); ok {
			userID := uint64(claims["user_id"].(float64))
			ctx := context.WithValue(r.Context(), "user_id", userID)
			next.ServeHTTP(w, r.WithContext(ctx))
		} else {
			JSONError(w, ErrorMsg{Message: "Не удалось прочитать данные из токена"}, http.StatusUnauthorized)
			return
		}
	})
}
