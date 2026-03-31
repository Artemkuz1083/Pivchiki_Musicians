import { UserProfile } from '../app/types';

export const MOCK_PROFILES: UserProfile[] = [
  {
    ID: 1,
    UserName: 'ALEXI LAIHO',
    AboutUser: 'Wildchild. Lead guitar and vocals in Children of Bodom. Hate Crew Deathroll! Ищу тех, кто готов играть быстро и технично.',
    Age: 41,
    City: 'Espoo',
    Contact: '@wildchild_cob',
    Genres: ['Melodic Death Metal', 'Power Metal', 'Thrash'],
    Instruments: [
      { Instrument: 'Электрогитара', InstrumentProficiencyLevel: 5 },
      { Instrument: 'Вокал', InstrumentProficiencyLevel: 4 }
    ],
    IsVisible: true,
    Link: 'https://www.cobhc.com',
    PerformancExperience: 'PROFESSIONAL',
    TheoryLevel: 5
  },
  {
    ID: 2,
    UserName: 'JAMES HETFIELD',
    AboutUser: 'I am the table. Metallica rhythm guitar and growls. Люблю кастомные ESP и быстрый даунстрок.',
    Age: 60,
    City: 'Los Angeles',
    Contact: '@papa_het',
    Genres: ['Heavy Metal', 'Thrash Metal'],
    Instruments: [
      { Instrument: 'Ритм-гитара', InstrumentProficiencyLevel: 5 },
      { Instrument: 'Вокал', InstrumentProficiencyLevel: 5 }
    ],
    IsVisible: true,
    Link: 'https://www.metallica.com',
    PerformancExperience: 'PROFESSIONAL',
    TheoryLevel: 4
  },
  {
    ID: 3,
    UserName: 'JOEY JORDISON',
    AboutUser: 'Ex-Slipknot (#1). Скорость, триггеры и маски. Ищу проект, где можно выдать настоящий индастриал-метал.',
    Age: 46,
    City: 'Des Moines',
    Contact: '@joey_1',
    Genres: ['Nu-Metal', 'Alternative Metal', 'Death Metal'],
    Instruments: [
      { Instrument: 'Барабаны', InstrumentProficiencyLevel: 5 }
    ],
    IsVisible: true,
    Link: 'https://www.slipknot1.com',
    PerformancExperience: 'PROFESSIONAL',
    TheoryLevel: 3
  },
  {
    ID: 4,
    UserName: 'DAVE MUSTAINE',
    AboutUser: 'King of Thrash. Megadeth frontman. Fast riffs and political lyrics. Ищу басиста и барабанщика для трэш-метал проекта.',
    Age: 62,
    City: 'Nashville',
    Contact: '@dave_mustaine',
    Genres: ['Thrash Metal', 'Heavy Metal'],
    Instruments: [
      { Instrument: 'Электрогитара', InstrumentProficiencyLevel: 5 },
      { Instrument: 'Вокал', InstrumentProficiencyLevel: 5 }
    ],
    IsVisible: true,
    Link: 'https://www.megadeth.com',
    PerformancExperience: 'PROFESSIONAL',
    TheoryLevel: 5
  },
  {
    ID: 5,
    UserName: 'FLEA',
    AboutUser: 'Red Hot Chili Peppers bassist. Slap bass guru. Funky grooves and energetic performances.',
    Age: 61,
    City: 'Los Angeles',
    Contact: '@flea_bass',
    Genres: ['Funk Rock', 'Alternative Rock'],
    Instruments: [
      { Instrument: 'Бас-гитара', InstrumentProficiencyLevel: 5 }
    ],
    IsVisible: true,
    Link: 'https://www.redhotchilipeppers.com',
    PerformancExperience: 'PROFESSIONAL',
    TheoryLevel: 4
  },
  {
    ID: 6,
    UserName: 'AMY LEE',
    AboutUser: 'Evanescence vocalist and pianist. Gothic rock and powerful vocals. Ищу виолончелиста и барабанщика.',
    Age: 42,
    City: 'Little Rock',
    Contact: '@amylee_official',
    Genres: ['Gothic Metal', 'Alternative Rock'],
    Instruments: [
      { Instrument: 'Вокал', InstrumentProficiencyLevel: 5 },
      { Instrument: 'Фортепиано', InstrumentProficiencyLevel: 4 }
    ],
    IsVisible: true,
    Link: 'https://www.evanescence.com',
    PerformancExperience: 'PROFESSIONAL',
    TheoryLevel: 4
  },
  {
    ID: 7,
    UserName: 'MARK TREMONTI',
    AboutUser: 'Alter Bridge and Creed guitarist. Heavy riffs and melodic solos. Ищу вокалиста с сильным голосом.',
    Age: 50,
    City: 'Orlando',
    Contact: '@mark_tremonti',
    Genres: ['Post-Grunge', 'Hard Rock'],
    Instruments: [
      { Instrument: 'Электрогитара', InstrumentProficiencyLevel: 5 },
      { Instrument: 'Вокал', InstrumentProficiencyLevel: 3 }
    ],
    IsVisible: true,
    Link: 'https://www.marktremonti.com',
    PerformancExperience: 'PROFESSIONAL',
    TheoryLevel: 4
  },
  {
    ID: 8,
    UserName: 'MIKE PORTNOY',
    AboutUser: 'Ex-Dream Theater drummer. Progressive metal drumming with complex time signatures. Ищу клавишника и гитариста для прогрессивного проекта.',
    Age: 57,
    City: 'Long Beach',
    Contact: '@mikeportnoy',
    Genres: ['Progressive Metal', 'Hard Rock'],
    Instruments: [
      { Instrument: 'Барабаны', InstrumentProficiencyLevel: 5 }
    ],
    IsVisible: true,
    Link: 'https://www.mikeportnoy.com',
    PerformancExperience: 'PROFESSIONAL',
    TheoryLevel: 5
  },
  {
    ID: 9,
    UserName: 'TARJA TURUNEN',
    AboutUser: 'Ex-Nightwish vocalist. Operatic soprano and symphonic metal queen. Ищу композитора для нового материала.',
    Age: 46,
    City: 'Kitee',
    Contact: '@tarjaofficial',
    Genres: ['Symphonic Metal', 'Classical Crossover'],
    Instruments: [
      { Instrument: 'Вокал', InstrumentProficiencyLevel: 5 }
    ],
    IsVisible: true,
    Link: 'https://www.tarjaturunen.com',
    PerformancExperience: 'PROFESSIONAL',
    TheoryLevel: 5
  },
  {
    ID: 10,
    UserName: 'SLASH',
    AboutUser: 'Guns N\' Roses lead guitarist. Top hat, Les Paul, and iconic blues-rock solos. Ищу хард-рок вокалиста.',
    Age: 58,
    City: 'Los Angeles',
    Contact: '@slash',
    Genres: ['Hard Rock', 'Blues Rock'],
    Instruments: [
      { Instrument: 'Электрогитара', InstrumentProficiencyLevel: 5 }
    ],
    IsVisible: true,
    Link: 'https://www.slashonline.com',
    PerformancExperience: 'PROFESSIONAL',
    TheoryLevel: 4
  }
];