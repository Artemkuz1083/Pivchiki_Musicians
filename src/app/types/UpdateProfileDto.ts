export interface UpdateProfileDto {
	userName?: string
	aboutUser?: string
	age?: number
	city?: string
	contact?: string
	genres?: string[]
	instruments?: {
		instrument: string
		instrumentProficiencyLevel: number
	}[]
	isVisible?: boolean
	link?: string
	performancExperience?: 'NEVER' | 'LOCAL_GIGS' | 'TOURS' | 'PROFESSIONAL'
	theoryLevel?: number
}
