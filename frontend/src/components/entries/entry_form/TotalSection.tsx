import { Button, Col, Form, Row } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { parseLocalizedNumber } from "../../../utils";
import { useEntryProcessor } from "../../../providers/EntryFormProvider";
import TooltipComponent from "../../TooltipComponent";
import type { EntryFormErrors } from "../EntryTypes";

interface TotalSectionProps {
    estimatedTotal: number;
    errors: EntryFormErrors["estimated_total"] | null | undefined;
}

export default function TotalSection({ estimatedTotal, errors }: TotalSectionProps) {
    const { t, i18n } = useTranslation();
    const { updateEntryData } = useEntryProcessor();

    const localizeNumber = (num: number) => {
        return num.toLocaleString(i18n.language, { maximumFractionDigits: 0 });
    }

    return <>
        <Form.Group as={Row} className="mb-3" controlId="estimatedTotal">
            <Form.Label column sm={2}>
                {t("total")}
            </Form.Label>
            <Col sm={6} className="position-relative">
                <Form.Control
                    type="text" placeholder={t("total")}
                    value={localizeNumber(estimatedTotal)}
                    isInvalid={!!errors}
                    onChange={(e) => {
                        const newTotal = parseLocalizedNumber(e.target.value, i18n.language);
                        if (e.target.value === '') {
                            updateEntryData({ type: 'update_estimated_total', estimated_total: 0 });
                        }
                        else if (!isNaN(newTotal) && newTotal >= 0) {
                            updateEntryData({ type: 'update_estimated_total', estimated_total: newTotal });
                        }
                    }}
                />
                {errors && <Form.Control.Feedback type="invalid" tooltip>
                    {errors.map((error, index) => <div key={`error-${index}`}>{error}</div>)}
                </Form.Control.Feedback>}
            </Col>
            <Col sm={4} className="d-flex justify-content-between align-items-center">
                <TooltipComponent id="increment-all-tooltip" text={t("increment_all_shares")}>
                    <Button
                        size="sm" variant="success"
                        onClick={() => updateEntryData({ type: 'update_shares', onlyPresent: false, increment: 1 })}
                    >
                        <i className="fas fa-user-plus"></i>
                    </Button>
                </TooltipComponent>
                <TooltipComponent id="increment-selected-tooltip" text={t("increment_selected_shares")}>
                    <Button
                        size="sm" variant="info"
                        onClick={() => updateEntryData({ type: 'update_shares', onlyPresent: true, increment: 1 })}
                    >
                        <i className="fas fa-user-cog"></i>
                    </Button>
                </TooltipComponent>
                <TooltipComponent id="decrement-selected-tooltip" text={t("decrement_selected_shares")}>
                    <Button
                        size="sm" variant="warning"
                        onClick={() => updateEntryData({ type: 'update_shares', onlyPresent: true, increment: -1 })}
                    >
                        <i className="fas fa-user-cog"></i>
                    </Button>
                </TooltipComponent>
                <TooltipComponent id="decrement-all-tooltip" text={t("decrement_all_shares")}>
                    <Button
                        size="sm" variant="danger"
                        onClick={() => updateEntryData({ type: 'update_shares', onlyPresent: false, increment: -1 })}
                    >
                        <i className="fas fa-user-minus"></i>
                    </Button>
                </TooltipComponent>
            </Col>
        </Form.Group>
    </>
}
