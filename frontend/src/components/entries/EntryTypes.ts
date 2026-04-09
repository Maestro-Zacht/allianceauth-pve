import type { components } from "../../api/Schema";

export type EntryFormSchema = components["schemas"]["EntryFormSchema"];
type ExtendedServerEntryFormSchema = components["schemas"]["ExtendedEntryFormSchema"];

export type ExtendedShareItem = ExtendedServerEntryFormSchema['shares'][number] & {
    is_present: boolean;
};

export type ExtendedEntryFormSchema = Omit<EntryFormSchema, 'shares'> & {
    shares: ExtendedShareItem[];
};

export type EntryFormErrors = components["schemas"]["EntryFormErrorsSchema"];