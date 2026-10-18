import type { components } from "../../api/Schema";

export type EntryFormSchema = components["schemas"]["EntryFormSchema"];

type ExtendedServerEntryFormSchema = components["schemas"]["ExtendedEntryFormSchema"];
export type ExtendedEntryItem = ExtendedServerEntryFormSchema['items'][number];

export type SiteRange = components["schemas"]["SiteRangeSchema"];

export type EditableSiteRange = { first: number | null; last: number | null };

export type ExtendedShareItem = ExtendedServerEntryFormSchema['shares'][number] & {
    active_sites: EditableSiteRange | null;
};

export type ExtendedEntryFormSchema = Omit<EntryFormSchema, 'shares' | 'items'> & {
    shares: ExtendedShareItem[];
    items: ExtendedEntryItem[];
};

export type SiteScaling = components["schemas"]["SiteScaling"];

export type EntryFormErrors = components["schemas"]["EntryFormErrorsSchema"];
