package utils

import (
	"os"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

var (
	jwtSecret    = []byte(os.Getenv("JWT_SECRET"))
	jwtAlgorithm = os.Getenv("JWT_ALGORITHM")
)

func CreateAccessToken(userID uint64) (string, error) {
	claims := jwt.MapClaims{
		"user_id":  userID,
		"exp":      time.Now().Add(time.Hour * 1).Unix(),
		"iat":      time.Now().Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	tokenString, err := token.SignedString(jwtSecret)
	if err != nil {
		return "", err
	}

	return tokenString, nil
}
