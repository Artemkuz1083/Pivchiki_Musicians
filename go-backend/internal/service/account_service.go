package service

import (
	"errors"

	"github.com/katrinani/pivchiki-bot/backend/internal/domain"
	"github.com/katrinani/pivchiki-bot/backend/internal/repository"
	"github.com/katrinani/pivchiki-bot/backend/internal/service/utils"
	"golang.org/x/crypto/bcrypt"
)

type AccountService interface {
	Registry(account *domain.Account) (string, string, error)
    Login(account *domain.Account) (string, string, bool, error)
    RefreshTokens(oldRefreshToken string) (string, string, error)
}

var _ AccountService = (*AccountServiceImpl)(nil)

type AccountServiceImpl struct {
	repo repository.AccountRepository
}

func NewAccountService(repo repository.AccountRepository) *AccountServiceImpl {
	return &AccountServiceImpl{repo: repo}
}

func (s *AccountServiceImpl) Registry(acc *domain.Account) (string, string, error) {
    hashedPassword, err := bcrypt.GenerateFromPassword([]byte(acc.PasswordHash), bcrypt.DefaultCost)
    if err != nil {
        return "", "", err
    }
    acc.PasswordHash = string(hashedPassword)

    id, err := s.repo.CreateAccount(acc)
    if err != nil {
        return "", "", err
    }

    accessToken, err := utils.CreateAccessToken(uint64(id))
    if err != nil {
        return "", "", err
    }

    refreshToken, err := utils.CreateRefreshToken(uint64(id))
    if err != nil {
        return "", "", err
    }

    return accessToken, refreshToken, nil
}

func (s *AccountServiceImpl) Login(account *domain.Account) (string, string, bool, error) {
    acc, err := s.repo.GetAccountByLogin(account.Login)
    if err != nil {
        return "", "", false, err
    }

    err = bcrypt.CompareHashAndPassword([]byte(acc.PasswordHash), []byte(account.PasswordHash))
    if err != nil {
        return "", "", false, err
    }

    accessToken, err := utils.CreateAccessToken(uint64(acc.ID))
    if err != nil {
        return "", "", false, err
    }

    refreshToken, err := utils.CreateRefreshToken(uint64(acc.ID))
    if err != nil {
        return "", "", false, err
    }

    hasProfile, err := s.repo.CheckProfileExists(int64(acc.ID))
    if err != nil {
        return "", "", false, err
    }

    return accessToken, refreshToken, hasProfile, nil
}

func (s *AccountServiceImpl) RefreshTokens(oldRefreshToken string) (string, string, error) {
	userID, err := utils.ParseRefreshToken(oldRefreshToken)
	if err != nil {
		return "", "", errors.New("invalid or expired refresh token")
	}

	newAccessToken, err := utils.CreateAccessToken(userID)
	if err != nil {
		return "", "", err
	}

	newRefreshToken, err := utils.CreateRefreshToken(userID)
	if err != nil {
		return "", "", err
	}

	return newAccessToken, newRefreshToken, nil
}