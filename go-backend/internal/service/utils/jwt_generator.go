package utils

import (
	"errors"
	"os"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

var (
	jwtSecret    = []byte(os.Getenv("JWT_SECRET"))
	jwtAlgorithm = os.Getenv("JWT_ALGORITHM") // на случай, если используешь динамический выбор метода
)

func CreateAccessToken(userID uint64) (string, error) {
	claims := jwt.MapClaims{
		"user_id": userID,
		"exp":     time.Now().Add(time.Hour * 1).Unix(),
		"iat":     time.Now().Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(jwtSecret)
}

func CreateRefreshToken(userID uint64) (string, error) {
	claims := jwt.MapClaims{
		"user_id": userID,
		"exp":     time.Now().Add(time.Hour * 24 * 30).Unix(),
		"iat":     time.Now().Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(jwtSecret)
}

func ParseRefreshToken(tokenString string) (uint64, error) {
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, errors.New("unexpected signing method")
		}
		return jwtSecret, nil
	})

	if err != nil {
		return 0, err
	}

	if ok := token.Valid; ok && token.Valid {
		mapClaims, ok := token.Claims.(jwt.MapClaims)
		if !ok {
			return 0, errors.New("invalid claims type")
		}

		userIDFloat, ok := mapClaims["user_id"].(float64)
		if !ok {
			return 0, errors.New("user_id not found in token")
		}

		return uint64(userIDFloat), nil
	}

	return 0, errors.New("invalid token")
}