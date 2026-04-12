import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { getRotationButtons } from "../../../api/api";
import { Button, Col, Form, Row } from "react-bootstrap";
import Loading from "../../Loading";
import TooltipComponent from "../../TooltipComponent";
import { useEntryProcessor } from "../../../providers/EntryFormProvider";
import { useState } from "react";
import { parseLocalizedNumber } from "../../../utils";

interface IncrementTotalSectionProps {
    rotationId: number
}

export default function IncrementTotalSection({ rotationId }: IncrementTotalSectionProps) {
    const { t, i18n } = useTranslation();
    const { updateEntryData } = useEntryProcessor();
    const [customIncrement, setCustomIncrement] = useState(0);
    const { isLoading, error, data } = useQuery({
        queryKey: ['rotation', rotationId, 'buttons'],
        queryFn: () => getRotationButtons(rotationId),
    });

    if (error) {
        return <div>Error loading buttons</div>
    }

    const localizeNumber = (num: number) => {
        return num.toLocaleString(i18n.language);
    }

    const buttons = data || [];

    return <>
        <Row>
            {isLoading ?
                <div className="text-center"><Loading /></div> :
                buttons.map(button => <Col key={button.id} xs={12} sm={6} lg={3} className="my-2">
                    <TooltipComponent
                        id={`increment-button-${button.id}`}
                        text={t("entry.button_tooltip", { increment: button.amount })}
                    >
                        <Button
                            variant="info" className="w-100"
                            onClick={() => updateEntryData({ type: 'increment_estimated_total', increment: button.amount })}
                        >
                            {button.text}
                        </Button>
                    </TooltipComponent>
                </Col>)
            }
        </Row>
        <Form.Group className="d-flex justify-content-between align-items-center mt-3">
            <Form.Label>{t("custom_increment")}</Form.Label>
            <Form.Control
                type="text" placeholder={t("custom_increment")}
                className="w-50"
                value={localizeNumber(customIncrement)}
                onChange={(e) => {
                    const newIncrement = parseLocalizedNumber(e.target.value, i18n.language);
                    if (e.target.value === '') {
                        setCustomIncrement(0);
                    }
                    else if (e.target.value === '-') {
                        setCustomIncrement(-0);
                    }
                    else if (!isNaN(newIncrement)) {
                        setCustomIncrement(newIncrement);
                    }
                }}
            />
            <Button
                variant="primary"
                onClick={() => {
                    updateEntryData({ type: 'increment_estimated_total', increment: customIncrement });
                }}
            >
                {t("add")}
            </Button>
        </Form.Group>
        <Form.Text className="mt-0" muted>{t("custom_increment_description")}</Form.Text>
    </>
}
