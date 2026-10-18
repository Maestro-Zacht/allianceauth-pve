import type { TFunction } from "i18next";
import type { EntryFormErrors, ExtendedEntryFormSchema } from "../EntryTypes";

type SiteRangeErrors = EntryFormErrors["shares"][string]["sites"][string];

export function validateShareSites(
    shares: ExtendedEntryFormSchema["shares"],
    t: TFunction<"translation", undefined>
): EntryFormErrors | null {
    const sharesErrors: EntryFormErrors["shares"] = {};

    shares.forEach((share, index) => {
        const active = share.active_sites;
        if (active === null) {
            return;
        }

        const rangeErrors: SiteRangeErrors = { first: [], last: [] };

        if ((active.first === null) !== (active.last === null)) {
            rangeErrors.first.push(t("site_range_incomplete"));
        } else if (active.first !== null && active.last !== null && active.last < active.first) {
            rangeErrors.last.push(t("site_range_inverted"));
        } else {
            return;
        }

        sharesErrors[index] = {
            character_id: [],
            helped_setup: [],
            role_name: [],
            sites_root: [],
            sites: { [share.sites.length]: rangeErrors },
        };
    });

    if (Object.keys(sharesErrors).length === 0) {
        return null;
    }

    return {
        estimated_total: [],
        funding_project_id: [],
        funding_percentage: [],
        roles_root: [],
        roles: {},
        shares_root: [],
        shares: sharesErrors,
        items: {},
    };
}
