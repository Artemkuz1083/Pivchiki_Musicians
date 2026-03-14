package delivery

import "github.com/katrinani/pivchiki-bot/backend/internal/domain"

type UpdateProfile struct {
	UserName             *string                       `json:"userName,omitempty"`
	City                 *string                       `json:"city,omitempty"`
	Contact              *string                       `json:"contact,omitempty"`
	PerformancExperience *domain.PerformanceExperience `json:"performanceExperience,omitempty"`
	Link                 *string                       `json:"link,omitempty"`
	AboutUser            *string                       `json:"aboutUser,omitempty"`
	Age                  *uint                         `json:"age,omitempty"`
	ProficiencyLevel     *uint                         `json:"proficiencyLevel,omitempty"`
	TheoryLevel          *uint                         `json:"theoryLevel,omitempty"`
	Genres               *[]string                     `json:"genres,omitempty"`
	Instruments          *[]*UpdateInstrument          `json:"instruments,omitempty"`
	IsVisible            *bool                         `json:"isVisible,omitempty"`
}

type UpdateInstrument struct {
	Instrument                 *string `json:"instrument,omitempty"`
	InstrumentProficiencyLevel *uint   `json:"instrumentProficiencyLevel,omitempty"`
}
