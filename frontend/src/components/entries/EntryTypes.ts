import type { components } from "../../api/Schema";

type EntryFormSchema = components["schemas"]["EntryFormSchema"];

type ExtendedShareItem = EntryFormSchema['shares'][number] & {
    isPresent: boolean;
};

export type ExtendedEntryFormSchema = Omit<EntryFormSchema, 'shares'> & {
    shares: ExtendedShareItem[];
};