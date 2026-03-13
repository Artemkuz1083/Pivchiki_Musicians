package domain

import (
	"errors"
)

type ProfileID uint64

type PerformanceExperience string

const (
	ExpNever        PerformanceExperience = "NEVER"
	ExpLocalGigs    PerformanceExperience = "LOCAL_GIGS"
	ExpTours        PerformanceExperience = "TOURS"
	ExpProfessional PerformanceExperience = "PROFESSIONAL"
)

// TODO: сделать аудио фото таймстап добавить плюс логики
type FullProfile struct {
	ID                   ProfileID
	UserName             string
	City                 string
	Contact              string
	PerformancExperience *string
	Link                 *string
	AboutUser            *string
	Age                  *uint
	ProficiencyLevel     *uint
	TheoryLevel          *uint
	Genres               []string
	Instruments          []*Instrument
	IsVisible            bool
}

type Instrument struct {
	Instrument                 string
	InstrumentProficiencyLevel uint
}

// type FullUpdatedProfile struct {
// 	ID      ProfileID
// 	Title   *string
// 	Content *string
// }

var ErrNoteNotFound = errors.New("your profile is not found")
