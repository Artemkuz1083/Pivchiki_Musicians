
export interface UpdateProfileDto {
  UserName?: string;
  AboutUser?: string;
  Age?: number;
  City?: string;
  Contact?: string;
  Genres?: string[];
  Instruments?: {
    Instrument: string;
    InstrumentProficiencyLevel: number;
  }[];
  IsVisible?: boolean;
  Link?: string;
  PerformancExperience?: 'NEVER' | 'LOCAL_GIGS' | 'TOURS' | 'PROFESSIONAL';
  TheoryLevel?: number;
}
