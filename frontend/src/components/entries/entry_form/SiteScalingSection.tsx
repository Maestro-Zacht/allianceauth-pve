import { useTranslation } from "react-i18next";
import { Alert, Form } from "react-bootstrap";
import TooltipComponent from "../../utils/TooltipComponent";
import { useEntryProcessor } from "../../../providers/EntryFormProvider";
import type { SiteScaling } from "../EntryTypes";

interface SiteScalingSectionProps {
    siteScaling: SiteScaling;
    siteScalingCoefficient: number | null;
    errorsSiteScalingCoefficient: string[] | null | undefined;
}

export default function SiteScalingSection({ siteScaling, siteScalingCoefficient, errorsSiteScalingCoefficient }: SiteScalingSectionProps) {
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
        {siteScaling === 'fabricator' && <Form.Group className="d-flex align-items-center gap-3 mt-3">
            <Form.Label className="mb-0 text-nowrap">{t("site_scaling_coefficient")}</Form.Label>
            <TooltipComponent id="site-scaling-coefficient-tooltip" text={t("site_scaling_coefficient_tooltip")}>
                <Form.Control
                    type="number" min={1} step={1}
                    value={siteScalingCoefficient || ""}
                    onChange={(e) => {
                        if (e.target.value !== "") {
                            updateEntryData({ type: 'update_site_scaling_coefficient', coefficient: parseInt(e.target.value) });
                        }
                    }}
                />
            </TooltipComponent>
        </Form.Group>}
        {errorsSiteScalingCoefficient && errorsSiteScalingCoefficient.length > 0 && <Alert variant="danger" className="mt-2" dismissible>
            {errorsSiteScalingCoefficient.map((error, index) => <div key={index}>{error}</div>)}
        </Alert>}
    </>
}
