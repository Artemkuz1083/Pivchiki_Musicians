package domain

import (
	"errors"
)

type ProfileID uint64

// @Description Уровень опыта выступлений
// @Enum NEVER, LOCAL_GIGS, TOURS, PROFESSIONAL
type PerformanceExperience string

const (
	expNever        PerformanceExperience = "NEVER"
	expLocalGigs    PerformanceExperience = "LOCAL_GIGS"
	expTours        PerformanceExperience = "TOURS"
	expProfessional PerformanceExperience = "PROFESSIONAL"
)

func (e PerformanceExperience) IsValid() bool {
	switch e {
	case expNever, expLocalGigs, expTours, expProfessional:
		return true
	}
	return false
}

// TODO: сделать фото и аудио логику мб клиент или другую хуйню
type FullProfile struct {
	ID                   ProfileID
	UserName             string
	City                 string
	Contact              string
	PerformancExperience *PerformanceExperience
	Link                 *string
	AboutUser            *string
	PhotoURL             *string
	AudioURL             *string
	Age                  *uint
	TheoryLevel          *uint
	Genres               []string
	Instruments          []*Instrument
	IsVisible            bool
}

type Instrument struct {
	Instrument                 string
	InstrumentProficiencyLevel uint
}

type FullProfileToUpdate struct {
	ID                   ProfileID
	UserName             *string
	City                 *string
	Contact              *string
	PerformancExperience *PerformanceExperience
	Link                 *string
	AboutUser            *string
	PhotoPath            *string
	AudioPath            *string
	Age                  *uint
	TheoryLevel          *uint
	Genres               *[]string
	Instruments          *[]*UpdateInstrument
	IsVisible            *bool
}

type UpdateInstrument struct {
	Instrument                 *string
	InstrumentProficiencyLevel *uint
}

type SwipeResult struct {
    IsMatch bool `json:"is_match"`
}

type ProfileFilters struct {
    Cities          []string
    Genres          []string
    Instruments     []string
    ProficiencyLevel *uint
    HasExperience   *string
    TheoryLevel      *uint
}

var ErrNoteNotFound = errors.New("your profile is not found")
