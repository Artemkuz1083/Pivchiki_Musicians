	package service

	import (
		"github.com/katrinani/pivchiki-bot/backend/internal/domain"
		"github.com/katrinani/pivchiki-bot/backend/internal/repository"
		"github.com/katrinani/pivchiki-bot/backend/internal/service/utils"
		"golang.org/x/crypto/bcrypt"
	)

	type AccountService interface {
		Login(account *domain.Account) (string, bool, error)
		Registry(account *domain.Account) (string, error)
	}

	var _ AccountService = (*AccountServiceImpl)(nil)

	type AccountServiceImpl struct {
		repo repository.AccountRepository
	}

	func NewAccountService(
		repo repository.AccountRepository,
	) *AccountServiceImpl {
		return &AccountServiceImpl{
			repo: repo,
		}
	}

	func (s *AccountServiceImpl) Registry(acc *domain.Account) (string, error) {
		hashedPassword, err := bcrypt.GenerateFromPassword([]byte(acc.PasswordHash), bcrypt.DefaultCost)
		if err != nil {
			return "", err
		}
		acc.PasswordHash = string(hashedPassword)

		id, err := s.repo.CreateAccount(acc)
		if err != nil {
			return "", err
		}

		token, err := utils.CreateAccessToken(uint64(id))
		if err != nil {
			return "", err
		}

		return token, nil
	}

	func (s *AccountServiceImpl) Login(account *domain.Account) (string, bool, error) {
		acc, err := s.repo.GetAccountByLogin(account.Login)
		if err != nil {
			return "", false, err
		}

		err = bcrypt.CompareHashAndPassword([]byte(acc.PasswordHash), []byte(account.PasswordHash))
		if err != nil {
			return "", false, err
		}

		token, err := utils.CreateAccessToken(uint64(acc.ID))
		if err != nil {
			return "", false, err
		}

		hasProfile, err := s.repo.CheckProfileExists(int64(acc.ID))
		if err != nil {
			return "", false, err
		}

		return token, hasProfile, nil
	}
