package service

import (
	"log"

	"github.com/katrinani/pivchiki-bot/backend/internal/domain"
	"github.com/katrinani/pivchiki-bot/backend/internal/repository"
)

type ProfileService interface {
	CreateUserProfile(profile *domain.FullProfile) (*domain.FullProfile, error)
	GetUserProfile(id domain.ProfileID) (*domain.FullProfile, error)
	UpdateUserProfile(profile *domain.FullProfileToUpdate) (*domain.FullProfile, error)
	GetFeedProfile(id domain.ProfileID, limit int) ([]*domain.FullProfile, error)
}

var _ ProfileService = (*ProfileServiceImpl)(nil)

type ProfileServiceImpl struct {
	repo repository.ProfileRepository
}

func NewProfileService(
	repo repository.ProfileRepository,
) *ProfileServiceImpl {
	return &ProfileServiceImpl{
		repo: repo,
	}
}

func (s *ProfileServiceImpl) GetUserProfile(id domain.ProfileID) (*domain.FullProfile, error) {
	profile, err := s.repo.GetProfile(id)
	if err != nil {
		return nil, err
	}

	return profile, nil
}

func (s *ProfileServiceImpl) UpdateUserProfile(profile *domain.FullProfileToUpdate) (*domain.FullProfile, error) {
	err := s.repo.UpdateProfile(profile)
	if err != nil {
		return nil, err
	}

	newProfile, err := s.repo.GetProfile(profile.ID)
	if err != nil {
		return nil, err
	}

	return newProfile, nil
}

func (s *ProfileServiceImpl) CreateUserProfile(profile *domain.FullProfile) (*domain.FullProfile, error) {
	log.Printf("[SERV:CreateUserProfile] Вызов Repo.CreateProfile для ID: %d", profile.ID)
	err := s.repo.CreateProfile(profile)
	if err != nil {
		log.Printf("[SERV:CreateUserProfile:ERROR] Repo.CreateProfile вернул: %v", err)
		return nil, err
	}

	p, err := s.repo.GetProfile(profile.ID)
	if err != nil {
		log.Printf("[SERV:CreateUserProfile:ERROR] ОЙ! Мы только что создали профиль %d, но GetProfile его не нашел: %v", profile.ID, err)
		return nil, err
	}

	return p, nil
}

func (s *ProfileServiceImpl) GetFeedProfile(id domain.ProfileID, limit int) ([]*domain.FullProfile, error) {
	profiles, err := s.repo.GetFeedProfiles(id, limit)
	if err != nil {
		return nil, err
	}

	if len(profiles) == 0 {
		return []*domain.FullProfile{}, nil
	}

	return profiles, nil
}
