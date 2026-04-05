import type { ExtendedEntryFormSchema } from "../EntryTypes";

interface SharesSectionProps {
    shares: ExtendedEntryFormSchema['shares'];
}

export default function SharesSection({ shares }: SharesSectionProps) {

    return <>
        shares: {shares.length}
    </>
}
