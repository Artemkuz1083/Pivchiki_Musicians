// Соответствие LevelOfSeriousness

export type LevelOfSeriousness = 'HOBBY' | 'SEMI_PROFESSIONAL' | 'PROFESSIONAL';
// Соответствие FinancialStatus

export type FinancialStatus = 'POOR' | 'READY_TO_INVEST' | 'LIMITED_BUDGET';

export interface GroupMember {
	UserID: number; // В Go это ProfileID (uint64)
	Name: string;
	Role: string;
}

export interface FullGroupProfile {
	ID: number;
	GroupName: string;
	City: string;
	YearOfCreation: number;
	Genres: string[];
	Platforms: string[];
	Members: GroupMember[];
	IsVisible: boolean;
	LevelOfSerious: LevelOfSeriousness;
	FinancialStatus: FinancialStatus;
	// Опциональные поля (те, что в Go с '*')
	Link?: string;
	PhotoURL?: string;
	AudioPath?: string;
	AboutGroup?: string;
	Concerts?: Record<string, string>; // В Go map[int]string, в JSON ключи всегда строки
}
