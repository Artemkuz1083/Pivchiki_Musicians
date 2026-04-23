package delivery

import "github.com/katrinani/pivchiki-bot/backend/internal/domain"

type UpdateProfile struct {
	UserName             *string                       `json:"userName,omitempty"`
	City                 *string                       `json:"city,omitempty"`
	Contact              *string                       `json:"contact,omitempty"`
	PerformancExperience *domain.PerformanceExperience `json:"performanceExperience,omitempty"`
	Link                 *string                       `json:"link,omitempty"`
	AboutUser            *string                       `json:"aboutUser,omitempty"`
	PhotoURL             *string                       `json:"photoUrl,omitempty"`
	AudioURL             *string                       `json:"audioUrl,omitempty"`
	Age                  *uint                         `json:"age,omitempty"`
	TheoryLevel          *uint                         `json:"theoryLevel,omitempty"`
	Genres               *[]string                     `json:"genres,omitempty"`
	Instruments          *[]*UpdateInstrument          `json:"instruments,omitempty"`
	IsVisible            *bool                         `json:"isVisible,omitempty"`
}

type CreateProfile struct {
	UserName    string       `json:"userName,omitempty"`
	City        string       `json:"city,omitempty"`
	Contact     string       `json:"contact,omitempty"`
	Genres      []string     `json:"genres,omitempty"`
	Instruments []Instrument `json:"instruments,omitempty"`
	IsVisible   bool         `json:"isVisible,omitempty"`
}

type Instrument struct {
	Instrument                 string `json:"instrument,omitempty"`
	InstrumentProficiencyLevel uint   `json:"instrumentProficiencyLevel,omitempty"`
}

type UpdateInstrument struct {
	Instrument                 *string `json:"instrument,omitempty"`
	InstrumentProficiencyLevel *uint   `json:"instrumentProficiencyLevel,omitempty"`
}

type AuthRequest struct {
	Login    string `json:"login"`
	Password string `json:"password"`
}

type AuthResponse struct {
	Token            string `json:"token"`
	IsProfileCreated bool   `json:"is_profile_created"`
}
