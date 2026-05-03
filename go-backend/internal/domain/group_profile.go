package domain

type GroupID uint64

// @Description Уровень серьезности группы
// @Enum NEVER, LOCAL_GIGS, TOURS, PROFESSIONAL
type LevelOfSeriousness string

const (
	Hobby            LevelOfSeriousness = "HOBBY"
	SemiProfessional LevelOfSeriousness = "SEMI_PROFESSIONAL"
	Professional     LevelOfSeriousness = "PROFESSIONAL"
)

func (e LevelOfSeriousness) IsValid() bool {
	switch e {
	case Hobby, SemiProfessional, Professional:
		return true
	}
	return false
}

type FinancialStatus string

const (
	FinancialPoor          FinancialStatus = "POOR"
	FinancialReadyToInvest FinancialStatus = "READY_TO_INVEST"
	FinancialLimitedBudget FinancialStatus = "LIMITED_BUDGET"
)

func (e FinancialStatus) IsValid() bool {
	switch e {
	case FinancialPoor, FinancialReadyToInvest, FinancialLimitedBudget:
		return true
	}
	return false
}

type FullGroupProfile struct {
	ID              GroupID
	GroupName       string
	City            string
	Link            *string
	PhotoURL        *string
	AudioPath       *string
	AboutGroup      *string
	YearOfCreation  uint
	Genres          []string
	Platforms       []string
	Members         []GroupMember
	Concerts        map[int]string
	IsVisible       bool
	LevelOfSerious  LevelOfSeriousness
	FinancialStatus FinancialStatus
}

type FullGroupProfileToUpdate struct {
	ID              GroupID
	GroupName       *string
	City            *string
	Link            *string
	PhotoURL        *string
	AudioPath       *string
	AboutGroup      *string
	YearOfCreation  *uint
	Genres          *[]string
	Members         *[]GroupMember
	IsVisible       *bool
	LevelOfSerious  *LevelOfSeriousness
	FinancialStatus *FinancialStatus
	Platforms       *[]string
    // @example {"1": "Luzhniki"}
    Concerts map[string]string `json:"concerts" swaggertype:"object"`
}

type GroupMember struct {
	UserID ProfileID
	Name   string
	Role   string
}

type GroupSwipeResult struct {
	IsMatch bool `json:"is_match"`
}

type GroupProfileFilters struct {
	Cities         []string
	Genres         []string
	LevelOfSerious *LevelOfSeriousness
}
