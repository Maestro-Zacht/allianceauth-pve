import { useTranslation } from "react-i18next";
import { Form } from "react-bootstrap";
import { useEntryProcessor } from "../../../providers/EntryFormProvider";
import type { SiteScaling } from "../EntryTypes";

interface SiteScalingSectionProps {
    siteScaling: SiteScaling;
}

export default function SiteScalingSection({ siteScaling }: SiteScalingSectionProps) {
    const { t } = useTranslation();
    const { updateEntryData } = useEntryProcessor();

    return <>
        <div className="text-center">
            <h5>{t("site_scaling")}</h5>
        </div>
        <Form.Select
            value={siteScaling}
            onChange={(e) => updateEntryData({ type: 'select_site_scaling', siteScaling: e.target.value as SiteScaling })}
        >
            <option value="flat">{t("site_scaling_flat")}</option>
            <option value="fabricator">{t("site_scaling_fabricator")}</option>
        </Form.Select>
    </>
}
