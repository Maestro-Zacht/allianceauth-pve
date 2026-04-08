import type { components } from "../../api/Schema";

export type EntryFormSchema = components["schemas"]["EntryFormSchema"];

export type ExtendedShareItem = EntryFormSchema['shares'][number] & {
    portraitUrl: string;
    characterName: string;
    mainCharacterName: string;
    mainCharacterPortraitUrl: string;
    isPresent: boolean;
};

export type ExtendedEntryFormSchema = Omit<EntryFormSchema, 'shares'> & {
    shares: ExtendedShareItem[];
};

export type EntryFormErrors = components["schemas"]["EntryFormErrorsSchema"];